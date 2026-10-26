# Analysis: Wrong Code Found

**Date:** October 24, 2026  
**File:** `/home/oran/kpm_logger_xapp.py`

---

## ❌ Problems Identified

### 1. Wrong Reporting Interval
```python
self.e2sm_kpm.subscribe_report_service_4(
    e2_node_id, 1000, conds, METRICS, 1000, self.cb)
    #           ^^^^ 1000ms = 1 second (WRONG)
```
**Required:** 250ms intervals for E6 experiment

---

### 2. Wrong Labeling Approach
```python
p.add_argument("--label", default="normal")
self.label = label
row = [ts, ue_id, self.label]
```
**Problem:** Uses manual "normal" vs "congested" labels

**Required:** Calculate starvation label from delivered÷offered formula:
```python
starved = (delivered_bytes / offered_bytes) < 0.5
```

---

### 3. Wrong Metrics Set
```python
METRICS = ["DRB.UEThpDl", "DRB.UEThpUl",
           "DRB.RlcSduTransmittedVolumeDL", "DRB.RlcSduTransmittedVolumeUL",
           "DRB.RlcPacketDropRateDl", "DRB.PacketSuccessRateUlgNBUu"]
```
**Problem:** Only 2 relevant metrics (throughput), others don't map to dataset schema

**Required 6 measurements:**
1. Cell load (PRB usage)
2. DL CQI
3. UL SINR
4. DL Speed (Mbps)
5. UL Speed (Mbps)
6. UL Error Rate (%)

---

### 4. Wrong Data Source
**Problem:** Collects from E2SM-KPM subscription (1-second E2 reports)

**Required:** Parse gNB JSON metrics at 250ms intervals with fields:
- `cqi`
- `pusch_snr_db`
- `dl_brate`
- `ul_brate`
- `ul_nof_ok`, `ul_nof_nok`
- `dl_bs`

---

### 5. Breaks E6 Zero-Shot Test
**Problem:** This code was intended for training on testbed data

**Critical Issue:** E6 is a **test set only**. Training on our testbed data invalidates the sim-to-reality transfer claim. The dataset team trains on simulation (E1-E5), and E6 proves their model works on unseen live hardware.

---

## ✅ Corrected Approach

### Data Collection Method
1. Enable JSON metrics in `gnb_zmq.yaml`: `enable_json: true`, `du_report_period: 250`
2. Parse JSON output from gNB stderr (not E2 subscription)
3. Extract 6 measurements per UE every 250ms
4. Track offered traffic from iperf settings
5. Calculate delivered from actual throughput
6. Apply label formula: `starved = delivered/offered < 0.5`
7. Output in dataset team's exact CSV schema

### Our Role
- Collect E6 data only (don't train)
- Match dataset team's schema exactly
- Provide zero-shot test set for their trained models
- Measure sim-to-reality transfer gap

---

## 🗑️ Action Required

**Delete this file from VM:**
```bash
rm ~/kpm_logger_xapp.py
```

**Use corrected collector instead:**
- `testbed_collector.py` (being created in phase2_corrected/scripts/)

---

## 📋 Summary

| Aspect | Wrong (kpm_logger_xapp.py) | Correct (Phase 2 approach) |
|--------|---------------------------|---------------------------|
| Interval | 1000ms (1 second) | 250ms |
| Label | Manual "normal/congested" | delivered÷offered < 0.5 |
| Metrics | 6 E2SM-KPM metrics | 6 dataset-schema measurements |
| Source | E2 subscription | gNB JSON metrics |
| Purpose | Training on testbed | E6 test set collection |

**Status:** Wrong code identified. Corrected implementation in progress.
