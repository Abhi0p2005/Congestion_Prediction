# Stage 2: ML scripts (congestion-onset prediction)

Follows HANDOFF.md from the dataset team: six `f_*` inputs, 10-bin (2.5 s) windows,
`onset` target 1 s ahead, series broken at gaps, validation = whole series held out
from the training set, PR-AUC as the main score.

| Step | Script | Output |
|---|---|---|
| 1 | `01_check_data.py --data <folder>` | Checks row/onset counts vs HANDOFF.md, gaps, scaler |
| 2 | `02_baselines.py --data <folder> --exp E2` | constant, load moving average, logistic regression, gradient-boosted trees |
| 3 | `03_train_lstm.py --data <folder> --exp E2 --seed 0` | LSTM, saved in `models/` |
| 4 | `04_export_onnx.py --data <folder> --model E2_lstm_all_s0` | Hand-off package for the xApp in `package/` |

Options: `--exp all` (baselines), `--features all|reduced|no_ulerr`, `--max-train 50000` (quick test).
All results go to `results/<run>.json` and one table, `results/summary.csv`.
