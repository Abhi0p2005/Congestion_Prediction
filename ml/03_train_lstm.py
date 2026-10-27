"""Step 3: train an LSTM onset predictor on one experiment.

Input: last 10 bins (2.5 s) x six f_* features for one UE. Output: logit of onset 1 s ahead.
Early stopping on validation PR-AUC, where validation = whole series held out from TRAIN.

Usage:  python 03_train_lstm.py --data <folder> --exp E2 --seed 0
Quick smoke test on a subset:  add --max-train 50000
"""
import argparse
import json
import os
import time

import numpy as np
import torch
from torch import nn

from model_defs import LSTMClassifier
from common import (FEATURE_SETS, MODELS_DIR, WINDOW, best_f1_threshold, build_windows, evaluate,
                    find_datasets_dir, fmt, load_split, save_result, series_split)


@torch.no_grad()
def predict(model, X, batch=8192):
    model.eval()
    ps = [torch.sigmoid(model(torch.from_numpy(X[i:i + batch]))).numpy() for i in range(0, len(X), batch)]
    return np.concatenate(ps) if ps else np.array([])


ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--exp", default="E2")
ap.add_argument("--features", default="all", choices=list(FEATURE_SETS))
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--hidden", type=int, default=64)
ap.add_argument("--layers", type=int, default=1)
ap.add_argument("--epochs", type=int, default=20)
ap.add_argument("--patience", type=int, default=3)
ap.add_argument("--batch", type=int, default=1024)
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--max-train", type=int, default=0, help="subsample training windows (0 = all)")
args = ap.parse_args()

torch.manual_seed(args.seed); np.random.seed(args.seed)
torch.set_num_threads(os.cpu_count() or 4)
fs = FEATURE_SETS[args.features]
ds = find_datasets_dir(args.data)

Xtr, ytr, mtr = build_windows(load_split(ds, args.exp, "train"), fs)
Xte, yte, _ = build_windows(load_split(ds, args.exp, "test"), fs)
val = series_split(mtr, seed=args.seed)
Xfit, yfit, Xval, yval = Xtr[~val], ytr[~val], Xtr[val], ytr[val]
if args.max_train and len(yfit) > args.max_train:
    keep = np.random.default_rng(args.seed).choice(len(yfit), args.max_train, replace=False)
    Xfit, yfit = Xfit[keep], yfit[keep]
print(f"{args.exp} | features={args.features} | train {len(yfit):,} (pos {int(yfit.sum()):,}) "
      f"| val {len(yval):,} (pos {int(yval.sum()):,}) | test {len(yte):,} (pos {int(yte.sum()):,})")

pos_weight = float((len(yfit) - yfit.sum()) / max(yfit.sum(), 1))   # rare onsets -> weight positives up
model = LSTMClassifier(len(fs), args.hidden, args.layers)
opt = torch.optim.Adam(model.parameters(), lr=args.lr)
loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight))
Xt, yt = torch.from_numpy(Xfit), torch.from_numpy(yfit)

best, best_state, bad = -1.0, None, 0
for epoch in range(1, args.epochs + 1):
    model.train(); t = time.time(); total = 0.0
    perm = torch.randperm(len(yt))
    for i in range(0, len(perm), args.batch):
        b = perm[i:i + args.batch]
        opt.zero_grad()
        loss = loss_fn(model(Xt[b]), yt[b])
        loss.backward(); opt.step()
        total += loss.item() * len(b)
    val_m = evaluate(yval, predict(model, Xval))
    print(f"epoch {epoch:2d} | loss {total/len(yt):.4f} | val PR-AUC {val_m['pr_auc']:.4f} | {time.time()-t:.0f}s")
    if val_m["pr_auc"] > best:
        best, best_state, bad = val_m["pr_auc"], {k: v.clone() for k, v in model.state_dict().items()}, 0
    else:
        bad += 1
        if bad >= args.patience:
            print("early stop"); break

model.load_state_dict(best_state)
pval, pte = predict(model, Xval), predict(model, Xte)
thr = best_f1_threshold(yval, pval)
name = f"{args.exp}_lstm_{args.features}_s{args.seed}"
res = {"experiment": args.exp, "model": "lstm", "features": args.features, "seed": args.seed,
       "hparams": {k: getattr(args, k) for k in ["hidden", "layers", "epochs", "batch", "lr", "max_train"]},
       "pos_weight": pos_weight, "val": evaluate(yval, pval, thr), "test": evaluate(yte, pte, thr)}
save_result(name, res)
print(f"\nTEST {fmt(res['test'])}")

MODELS_DIR.mkdir(exist_ok=True)
torch.save(model.state_dict(), MODELS_DIR / f"{name}.pt")
with open(MODELS_DIR / f"{name}.json", "w") as f:
    json.dump({"experiment": args.exp, "features": fs, "window": WINDOW, "hidden": args.hidden,
               "layers": args.layers, "threshold": thr, "val_pr_auc": best,
               "test_pr_auc": res["test"]["pr_auc"]}, f, indent=2)
print(f"Model saved: models/{name}.pt (+ .json)")
