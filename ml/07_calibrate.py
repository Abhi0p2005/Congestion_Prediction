"""Step 7: calibration and alarm thresholds for trained neural models.

Class-weighted training makes raw probabilities far too high, and simulator-trained models are
miscalibrated on real data (onsets are ~16x rarer there). This script compares:

  none        raw model output
  temp_val    temperature scaling fitted on the model's validation set (same source as training)
  platt_val   Platt scaling (logistic on the logit) fitted on the validation set
  platt_real  Platt scaling fitted on a few minutes of labelled REAL data from the E4 training pool
              (never the test set). Only for models whose test set is real and that were not
              trained on real data alone (E2, E3_*). This is the "recalibrate live" scenario.

For each: Brier score, expected calibration error (ECE), mean predicted vs observed rate, and the
alarm rule (threshold = best F1 on that calibration set) applied to test: precision, recall,
alarms per UE-hour, and false alarms in calm conditions (1-2 active users).
PR-AUC does not change with calibration (it only depends on the ranking).

Usage:  python 07_calibrate.py --data <folder> --model E2_lstm_all_ps_s0
        python 07_calibrate.py --data <folder> --model all          (every saved model)
        options: --recal-minutes 10
Writes results/calib_<model>.json, results/calibration_summary.csv, models/<model>_calib.json,
and results/reliability_<model>.png (if matplotlib is installed).
"""
import argparse
import json
import re

import numpy as np
import pandas as pd
import torch
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LogisticRegression

from common import (MODELS_DIR, RESULTS_DIR, apply_scaler, best_f1_threshold, build_windows, evaluate,
                    find_datasets_dir, load_data, load_scaler, series_split)
from model_defs import build_model

EPS = 1e-6


def logit(p):
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def fit_platt(p, y):
    lr = LogisticRegression(C=1e6, max_iter=1000).fit(logit(p).reshape(-1, 1), y)
    a, b = float(lr.coef_[0, 0]), float(lr.intercept_[0])
    return {"a": a, "b": b}


def apply_platt(p, prm):
    return sigmoid(prm["a"] * logit(p) + prm["b"])


def fit_temp(p, y):
    z = logit(p)
    def nll(logT):
        q = np.clip(sigmoid(z / np.exp(logT)), EPS, 1 - EPS)
        return -np.mean(y * np.log(q) + (1 - y) * np.log(1 - q))
    r = minimize_scalar(nll, bounds=(np.log(0.05), np.log(50)), method="bounded")
    return {"T": float(np.exp(r.x))}


def apply_temp(p, prm):
    return sigmoid(logit(p) / prm["T"])


def ece(y, p, bins=15):
    """Expected calibration error with equal-count bins (better than equal-width for rare events)."""
    order = np.argsort(p)
    chunks = np.array_split(order, bins)
    err, rows = 0.0, []
    for c in chunks:
        if len(c) == 0:
            continue
        mp, my = float(p[c].mean()), float(y[c].mean())
        err += len(c) / len(p) * abs(mp - my)
        rows.append((mp, my, len(c)))
    return err, rows


@torch.no_grad()
def predict(model, X, batch=8192):
    model.eval()
    return np.concatenate([torch.sigmoid(model(torch.from_numpy(X[i:i + batch]))).numpy()
                           for i in range(0, len(X), batch)])


def real_sample(ds, card, minutes, seed):
    """A few minutes of labelled real data from the E4 training pool, scaled the way the model expects."""
    if card["scaling"] == "per_source":
        df = load_data(ds, "E4", "train", "per_source")
    else:
        df = apply_scaler(load_data(ds, "E4", "train"), load_scaler(ds / card["experiment"] / "scaler.json"))
    X, y, meta = build_windows(df, card["features"])
    keys = (meta["experiment"].astype(str) + "|" + meta["ue"].astype(str)).values
    rng = np.random.default_rng(seed)
    chosen, n_win, n_pos = [], 0, 0
    for k in rng.permutation(np.unique(keys)):
        m = keys == k
        chosen.append(k); n_win += int(m.sum()); n_pos += int(y[m].sum())
        if n_win >= minutes * 240 and n_pos >= 10:      # 240 windows per minute (250 ms bins)
            break
    mask = np.isin(keys, chosen)
    return X[mask], y[mask], len(chosen)


