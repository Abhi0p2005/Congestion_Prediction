"""Step 4: export a trained model as the hand-off package for the live xApp.

Creates package/<model name>/ with:
  model.onnx         input "x": (batch, 10, n_features) SCALED features -> output "p": onset probability
  scaler.json        copy of the training experiment's scaler (the xApp scales raw inputs with it)
  model_card.json    feature order, window, bin size, horizon, threshold, versions, metrics
  test_vectors.json  RAW input windows + expected probability, so the xApp's own scaling is tested too

Usage:  python 04_export_onnx.py --data <folder> --model E2_lstm_all_s0   (or E2_tcn_all_s0)
"""
import argparse
import json
import platform
import shutil
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch

from common import (MODELS_DIR, WINDOW, build_windows, check_scaler, find_datasets_dir, load_scaler,
                    load_split)

from model_defs import build_model

class Wrapped(torch.nn.Module):
    def __init__(self, m):
        super().__init__(); self.m = m

    def forward(self, x):
        return torch.sigmoid(self.m(x))


ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--model", required=True, help="name in models/, e.g. E2_lstm_all_s0")
ap.add_argument("--n-vectors", type=int, default=10)
args = ap.parse_args()

card = json.load(open(MODELS_DIR / f"{args.model}.json"))
fs, exp = card["features"], card["experiment"]

kind = card.get("model", "lstm")
size = card.get("size", card.get("hidden"))
if card.get("scaling", "handoff") != "handoff":
    raise SystemExit("Only models trained with --scaling handoff can be exported (they match scaler.json).")
model = build_model(kind, len(fs), size, card["layers"])
model.load_state_dict(torch.load(MODELS_DIR / f"{args.model}.pt", map_location="cpu"))
model.eval()

out = Path("package") / args.model
out.mkdir(parents=True, exist_ok=True)
onnx_path = out / "model.onnx"
dummy = torch.zeros(1, WINDOW, len(fs))
wrapped = Wrapped(model).eval()
torch.onnx.export(wrapped, dummy, str(onnx_path), input_names=["x"], output_names=["p"],
                  dynamic_axes={"x": {0: "batch"}, "p": {0: "batch"}}, opset_version=17, dynamo=False)
onnx.checker.check_model(onnx.load(str(onnx_path)))
wrapped.eval()   # export can restore training mode; make sure dropout is off

# scaler: copy and verify it reproduces the f_* columns
ds = find_datasets_dir(args.data)
shutil.copy(ds / exp / "scaler.json", out / "scaler.json")
scaler = load_scaler(ds / exp / "scaler.json")
te = load_split(ds, exp, "test")
worst = check_scaler(te, scaler)
assert all(v < 1e-3 for v in worst.values() if v == v), f"scaler.json does not reproduce f_* columns: {worst}"

# test vectors from the test set: windows with complete raw inputs, half onsets, half not
Xs, y, meta = build_windows(te, fs, scaled=True)
Xr, _, _ = build_windows(te, fs, scaled=False)
complete = ~np.isnan(Xr).any(axis=(1, 2))
rng = np.random.default_rng(0)
pick = []
for label in (1, 0):
    cand = np.flatnonzero(complete & (y == label))
    pick += list(rng.choice(cand, size=min(args.n_vectors // 2, len(cand)), replace=False))

sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
p_onnx = sess.run(None, {"x": Xs[pick]})[0]
with torch.no_grad():
    p_torch = wrapped(torch.from_numpy(Xs[pick])).numpy()
assert np.allclose(p_onnx, p_torch, atol=1e-5), "ONNX and PyTorch outputs differ"

# check that scaling the raw window with scaler.json gives the scaled window
mean = np.array([scaler[c][0] for c in fs], dtype=np.float32)
std = np.array([scaler[c][1] for c in fs], dtype=np.float32)
assert np.allclose((Xr[pick] - mean) / std, Xs[pick], atol=1e-3), "raw->scaled mismatch"

vectors = [{"raw_window": Xr[i].round(6).tolist(), "label_onset": int(y[i]),
            "expected_probability": float(p)} for i, p in zip(pick, p_onnx)]
json.dump({"features": fs, "window_bins": WINDOW, "note": "rows = oldest..newest bin; columns = features",
           "vectors": vectors}, open(out / "test_vectors.json", "w"), indent=1)

json.dump({
    "model": args.model, "trained_on": exp, "architecture": f"{kind.upper()} size={size} layers={card['layers']}",
    "input": {"name": "x", "shape": ["batch", WINDOW, len(fs)], "features_in_order": fs,
              "scaling": "(raw - mean) / std using scaler.json; missing value -> carry last value, else 0 after scaling"},
    "output": {"name": "p", "meaning": "probability of starvation onset 1 s (4 bins) ahead", "calibrated": False},
    "bin_ms": 250, "horizon_bins": 4, "alarm_threshold": card["threshold"],
    "metrics": {"val_pr_auc": card["val_pr_auc"], "test_pr_auc": card["test_pr_auc"]},
    "versions": {"python": platform.python_version(), "torch": torch.__version__,
                 "onnx": onnx.__version__, "onnxruntime": ort.__version__},
}, open(out / "model_card.json", "w"), indent=2)

print(f"Package written to {out}/  (model.onnx, scaler.json, model_card.json, test_vectors.json)")
print(f"ONNX matches PyTorch on {len(pick)} test vectors.")
