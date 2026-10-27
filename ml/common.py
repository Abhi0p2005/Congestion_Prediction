"""Shared helpers for Stage 2 (ML side).

Follows HANDOFF.md exactly:
  - one time series = one (experiment, ue) pair, ordered by bin
  - a gap (bin jump other than +1) breaks the series; no window may span it
  - window = last 10 bins (2.5 s) of the six f_* columns, target = onset at the window's last bin
  - rows with empty onset are dropped
  - never tune on a test set: validation = whole series held out from the training set
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_recall_curve, roc_auc_score)

FEATURES = ["cell_util", "dl_cqi", "ul_sinr", "dl_mbps", "ul_mbps", "ul_error_pct"]
REDUCED = ["cell_util", "ul_sinr", "dl_mbps", "ul_mbps"]          # reduced-input ablation
NO_ULERR = ["cell_util", "dl_cqi", "ul_sinr", "dl_mbps", "ul_mbps"]  # drop ul_error_pct ablation
FEATURE_SETS = {"all": FEATURES, "reduced": REDUCED, "no_ulerr": NO_ULERR}
WINDOW = 10            # bins = 2.5 s of history
EXPERIMENTS = ["E1", "E2", "E3_k05", "E3_k10", "E3_k20", "E4", "E5"]

# From HANDOFF.md "Expected sizes": (train rows, train onsets, test rows, test onsets); None = not given exactly
EXPECTED = {
    "E1": (355737, 24693, 129809, 7207),
    "E2": (485546, 31900, 242347, 1026),
    "E3_k05": (500034, None, 242347, 1026),
    "E3_k10": (516980, None, 242347, 1026),
    "E3_k20": (557017, None, 242347, 1026),
    "E4": (359245, 2580, 242347, 1026),
    "E5": (139104, 237, 124701, 1355),
}

META_COLS = ["source", "experiment", "ue", "bin", "t_s", "serving_cell",
             "traffic_class", "n_ue_active", "starved"]

RESULTS_DIR = Path("results")
MODELS_DIR = Path("models")


# ---------------------------------------------------------------- data location
def find_datasets_dir(root):
    """Return the folder that contains E1, E2, ... (each with train.csv.gz)."""
    root = Path(root)
    for p in [root] + [d for d in root.rglob("*") if d.is_dir()]:
        if (p / "E2" / "train.csv.gz").exists():
            return p
    raise FileNotFoundError(
        f"No folder containing E2/train.csv.gz found under {root}. "
        "Unzip CP_5G_Congestion_datasets.zip and pass --data <that folder>.")


def load_split(datasets_dir, exp, split):
    """Load train or test of one experiment with only the columns we use."""
    path = Path(datasets_dir) / exp / f"{split}.csv.gz"
    wanted = set(META_COLS + FEATURES + ["f_" + c for c in FEATURES] + ["onset"])
    header = pd.read_csv(path, nrows=0).columns
    cols = [c for c in header if c in wanted]
    df = pd.read_csv(path, usecols=cols, low_memory=False)
    for c in FEATURES + ["f_" + c for c in FEATURES] + ["onset"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float32")
    return df


# ---------------------------------------------------------------- windows
def build_windows(df, features=FEATURES, scaled=True):
    """Return X (n, WINDOW, n_feat) float32, y (n,) float32, meta DataFrame (one row per window).

    A window ends at a row whose onset is defined and that has WINDOW-1 earlier rows
    in the same gap-free segment of the same (experiment, ue) series."""
    cols = [("f_" + c) if scaled else c for c in features]
    df = df.sort_values(["experiment", "ue", "bin"], kind="mergesort").reset_index(drop=True)
    same_series = (df["experiment"].values[1:] == df["experiment"].values[:-1]) & \
                  (df["ue"].values[1:] == df["ue"].values[:-1])
    contiguous = np.diff(df["bin"].values.astype(np.int64)) == 1
    new_seg = np.concatenate([[True], ~(same_series & contiguous)])
    seg_id = np.cumsum(new_seg)
    pos = df.groupby(seg_id).cumcount().values
    valid = (pos >= WINDOW - 1) & df["onset"].notna().values
    idx = np.flatnonzero(valid)

    arr = df[cols].to_numpy(dtype=np.float32)
    if scaled:
        arr = np.nan_to_num(arr, nan=0.0)   # dataset already fills; this is only a guard
    X = np.stack([arr[idx - (WINDOW - 1 - k)] for k in range(WINDOW)], axis=1)
    y = df["onset"].to_numpy(dtype=np.float32)[idx]
    meta = df.iloc[idx][[c for c in META_COLS if c in df.columns]].reset_index(drop=True)
    return X, y, meta


def series_split(meta, val_frac=0.15, seed=0):
    """Hold out whole (experiment, ue) series for validation. Returns boolean mask of validation rows."""
    keys = meta["experiment"].astype(str) + "|" + meta["ue"].astype(str)
    uniq = keys.unique()
    rng = np.random.default_rng(seed)
    n_val = max(1, int(round(len(uniq) * val_frac)))
    val_keys = set(rng.choice(uniq, size=n_val, replace=False))
    return keys.isin(val_keys).values


# ---------------------------------------------------------------- metrics
def best_f1_threshold(y, p):
    prec, rec, thr = precision_recall_curve(y, p)
    f1 = 2 * prec * rec / np.clip(prec + rec, 1e-12, None)
    i = int(np.nanargmax(f1[:-1])) if len(thr) else 0
    return float(thr[i]) if len(thr) else 0.5


def evaluate(y, p, threshold=None):
    y = np.asarray(y)
    p = np.asarray(p, dtype=np.float64)
    out = {"n": int(len(y)), "positives": int(y.sum()), "base_rate": float(y.mean()),
           "pr_auc": float(average_precision_score(y, p)) if y.sum() > 0 else float("nan"),
           "roc_auc": float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else float("nan"),
           "brier": float(brier_score_loss(y, np.clip(p, 0, 1)))}
    if threshold is not None:
        pred = p >= threshold
        tp = int((pred & (y == 1)).sum()); fp = int((pred & (y == 0)).sum()); fn = int((~pred & (y == 1)).sum())
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        out.update({"threshold": float(threshold), "precision": prec, "recall": rec,
                    "f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
                    "alarms": int(pred.sum())})
    return out


def save_result(name, result):
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / f"{name}.json", "w") as f:
        json.dump(result, f, indent=2)
    cols = ["n", "positives", "base_rate", "pr_auc", "roc_auc", "brier", "threshold", "precision", "recall", "f1", "alarms"]
    flat = {"run": name, **{k: result.get(k) for k in ["experiment", "model", "features", "seed"]}}
    for part in ["val", "test"]:
        for c in cols:
            flat[f"{part}_{c}"] = result.get(part, {}).get(c)
    summary = RESULTS_DIR / "summary.csv"
    pd.DataFrame([flat]).to_csv(summary, mode="a", header=not summary.exists(), index=False)


def fmt(m):
    s = f"PR-AUC {m['pr_auc']:.4f} | ROC-AUC {m['roc_auc']:.4f} | base rate {m['base_rate']:.4f}"
    if "f1" in m:
        s += f" | P {m['precision']:.3f} R {m['recall']:.3f} F1 {m['f1']:.3f} @thr {m['threshold']:.3f}"
    return s


# ---------------------------------------------------------------- scaler.json
def load_scaler(path):
    """Return {feature: (mean, std)} for the six raw features, accepting common layouts.
    Always confirm with check_scaler() that it reproduces the f_* columns."""
    with open(path) as f:
        s = json.load(f)

    def norm(k):
        return k[2:] if k.startswith("f_") else k

    out = {}
    if isinstance(s, dict) and "mean" in s and "std" in s:
        m, d = s["mean"], s["std"]
        if isinstance(m, dict):
            out = {norm(k): (float(m[k]), float(d[k])) for k in m}
        else:
            names = s.get("columns") or s.get("features") or s.get("feature_names")
            if not names:
                raise ValueError(f"{path}: mean/std are lists but no column names given; send this file's content.")
            out = {norm(k): (float(a), float(b)) for k, a, b in zip(names, m, d)}
    elif isinstance(s, dict) and all(isinstance(v, dict) for v in s.values()):
        for k, v in s.items():
            mean = v.get("mean", v.get("mu"))
            std = v.get("std", v.get("sd", v.get("scale")))
            if mean is not None and std is not None:
                out[norm(k)] = (float(mean), float(std))
    missing = [c for c in FEATURES if c not in out]
    if missing:
        raise ValueError(f"{path}: could not find mean/std for {missing}. Layout: {json.dumps(s)[:500]}")
    return {c: out[c] for c in FEATURES}


def check_scaler(df, scaler):
    """Max |(raw-mean)/std - f_*| over rows where raw is present. Should be ~1e-5."""
    worst = {}
    for c in FEATURES:
        if c in df.columns and "f_" + c in df.columns:
            m, s = scaler[c]
            ok = df[c].notna()
            diff = np.abs((df.loc[ok, c] - m) / s - df.loc[ok, "f_" + c])
            worst[c] = float(diff.max()) if ok.any() else float("nan")
    return worst
