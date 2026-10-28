"""Step 3: train a neural onset predictor (LSTM or TCN) on one experiment.

Input: last 10 bins (2.5 s) x f_* features for one UE. Output: logit of onset 1 s ahead.
Early stopping on validation PR-AUC, where validation = whole series held out from TRAIN.

Usage:  python 03_train_nn.py --data <folder> --exp E2 --model lstm --seed 0
        python 03_train_nn.py --data <folder> --exp E2 --model tcn
        python 03_train_nn.py --data <folder> --exp E2 --model lstm --scaling per_source
Quick smoke test on a subset:  add --max-train 50000 --epochs 2
"""
import argparse
import json
import os
import time

import numpy as np
import torch
from torch import nn

from common import (FEATURE_SETS, MODELS_DIR, SCALINGS, WINDOW, best_f1_threshold, build_windows,
                    evaluate, find_datasets_dir, fmt, load_data, run_name, save_result, series_split)
from model_defs import build_model


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@torch.no_grad()
def predict(model, X, batch=8192):
    model.eval()
    dev = next(model.parameters()).device
    ps = [torch.sigmoid(model(torch.from_numpy(X[i:i + batch]).to(dev))).cpu().numpy()
          for i in range(0, len(X), batch)]
    return np.concatenate(ps) if ps else np.array([])


ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--exp", default="E2")
ap.add_argument("--model", default="lstm", choices=["lstm", "tcn"])
ap.add_argument("--features", default="all", choices=list(FEATURE_SETS))
ap.add_argument("--scaling", default="handoff", choices=SCALINGS)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--size", type=int, default=0, help="LSTM hidden units (default 64) / TCN channels (default 32)")
ap.add_argument("--layers", type=int, default=0, help="LSTM layers (default 1) / TCN levels (default 3)")
ap.add_argument("--epochs", type=int, default=20)
ap.add_argument("--patience", type=int, default=3)
ap.add_argument("--batch", type=int, default=1024)
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--max-train", type=int, default=0, help="subsample training windows (0 = all)")
args = ap.parse_args()
size = args.size or (64 if args.model == "lstm" else 32)
layers = args.layers or (1 if args.model == "lstm" else 3)

torch.manual_seed(args.seed); np.random.seed(args.seed)
torch.set_num_threads(os.cpu_count() or 4)
fs = FEATURE_SETS[args.features]
ds = find_datasets_dir(args.data)

Xtr, ytr, mtr = build_windows(load_data(ds, args.exp, "train", args.scaling), fs)
Xte, yte, _ = build_windows(load_data(ds, args.exp, "test", args.scaling), fs)
val = series_split(mtr, seed=args.seed)
Xfit, yfit, Xval, yval = Xtr[~val], ytr[~val], Xtr[val], ytr[val]
if args.max_train and len(yfit) > args.max_train:
    keep = np.random.default_rng(args.seed).choice(len(yfit), args.max_train, replace=False)
    Xfit, yfit = Xfit[keep], yfit[keep]
print(f"{args.exp} | {args.model} | features={args.features} | scaling={args.scaling} | train {len(yfit):,} "
      f"(pos {int(yfit.sum()):,}) | val {len(yval):,} (pos {int(yval.sum()):,}) | test {len(yte):,} (pos {int(yte.sum()):,})")

pos_weight = float((len(yfit) - yfit.sum()) / max(yfit.sum(), 1))   # rare onsets -> weight positives up
print(f"device: {DEVICE}")
model = build_model(args.model, len(fs), size, layers).to(DEVICE)
opt = torch.optim.Adam(model.parameters(), lr=args.lr)
loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight, device=DEVICE))
Xt, yt = torch.from_numpy(Xfit).to(DEVICE), torch.from_numpy(yfit).to(DEVICE)

best, best_state, bad, t0 = -1.0, None, 0, time.time()
for epoch in range(1, args.epochs + 1):
    model.train(); t = time.time(); total = 0.0
    perm = torch.randperm(len(yt), device=DEVICE)
    for i in range(0, len(perm), args.batch):
        b = perm[i:i + args.batch]
        opt.zero_grad()
        loss = loss_fn(model(Xt[b]), yt[b])
        loss.backward(); opt.step()
        total += loss.item() * len(b)
    val_m = evaluate(yval, predict(model, Xval))
    print(f"epoch {epoch:2d} | loss {total/len(yt):.4f} | val PR-AUC {val_m['pr_auc']:.4f} | {time.time()-t:.0f}s")
    if val_m["pr_auc"] > best:
        best, best_state, bad = val_m["pr_auc"], {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}, 0
    else:
        bad += 1
        if bad >= args.patience:
            print("early stop"); break

model = model.cpu()                     # final evaluation, timing and saving on CPU (as in the xApp)
model.load_state_dict(best_state)
pval, pte = predict(model, Xval), predict(model, Xte)
thr = best_f1_threshold(yval, pval)
# inference time for one decision (one UE window) on this CPU
model.eval(); one = torch.from_numpy(Xte[:1])
with torch.no_grad():
    for _ in range(20): model(one)
    t = time.perf_counter()
    for _ in range(200): model(one)
infer_ms = (time.perf_counter() - t) / 200 * 1000

name = run_name(args.exp, args.model, args.features, args.scaling, args.seed)
n_params = sum(p.numel() for p in model.parameters())
res = {"experiment": args.exp, "model": args.model, "features": args.features, "scaling": args.scaling,
       "seed": args.seed, "hparams": {"size": size, "layers": layers, "epochs": args.epochs, "batch": args.batch,
                                      "lr": args.lr, "max_train": args.max_train},
       "params": n_params, "infer_ms_one_window": infer_ms, "train_s": time.time() - t0,
       "pos_weight": pos_weight, "val": evaluate(yval, pval, thr), "test": evaluate(yte, pte, thr)}
save_result(name, res)
print(f"\nTEST {fmt(res['test'])}")
print(f"params {n_params:,} | inference {infer_ms:.2f} ms per window (budget 250 ms)")

MODELS_DIR.mkdir(exist_ok=True)
torch.save(model.state_dict(), MODELS_DIR / f"{name}.pt")
with open(MODELS_DIR / f"{name}.json", "w") as f:
    json.dump({"experiment": args.exp, "model": args.model, "features": fs, "scaling": args.scaling,
               "window": WINDOW, "size": size, "layers": layers, "threshold": thr, "val_pr_auc": best,
               "test_pr_auc": res["test"]["pr_auc"]}, f, indent=2)
print(f"Model saved: models/{name}.pt (+ .json)")
