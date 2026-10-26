# Project Docs Summary

Summary of the three report documents in this project:

1. `5G_Congestion_Results_Report_ArnavK.docx` — Results & Findings (LSTM)
2. `Model_Comparison_Report_5models.docx` — 5-Model Comparison
3. `Simulation_Impact_Analysis.docx` — Simulation-to-Reality Gap Analysis

**Common thread:** The work is methodologically sound *inside the simulation*, but the throughput-label issue and the absence of any real-data validation are the biggest threats to the real-world claim.

---

## 1. 5G_Congestion_Results_Report_ArnavK.docx

### Objective
CDAC internship congestion-prediction track. Key distinction the whole project is built around:

- **Reactive congestion handling** — a controller reacts to a KPI only *after* it crosses a threshold (congestion already happened).
- **Proactive congestion prediction** — a model forecasts a KPI's near-future trajectory so a breach can be anticipated *before* it happens.

### Simulation Setup
- Framework: OMNeT++ / Simu5G (WSL2/Ubuntu).
- Topology: 5-cell urban NR cluster — 1 macro gNB (500m,500m, 46 dBm) + 3 micro gNBs (30 dBm) + 50 UEs (RandomWaypoint mobility, 1–5 m/s).
- Traffic: baseline CBR (DL+UL, ~250 KB/s cell-wide) + injected **asymmetric uplink burst** (T=50–70s) to create a controlled congestion event.
- 10 seeded runs → parsed into a **60,043-row KPI dataset**.

### LSTM Model
- Input: 1-second history window (10 bins × 100ms), 8 features.
- Targets (next bin): Avg_Latency, Total_Throughput, Avg_HARQ_Attempts.
- Architecture: 2-layer LSTM (hidden 64, dropout 0.2) → LayerNorm → Linear(64→32) → ReLU → Dropout → Linear(32→3). 54,531 params.

### Key Results
| Target | Test R² | Verdict |
|---|---|---|
| Avg_Latency | 0.854 | Strong fit (but see leakage note below) |
| Avg_HARQ_Attempts | 0.714 | Good fit |
| Total_Throughput | 0.188 | Weak — no relationship to any other KPI |

### Problems / Open Items
- Burst is **uplink-only** and doesn't recover by sim end — no clean before/during/after narrative.
- **MAC queue depth and PRB utilization are 100% empty** (0 values in 60,043 rows) — explicitly targeted KPIs not recorded.
- Headline deliverable — quantified **lead-time comparison** between LSTM forecast and reactive (threshold) detector — not yet produced even though code exists.
- KPI redundancy found: Avg_Latency ↔ Avg_RLC_Delay = 1.00 (identical signal); Avg_PacketLoss ↔ Avg_HARQ = 0.91.

### Phase Status (Table 1)
| Phase | Status |
|---|---|
| Environment setup (OMNeT++ + Simu5G) | Done |
| NED topology design | Done |
| .ini configuration | Done |
| KPI vector recording | Partial — throughput/delay/SINR recorded; PRB/queue missing |
| .vec → CSV parser | Done |
| LSTM training | In progress |
| Batch sweeps (density, mix, seeds) | Pending |
| Spatial/graph features, GNN training | Pending |

---

## 2. Model_Comparison_Report_5models.docx

Compares **5 models**: Moving Average, ARIMA(2,0,1), LSTM, GraphSAGE GNN, TCN.

### Common Setup
- Same per-UE, per-100ms-bin KPI table, 8 features (Avg_Latency, Total_Throughput, Avg_CQI, Avg_SINR, Avg_PacketLoss, Avg_HARQ_Attempts, Avg_RLC_Delay, Total_Throughput_UL).
- 10-bin (1s) sliding window → predict next bin. StandardScaler fit on training data only.
- **Trained on UDP-burst** scenario, evaluated on an **unseen gradual-ramp** scenario (genuine generalization test).

### Models & Results (unseen gradual-ramp scenario)

#### LSTM
- 2-layer LSTM, hidden 64, **3 targets**, 54,531 params.
- Latency R²=0.86 in-distribution; **0.832** on unseen scenario.
- Classification: ROC-AUC 0.879, F1 0.482, Precision 0.417, Recall 0.571.

#### GNN (GraphSAGE)
- 3-layer GraphSAGE, hidden 64, **1 target (latency only)**, 20,097 params (~⅓ of LSTM).
- Nodes = UEs; edges = UEs sharing the same serving cell (undirected, fully-connected).
- In-distribution latency R² = **0.97** (beats LSTM).
- **Collapses to R² = 0.039 on the unseen scenario** — yet **wins all classification metrics**: ROC-AUC 0.924, F1 0.535, Precision 0.449, Recall 0.662.

#### TCN
- 3-block dilated causal convolutions (dilation 1,2,4), same 3 targets, same 8 features.
- Latency R² = **0.775** on unseen scenario; F1 0.507, ROC-AUC 0.880.
- Proves the GNN collapse is *not* a generic "modern architecture" problem.

#### Moving Average (baseline)
- Predicts next value = mean of previous 10 latency readings. No training.
- **Surprisingly strong**: ROC-AUC 0.890, F1 0.505, Precision 0.495, Recall 0.515; Latency R²=0.269.

#### ARIMA(2,0,1)
- Rolling one-step-ahead refit per UE (sample of 20 UEs), costly.
- Regression **catastrophic**: Latency R² = **−261.96**. Classification usable: F1 0.392, Recall 0.588.