def run(ds, name, minutes):
    card = json.load(open(MODELS_DIR / f"{name}.json"))
    card.setdefault("model", "lstm"); card.setdefault("scaling", "handoff")
    card.setdefault("size", card.get("hidden"))
    exp, fs, scaling = card["experiment"], card["features"], card["scaling"]
    seed = int(re.search(r"_s(\d+)$", name).group(1))

    model = build_model(card["model"], len(fs), card["size"], card["layers"])
    model.load_state_dict(torch.load(MODELS_DIR / f"{name}.pt", map_location="cpu"))

    Xtr, ytr, mtr = build_windows(load_data(ds, exp, "train", scaling), fs)
    Xte, yte, mte = build_windows(load_data(ds, exp, "test", scaling), fs)
    val = series_split(mtr, seed=seed)                    # same validation split as in training
    pval, pte = predict(model, Xtr[val]), predict(model, Xte)
    yval = ytr[val]
    calm = (mte["n_ue_active"] <= 2).values if "n_ue_active" in mte else np.zeros(len(yte), bool)
    hours = len(yte) * 0.25 / 3600

    variants = {"none": (lambda p: p, None, pval, yval)}
    variants["temp_val"] = (None, fit_temp(pval, yval), pval, yval)
    variants["platt_val"] = (None, fit_platt(pval, yval), pval, yval)
    info = {}
    if exp == "E2" or exp.startswith("E3"):      # real test set, and not trained on real data alone
        Xr, yr, n_series = real_sample(ds, card, minutes, seed)
        pr = predict(model, Xr)
        variants["platt_real"] = (None, fit_platt(pr, yr), pr, yr)
        info = {"real_sample_windows": int(len(yr)), "real_sample_onsets": int(yr.sum()),
                "real_sample_series": n_series, "real_sample_minutes": len(yr) / 240}

    out = {"model": name, "experiment": exp, "kind": card["model"], "scaling": scaling, "seed": seed,
           "test_pr_auc": evaluate(yte, pte)["pr_auc"], "test_base_rate": float(yte.mean()), **info, "variants": {}}
    rel = {}
    for v, (_, prm, pcal_set, ycal_set) in variants.items():
        f = (lambda p: p) if prm is None else (apply_temp if "T" in prm else apply_platt)
        g = (lambda p, f=f, prm=prm: f(p, prm)) if prm is not None else (lambda p: p)
        pt, pc = g(pte), g(pcal_set)
        thr = best_f1_threshold(ycal_set, pc)
        m = evaluate(yte, pt, thr)
        e, rows = ece(yte, pt)
        rel[v] = rows
        out["variants"][v] = {
            "params": prm, "threshold": thr, "brier": m["brier"], "ece": e,
            "mean_pred": float(pt.mean()), "observed_rate": float(yte.mean()),
            "precision": m["precision"], "recall": m["recall"], "f1": m["f1"],
            "alarms_per_ue_hour": m["alarms"] / hours,
            "calm_false_alarm_rate": float((pt[calm] >= thr).mean()) if calm.any() else None}

    RESULTS_DIR.mkdir(exist_ok=True)
    json.dump(out, open(RESULTS_DIR / f"calib_{name}.json", "w"), indent=2)
    json.dump({v: {"params": d["params"], "threshold": d["threshold"]} for v, d in out["variants"].items()},
              open(MODELS_DIR / f"{name}_calib.json", "w"), indent=2)
    flat = [{"model": name, "experiment": exp, "kind": card["model"], "scaling": scaling, "seed": seed,
             "variant": v, **{k: d[k] for k in ["brier", "ece", "mean_pred", "observed_rate", "precision",
                                                 "recall", "f1", "alarms_per_ue_hour", "calm_false_alarm_rate"]}}
            for v, d in out["variants"].items()]
    summ = RESULTS_DIR / "calibration_summary.csv"
    old = pd.read_csv(summ) if summ.exists() else pd.DataFrame()
    if len(old):
        old = old[old["model"] != name]
    pd.concat([old, pd.DataFrame(flat)]).to_csv(summ, index=False)

    print(f"\n### {name} | test PR-AUC {out['test_pr_auc']:.4f} (unchanged by calibration) | "
          f"observed onset rate {yte.mean():.4f}")
    if info:
        print(f"    real recalibration sample: {info['real_sample_minutes']:.1f} min, "
              f"{info['real_sample_onsets']} onsets, {info['real_sample_series']} users (from E4 train)")
    print(f"    {'variant':10s} {'mean_pred':>9s} {'ECE':>7s} {'Brier':>7s} {'prec':>6s} {'recall':>6s} "
          f"{'F1':>6s} {'alarms/UE-h':>11s} {'calm FA':>8s}")
    for v, d in out["variants"].items():
        cfa = f"{d['calm_false_alarm_rate']:.4f}" if d["calm_false_alarm_rate"] is not None else "-"
        print(f"    {v:10s} {d['mean_pred']:9.4f} {d['ece']:7.4f} {d['brier']:7.4f} {d['precision']:6.3f} "
              f"{d['recall']:6.3f} {d['f1']:6.3f} {d['alarms_per_ue_hour']:11.1f} {cfa:>8s}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5, 5))
        top = max(max(r[0] for r in rows) for rows in rel.values())
        ax.plot([0, top], [0, top], "k--", lw=1, label="perfect")
        for v, rows in rel.items():
            ax.plot([r[0] for r in rows], [r[1] for r in rows], "o-", ms=3, label=v)
        ax.set_xscale("symlog", linthresh=1e-3); ax.set_yscale("symlog", linthresh=1e-3)
        ax.set_xlabel("mean predicted probability"); ax.set_ylabel("observed onset rate")
        ax.set_title(f"Reliability on test: {name}", fontsize=9); ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(RESULTS_DIR / f"reliability_{name}.png", dpi=130); plt.close(fig)
    except ImportError:
        pass


ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--model", required=True, help="model name in models/, or 'all'")
ap.add_argument("--recal-minutes", type=float, default=10)
args = ap.parse_args()
ds = find_datasets_dir(args.data)
names = ([p.stem for p in sorted(MODELS_DIR.glob("*.pt"))] if args.model == "all" else [args.model])
for n in names:
    run(ds, n, args.recal_minutes)
print("\nSaved: results/calibration_summary.csv, results/calib_<model>.json, models/<model>_calib.json")
