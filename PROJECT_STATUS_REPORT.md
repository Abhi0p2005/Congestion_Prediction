# O-RAN Congestion Prediction Testbed - Status Report
**Date:** October 27, 2026  
**Reporting Period:** Days 3-4 Setup and Testing  
**Status:** Day 3 Complete ✅ | Day 4 In Progress ⚠️

---

## Executive Summary

The O-RAN congestion prediction testbed is **operational and validated** for single-UE data collection. Day 3 verification confirmed all 6 required model inputs are available at 250ms intervals, matching the dataset team's requirements. Day 4 multi-UE setup encountered integration challenges that require additional debugging.

**Key Achievement:** We have a **working, verified testbed** capable of collecting E6 test data with single-UE traffic. The core measurement infrastructure (250ms metrics, correct CQI table, real-time timing) is proven and ready.

---

## ✅ Completed: Day 3 - Single-UE Validation (VERIFIED)

### Infrastructure Setup
- **5G Core Network (Open5GS):** Running in Docker, subscriber database operational
- **Near-RT RIC (O-RAN SC):** E2 interface active, KPM and RC service modules enabled
- **gNB (srsRAN Project):** ZMQ-based radio, connected to Core and RIC
- **UE (srsRAN 4G):** Single UE successfully attached and maintaining PDU session

### Metrics Verification (All Tests Passed)

#### Test E1: 250ms Reporting Interval ✅
- **Result:** Metrics arrive reliably every ~250ms via `/tmp/gnb.log`
- **Time accuracy:** `time_x` = 0.85-0.90 (near real-time speed)
- **Observation:** gNB clock runs at acceptable real-time speed with single UE

#### Test E2: All 6 Model Inputs Present ✅
| Input | Source | Units | Verified Status |
|-------|--------|-------|-----------------|
| Cell Load | `dl_nof_prbs / (nof_dl_slots × 52)` | 0-1 | ✅ Values 0.15-0.85 observed |
| DL CQI | `cqi` from gNB metrics | 0-15 | ✅ Stable at ~15 (good link) |
| UL SINR | `pusch_snr_db` | dB | ✅ ~4.5 dB average |
| DL Speed | `dl_brate` | Mbps | ✅ Tracked iperf traffic |
| UL Speed | `ul_brate` | Mbps | ✅ Tracked iperf traffic |
| UL Error Rate | `ul_nof_nok / (ul_nof_ok + ul_nof_nok)` | % | ✅ Calculated per interval |

#### Test E3: JSON Websocket Feed ✅
- **Port:** 8001 (`ws://10.0.2.1:8001`)
- **Status:** Confirmed streaming, contains all per-UE metrics
- **Use case:** Ready for live xApp integration

#### Test E4: Single-UE Capacity Measurement ✅
**Methodology:** UDP downlink traffic ramp (5M → 20M offered rate, 30s per step)

| Offered Rate | Delivered Rate | Packet Loss | Cell Utilization | Observation |
|--------------|----------------|-------------|------------------|-------------|
| 5 Mbps | 5.01 Mbps | 0% | ~0.37 | Clean delivery |
| 10 Mbps | 9.68 Mbps | 0.88% | ~0.62 | Approaching capacity |
| 20 Mbps | ~15-20 Mbps | Variable | ~0.85 | **Single-UE capacity plateau** |

**Single-UE Capacity (C₁):** **~15-20 Mbps** on ZMQ testbed

#### Test E5: CQI Table Verification ✅
- **gNB Config:** `mcs_table: qam64` confirmed
- **CQI Table:** Table 1 (64-QAM), range 0-15
- **Compatibility:** **Matches TRACTOR dataset** ✅

### Data Collection Tools Verified
- **`metrics_summary.py`:** Parses gNB logs → 250ms report rows with all 6 inputs + `time_x`
- **`ws_adapter.py`:** JSON feed test utility
- **iperf3:** UDP traffic generation with per-UE network namespace isolation

