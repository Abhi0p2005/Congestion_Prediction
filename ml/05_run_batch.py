"""Step 5: run many experiments x seeds x models in one go, skipping runs that already have results.
Safe to stop (Ctrl+C) and restart: finished runs are skipped.

Usage:
  python 05_run_batch.py --data <folder> --exps E1 E2 E4 --seeds 0 1 2 --models baselines lstm tcn
  python 05_run_batch.py --data <folder> --exps E1 E2 E3_k20 E4 --seeds 0 1 2 --models baselines lstm --scaling per_source
"""
import argparse
import subprocess
import sys
import time

from common import EXPERIMENTS, FEATURE_SETS, RESULTS_DIR, SCALINGS, run_name

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--exps", nargs="+", default=EXPERIMENTS)
ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
ap.add_argument("--models", nargs="+", default=["baselines", "lstm", "tcn"],
                choices=["baselines", "lstm", "tcn"])
ap.add_argument("--features", default="all", choices=list(FEATURE_SETS))
ap.add_argument("--scaling", default="handoff", choices=SCALINGS)
args = ap.parse_args()

jobs = []
for exp in args.exps:
    if args.scaling == "per_source" and exp == "E5":
        continue
    for seed in args.seeds:
        for m in args.models:
            check = run_name(exp, "gbt" if m == "baselines" else m, args.features, args.scaling, seed)
            if (RESULTS_DIR / f"{check}.json").exists():
                continue
            script = "02_baselines.py" if m == "baselines" else "03_train_nn.py"
            cmd = [sys.executable, script, "--data", args.data, "--exp", exp, "--seed", str(seed),
                   "--features", args.features, "--scaling", args.scaling]
            if m != "baselines":
                cmd += ["--model", m]
            jobs.append((check, cmd))

print(f"{len(jobs)} runs to do (finished runs are skipped)")
t0 = time.time()
for i, (name, cmd) in enumerate(jobs, 1):
    print(f"\n[{i}/{len(jobs)}] {name}  (elapsed {(time.time()-t0)/60:.0f} min)", flush=True)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"!! {name} failed (exit {r.returncode}); continuing")
print(f"\nDone in {(time.time()-t0)/60:.0f} min. Now run: python 06_summarize.py")
