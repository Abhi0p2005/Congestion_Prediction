"""Step 1: check that the datasets load and match HANDOFF.md before training anything.

Usage:  python 01_check_data.py --data <folder where you unzipped CP_5G_Congestion_datasets.zip>
"""
import argparse
from pathlib import Path

from common import (EXPECTED, EXPERIMENTS, FEATURES, build_windows, check_scaler,
                    find_datasets_dir, load_scaler, load_split)

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
args = ap.parse_args()

ds = find_datasets_dir(args.data)
print(f"Datasets folder: {ds}\n")

all_ok = True
for exp in EXPERIMENTS:
    if not (ds / exp).exists():
        print(f"{exp}: folder missing")
        all_ok = False
        continue
    print(f"=== {exp} ===")
    for i, split in enumerate(["train", "test"]):
        df = load_split(ds, exp, split)
        rows, onsets = len(df), int((df["onset"] == 1).sum())
        exp_rows, exp_on = EXPECTED[exp][2 * i], EXPECTED[exp][2 * i + 1]
        ok = rows == exp_rows and (exp_on is None or onsets == exp_on)
        all_ok &= ok
        missing = [c for c in ["f_" + f for f in FEATURES] + ["onset", "experiment", "ue", "bin"] if c not in df.columns]
        nan_f = int(df[[c for c in df.columns if c.startswith("f_")]].isna().sum().sum())
        X, y, meta = build_windows(df)
        n_series = df.groupby(["experiment", "ue"]).ngroups
        print(f"  {split:5s} rows {rows:>8,} (expected {exp_rows:,}) | onsets {onsets:>6,} "
              f"(expected {exp_on if exp_on is not None else '≈'}) | {'OK' if ok else 'MISMATCH'}")
        print(f"        series {n_series:,} | usable 10-bin windows {len(y):,} with {int(y.sum()):,} onsets "
              f"| NaN in f_* {nan_f} | missing columns {missing or 'none'}")
        if split == "test":
            scaler_path = ds / exp / "scaler.json"
            try:
                sc = load_scaler(scaler_path)
                worst = check_scaler(df, sc)
                good = all(v < 1e-3 for v in worst.values() if v == v)
                print(f"  scaler.json: {'reproduces f_* columns' if good else 'DOES NOT match f_* columns'} "
                      f"(max error {max(v for v in worst.values() if v == v):.2e})")
                all_ok &= good
            except Exception as e:
                print(f"  scaler.json: could not read ({e})")
                all_ok = False
    print()

print("ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED: send this output before training.")
