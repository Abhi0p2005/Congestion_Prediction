"""Step 2: floor baselines on one experiment (or all).

  constant     - prevalence; equals what "persistence" gives for the onset target
                 (persistence predicts no change, so it never predicts an onset)
  load_ma      - no training: score = mean cell load over the 2.5 s window
  logreg       - logistic regression on window summaries
  gbt          - gradient-boosted trees on the full window + summaries

Threshold for precision/recall/F1 is chosen on a validation set of whole series
held out from TRAIN, never on test.

Usage:  python 02_baselines.py --data <folder> --exp E2
        python 02_baselines.py --data <folder> --exp all
"""
import argparse
import time

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import (EXPERIMENTS, FEATURE_SETS, best_f1_threshold, build_windows, evaluate,
                    find_datasets_dir, fmt, load_split, save_result, series_split)


def summaries(X):
    """Per-feature mean, std, last value and last-minus-first over the window."""
    return np.concatenate([X.mean(1), X.std(1), X[:, -1], X[:, -1] - X[:, 0]], axis=1)


def run(ds, exp, features, seed):
    fs = FEATURE_SETS[features]
    tr = load_split(ds, exp, "train"); te = load_split(ds, exp, "test")
    Xtr, ytr, mtr = build_windows(tr, fs); Xte, yte, _ = build_windows(te, fs)
    val = series_split(mtr, seed=seed)
    Xfit, yfit, Xval, yval = Xtr[~val], ytr[~val], Xtr[val], ytr[val]
    print(f"\n### {exp} | features={features} | train {len(yfit):,} (pos {int(yfit.sum()):,}) "
          f"| val {len(yval):,} (pos {int(yval.sum()):,}) | test {len(yte):,} (pos {int(yte.sum()):,})")

    out = {}
    # constant / persistence
    out["constant"] = (np.full(len(yval), yfit.mean()), np.full(len(yte), yfit.mean()))
    # moving average of cell load (column 0 is cell_util in every feature set)
    ci = fs.index("cell_util")
    out["load_ma"] = (Xval[:, :, ci].mean(1), Xte[:, :, ci].mean(1))
    # logistic regression
    t = time.time()
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced"))
    lr.fit(summaries(Xfit), yfit)
    out["logreg"] = (lr.predict_proba(summaries(Xval))[:, 1], lr.predict_proba(summaries(Xte))[:, 1])
    print(f"  logreg trained in {time.time()-t:.0f}s")
    # gradient-boosted trees
    t = time.time()
    flat = lambda X: np.concatenate([X.reshape(len(X), -1), summaries(X)], axis=1)
    gbt = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, class_weight="balanced",
                                         early_stopping=True, validation_fraction=0.1, random_state=seed)
    gbt.fit(flat(Xfit), yfit)
    out["gbt"] = (gbt.predict_proba(flat(Xval))[:, 1], gbt.predict_proba(flat(Xte))[:, 1])
    print(f"  gbt trained in {time.time()-t:.0f}s")

    for name, (pval, pte) in out.items():
        thr = best_f1_threshold(yval, pval)
        res = {"experiment": exp, "model": name, "features": features, "seed": seed,
               "val": evaluate(yval, pval, thr), "test": evaluate(yte, pte, thr)}
        save_result(f"{exp}_{name}_{features}_s{seed}", res)
        print(f"  {name:8s} TEST {fmt(res['test'])}")


ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--exp", default="E2", help="E1, E2, E3_k05, E3_k10, E3_k20, E4, E5 or all")
ap.add_argument("--features", default="all", choices=list(FEATURE_SETS))
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

ds = find_datasets_dir(args.data)
for e in (EXPERIMENTS if args.exp == "all" else [args.exp]):
    run(ds, e, args.features, args.seed)
print("\nResults saved in results/ (one JSON per run, plus results/summary.csv)")
