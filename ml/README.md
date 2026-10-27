# Stage 2: ML scripts (congestion-onset prediction)

Follows HANDOFF.md from the dataset team: six `f_*` inputs, 10-bin (2.5 s) windows,
`onset` target 1 s ahead, series broken at gaps, validation = whole series held out
from the training set, PR-AUC as the main score.

| Step | Script | What it does |
|---|---|---|
| 1 | `01_check_data.py --data <folder>` | Checks row/onset counts vs HANDOFF.md, gaps, scaler |
| 2 | `02_baselines.py --data <folder> --exp E2 [--scaling per_source]` | constant, load moving average, logistic regression, gradient-boosted trees |
| 3 | `03_train_nn.py --data <folder> --exp E2 --model lstm\|tcn [--scaling per_source]` | Neural models, saved in `models/` |
| 4 | `04_export_onnx.py --data <folder> --model E2_lstm_all_s0` | Hand-off package for the xApp in `package/` |
| 5 | `05_run_batch.py --data <folder> --exps E1 E2 E4 --seeds 0 1 2 --models baselines lstm tcn` | Many runs; skips finished ones; safe to stop and restart |
| 6 | `06_summarize.py` | Mean ± 95% CI over seeds, transfer gap E4 − E2, inference time |

Options: `--features all|reduced|no_ulerr`, `--scaling handoff|per_source`, `--max-train 50000` (quick test).

**Scaling:** `handoff` = the dataset team's train-set scaling (default; the only one that can be exported).
`per_source` = each source standardised with its own statistics (simulator from E1 train, real from
E4 train; neither touches the shared real test set). Ablation for the sim-to-real gap; E1–E4 only.

Results: `results/<run>.json`, `results/summary.csv`, and after step 6 `results/table_main.csv`.