### Full Comparison Table (unseen scenario)
| Model | ROC-AUC | F1 | Precision | Recall | Latency R² |
|---|---|---|---|---|---|
| Moving Average | 0.890 | 0.505 | 0.495 | 0.515 | 0.269 |
| ARIMA(2,0,1) | 0.798 | 0.392 | 0.294 | 0.588 | −261.96 |
| LSTM | 0.879 | 0.482 | 0.417 | 0.571 | 0.832 |
| GNN (GraphSAGE) | 0.924 | 0.535 | 0.449 | 0.662 | 0.039 |
| TCN | 0.880 | 0.507 | 0.434 | 0.609 | 0.775 |

### The Latency-R² Contradiction (Key Finding)
- GNN **wins classification but fails regression** on the same unseen scenario; LSTM holds regression but worse at discrimination.
- Why: classification only needs the model to rank "is the cell busy" (above/below threshold) — neighbor aggregation generalizes this well. Numeric magnitude overfit to the UDP-burst shape it was trained on.
- **Honesty note:** quote both numbers (F1/ROC-AUC *and* the R² collapse) in any write-up/viva; quoting only classification overstates GNN reliability.

### Advance-Warning / Lead-Time (LSTM on UE_17)
| Statistic | Value |
|---|---|
| Events with advance warning | 116 / 129 (89.9%) |
| Mean advance notice | 0.91 s |
| Max advance notice | 1.00 s (capped by 10-bin/1s horizon) |
| ≥ 0.5 s advance | 94.0% of warned events |
| ≥ 1.0 s advance | 68.1% of warned events |

Warnings arrive near the max possible lead time — model uses its full horizon. Moderate false alarms are the cost of a high-recall early-warning design.

### Throughput Wall (data issue, not model issue)
All three deep models cap at Total_Throughput R² ≈ 0.22–0.24 with unrelated architectures — strong evidence the problem is in the **feature/label design**: Total_Throughput behaves like a **cumulative counter**, not a per-bin rate.

### Recommended Next Steps (from doc)
- Report classification numbers and R² caveat honestly.
- Add a 3rd realistic test scenario.
- Try hybrid GNN→LSTM model.
- Replace fixed sigmoid with learned calibration (Platt/isotonic).
- Extend lead-time analysis to GNN and more UEs than UE_17.

---

## 3. Simulation_Impact_Analysis.docx

Asks: **how much would scores move if fed real-network data instead of Simu5G output?**

### What the Simulation Stack Represents
- OMNeT++ = discrete-event simulator; Simu5G = 3GPP-inspired NR stack (PHY, MAC, RLC, PDCP, scheduler); INET = transport/mobility/network layers.
- Simu5G PHY is largely **analytic**: SINR from path-loss/interference formulas → CQI via lookup tables (no waveform simulation). Scheduler/HARQ are reference implementations, not vendor stacks.
- Trade-off: exact, noise-free ground truth (great for labeled training data) vs one abstraction layer removed from physical radio measurement.

### Sensitivity Ranking (Table 1) — most to least concerning
| Factor | Est. Sensitivity |
|---|---|
| Traffic pattern realism (hand-designed synthetic shapes) | **HIGH** — GNN latency R² dropped 0.969→0.039 purely from a scenario shift *inside the simulator* |
| Feature set completeness (8 KPIs only) | **HIGH** — throughput ceiling (R²≈0.22) already proves the 8-feature set is insufficient even in-sim |
| Channel / propagation model (analytic) | MEDIUM-HIGH |
| Ground-truth label quality (noise-free in sim) | MEDIUM-HIGH |
| Scheduler / MAC implementation | MEDIUM — HARQ/RLC delay are direct scheduler outputs |
| Cell topology / graph structure | HIGH for GNN specifically — likely root cause of regression collapse |
| Time granularity (100ms bins) | MEDIUM — known cap on lead time |
| Congestion label (percentile, not SLA-anchored) | MEDIUM |
| Mobility model / UE count / cell count | **UNDETERMINED** — not documented in source report |

### What the Work Already Gets Right
- Cross-scenario evaluation (genuine generalization test).
- StandardScaler fit on training data only (no leakage).
- 5 architecturally distinct models on identical data — isolates architecture vs pipeline effects.
- GNN threshold miscalibration caught via systematic sweep.
- The GNN contradiction investigated and explained, not left as anomaly.

### Gap List (Not Yet Done)
- No real-network trace used for calibration/sanity-check.
- Only 2 synthetic traffic shapes; no mixed/heterogeneous traffic.
- Channel & scheduler fixed to Simu5G defaults — no sensitivity runs.
- GNN graph static & fully-connected within cell; no weighted/multi-cell variant.
- Mobility, UE density, cell count undocumented.
- Congestion label is a statistical percentile, not an SLA threshold.
- No measurement-noise model on labels.

### Recommended Future Steps
- **Simulation side:** diversify traffic scenarios; vary channel/scheduler configs; scale up topology (multi-cell, handovers) with explicit UE/cell counts; inject synthetic measurement noise.
- **Modeling side:** SINR/distance-weighted GNN edges; fix the throughput label (true per-bin rate); end-to-end classification objective; domain randomization.
- **Bridging to deployment:** small real-trace validation set (eval-only); fine-tune simulation-trained models; add learned calibration layer (Platt/isotonic) for graceful uncertainty degradation.

### Conclusion
Defensible framing for write-up/viva: *"these results are a rigorous measurement of relative model performance under a specific, documented simulation configuration; the two highest-leverage next steps are (1) fixing the Total_Throughput label design, which caps every model, and (2) validating against even a small real-network trace."*
