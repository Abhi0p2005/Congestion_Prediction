"""Step 6: turn results/*.json into report tables: mean +- 95% confidence interval over seeds.

Writes results/table_main.csv (one row per model setup, one column per experiment)
and results/table_long.csv, and prints the main table plus the transfer gap E4 - E2.

Usage:  python 06_summarize.py
        python 06_summarize.py --metric test_f1
"""
import argparse
import json

import numpy as np
import pandas as pd
from scipy import stats

from common import EXPERIMENTS, RESULTS_DIR

ap = argparse.ArgumentParser()
ap.add_argument("--metric", default="test_pr_auc",
                help="test_pr_auc (default), test_roc_auc, test_f1, test_precision, test_recall, test_brier")
args = ap.parse_args()

rows = []
for p in RESULTS_DIR.glob("*.json"):
    r = json.load(open(p))
    if "test" not in r:
        continue
    rows.append({"experiment": r["experiment"], "model": r["model"], "features": r.get("features", "all"),
                 "scaling": r.get("scaling", "handoff"), "seed": r.get("seed", 0), "mtime": p.stat().st_mtime,
                 **{f"test_{k}": v for k, v in r["test"].items()},
                 "infer_ms": r.get("infer_ms_one_window"), "params": r.get("params")})
df = pd.DataFrame(rows)
key = ["experiment", "model", "features", "scaling", "seed"]
df = df.sort_values("mtime").drop_duplicates(key, keep="last")   # latest run of each config

def ci95(x):
    x = np.asarray(x, dtype=float)
    return float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else float("nan")

g = df.groupby(["model", "features", "scaling", "experiment"])[args.metric]
long = g.agg(n_seeds="count", mean="mean", ci95=ci95).reset_index()
long["base_rate"] = long.apply(lambda r: df[(df.experiment == r.experiment)]["test_base_rate"].iloc[0], axis=1)
long.to_csv(RESULTS_DIR / "table_long.csv", index=False)

long["cell"] = long.apply(lambda r: f"{r['mean']:.4f}" + (f" ±{r['ci95']:.4f}" if r.n_seeds > 1 else "")
                          + f" (n={r.n_seeds})", axis=1)
order = [e for e in EXPERIMENTS if e in set(long.experiment)]
main = long.pivot_table(index=["model", "features", "scaling"], columns="experiment", values="cell",
                        aggfunc="first")[order]
main.to_csv(RESULTS_DIR / "table_main.csv")

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
print(f"\n{args.metric}: mean ± 95% CI over seeds (n = number of seeds)\n")
print(main.fillna("-").to_string())

base = df.groupby("experiment")["test_base_rate"].first()
print("\nRandom-guess level (base rate):", ", ".join(f"{e} {base[e]:.4f}" for e in order))

if args.metric == "test_pr_auc" and {"E2", "E4"} <= set(long.experiment):
    m = long.pivot_table(index=["model", "features", "scaling"], columns="experiment", values="mean")
    if {"E2", "E4"} <= set(m.columns):
        gap = (m["E4"] - m["E2"]).dropna().sort_values()
        print("\nTransfer gap E4 - E2 (same real test set; smaller = better transfer):")
        print(gap.round(4).to_string())

speed = df.dropna(subset=["infer_ms"]).groupby("model")[["infer_ms", "params"]].median()
if len(speed):
    print("\nInference time per window (median, ms) and parameter count:")
    print(speed.round(3).to_string())
print(f"\nSaved: {RESULTS_DIR/'table_main.csv'}, {RESULTS_DIR/'table_long.csv'}")