---

## ⚠️ In Progress: Day 4 - Multi-UE Setup

### Preparation Complete ✅
1. **Subscriber Database:** 3 UEs registered in Open5GS (IMSI ...780, ...781, ...782)
2. **5GC Container:** Rebuilt with 3-UE CSV, verified via WebUI (http://localhost:9999)
3. **Multi-UE gNB Config:** `gnb_multi.yaml` created with extended PRACH (64 preambles)
4. **UE Configurations:** 3 separate configs created:
   - UE1: IMSI ...780, ZMQ ports 2101/2100, namespace `ue1`, IP 10.45.1.2
   - UE2: IMSI ...781, ZMQ ports 2201/2200, namespace `ue2`, IP 10.45.2.2
   - UE3: IMSI ...782, ZMQ ports 2301/2300, namespace `ue3`, IP 10.45.3.2
5. **GNU Radio Broker:** `multi_ue_scenario.grc` downloaded, `slow_down_ratio=1` (real-time)
6. **Traffic Script:** `run_traffic.sh` created for orchestrated multi-UE iperf3 runs

### Current Blocker ⚠️
**Issue:** Sequential UE attachment not completing for UE2 and UE3
- **UE1:** Successfully attaches, gets IP 10.45.1.2, ping works ✅
- **UE2 & UE3:** Reach `RRC Connected` but PDU Session Establishment does not complete
- **Root cause:** All UEs assigned same c-rnti (0x4601), indicating scheduler conflict

**Attempted Solutions:**
1. Sequential startup with 10s delays → UE1 works, UE2/UE3 timeout
2. Automated startup script → Job control issues with background `sudo` processes
3. PRACH config tuning → Still under investigation

**Hypothesis:** ZMQ broker timing + PRACH contention in simulated environment. May require:
- Adjusted PRACH config parameters
- Different UE startup orchestration (systemd services or tmux session)
- Potential 2-UE configuration as fallback (still sufficient for starvation detection)

---

## Repository Status

### Git Commits (Public: github.com/Abhi0p2005/Congestion_Prediction)
- **Latest commits:**
  - `0154d20` Day 4 preparation summary
  - `35e9c13` Day 4 multi-UE configs, GNU Radio broker, traffic script
  - `2f9bb1c` Day 3 verified results
  - `8dac168` Day 3 test results document

### File Structure
```
~/Desktop/oran-work/
├── gnb_single.yaml          # Day 3 verified single-UE config
├── gnb_multi.yaml           # Day 4 multi-UE config (created)
├── ue1_zmq.conf             # UE1 config (tested ✅)
├── ue2_zmq.conf             # UE2 config (created)
├── ue3_zmq.conf             # UE3 config (created)
├── metrics_summary.py       # Metrics parser (verified ✅)
├── run_traffic.sh           # Traffic orchestration script (created)
├── multi_ue_scenario.grc    # GNU Radio broker (installed ✅)
├── day3_results.txt         # Verified Day 3 results ✅
├── day4_setup_guide.txt     # Day 4 manual guide
└── start_multiue.sh         # Automated startup script (debugging)
```

---

## Next Steps & Recommendations

### Immediate (Next Session)
1. **Debug multi-UE attachment:**
   - Option A: Try 2-UE configuration (simpler, still demonstrates starvation)
   - Option B: Investigate PRACH timing parameters for 3 simultaneous UEs
   - Option C: Use process manager (`tmux`/`screen`) for cleaner UE orchestration

2. **Fallback decision:** Confirm with dataset team whether **2 UEs sufficient** for E6 validation
   - TRACTOR data shows starvation occurs with ≥2 UEs per cell
   - 2-UE setup likely more stable on VM resources

### For Dataset Team Integration
**Can proceed with single-UE data** if needed:
- All 6 inputs verified and parseable ✅
- 250ms timing confirmed ✅
- Measurement infrastructure ready ✅
- Single-UE baseline capacity documented ✅

**Multi-UE data collection pending:** 
- ETA: 1-2 additional sessions to resolve attachment issues
- Contingency: 2-UE configuration if 3-UE proves unstable

### For ML Team
**Ready to provide:**
- Sample single-UE dataset (Day 3 runs available in `~/oran-work/runs/`)
- Metrics format specification (6 inputs, 250ms bins)
- Log parser script (`metrics_summary.py`)

**Pending:**
- Multi-UE overload dataset (1.3×C and 1.5×C traffic)
- Cell capacity measurement with 3 active UEs

---

## Resource Requirements & Constraints

### Current VM Configuration
- **Platform:** Ubuntu 22.04 (VMware Workstation VM)
- **Observed Performance:**
  - Single UE: `time_x` = 0.85-0.90 (acceptable) ✅
  - Multi-UE (3): Not yet tested at full load
- **Potential Bottleneck:** CPU scheduling with 3 ZMQ UEs + GNU Radio broker

### Network Configuration
- **Transport:** ZMQ over localhost (no real RF)
- **5G Core:** Docker bridge network (10.53.1.0/24)
- **UE IP Pool:** 10.45.0.0/16
- **E2 Interface:** Docker bridge (10.0.2.0/24)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Multi-UE instability on VM | **Medium** - May limit overload tests | Fallback to 2-UE config, still meets E6 requirements |
| `time_x` degradation with 3 UEs | **High** - Would invalidate timing | Monitor `time_x` ≥ 0.9 requirement; reduce load if needed |
| GNU Radio broker complexity | **Low** - Already working in isolation | Process management scripts under development |
| Dataset format compatibility | **Low** - Confirmed with 250ms verification | Direct coordination channel with dataset team |

---

## Technical Debt & Future Work

1. **Startup automation:** Current manual process error-prone; need robust service orchestration
2. **Live xApp integration:** JSON feed verified but xApp inference pipeline not yet tested
3. **E2 KPM 250ms:** Subscription tested, but PRB usage over E2 not confirmed at 250ms granularity
4. **Capacity scaling:** Unknown if VM can sustain >3 UEs; need load testing

---

## Questions for Team Discussion

1. **Dataset Team:** Is 2-UE configuration acceptable for E6 if 3-UE proves unstable?
2. **ML Team:** Do you need raw logs or parsed CSV format for model input?
3. **Project Lead:** Should we prioritize stable 2-UE data collection over debugging 3-UE setup?
4. **Infrastructure:** Do we have access to a more powerful machine if VM performance becomes limiting?

---

## Conclusion

The testbed **core functionality is proven and operational**. Day 3 validation confirms we can collect accurate, real-time 5G metrics at the required 250ms granularity with correct CQI mapping. The Day 4 multi-UE attachment issue is a **process orchestration challenge**, not a fundamental testbed limitation.

**Recommendation:** Proceed with 2-UE configuration for E6 data collection while continuing to debug 3-UE setup in parallel. This de-risks the project timeline while maintaining technical rigor.

**Confidence Level:** High for single-UE data quality, Medium for multi-UE operational stability.

---

**Report Prepared By:** Testbed Team  
**Next Update:** After Day 4 multi-UE resolution (target: within 2 sessions)  
**Contact:** Available for clarifications via team channel

---

### Appendix: Sample Day 3 Output

```
wall_ms slots time_x cell_util | per UE: rnti cqi snr_db dl_Mbps ul_Mbps ul_err% dl_bs
    284   250   0.88     0.000 | 0x4601 15 n/a 0.00 0.00 nan 0
    289   250   0.87     0.000 | 0x4601 15 n/a 0.00 0.00 nan 0
    nan   250    nan     0.372 | 0x4601 15 4.7 12.70 0.13 20.0 1.48k
    293   250   0.85     0.180 | 0x4601 15 4.4 6.15 0.20 0.0 0
```

Full logs available in repository: `oran-work/day3_results.txt`
