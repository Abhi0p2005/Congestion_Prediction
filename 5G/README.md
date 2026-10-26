# O-RAN Congestion Prediction: Simulation-to-Reality Transfer
## Dataset Team + Testbed Team Integration

**Last Updated:** October 18, 2026  
**Status:** Infrastructure Complete ✅ | E6 Data Collection Starting  
**Project:** Validate sim-to-reality transfer on live O-RAN testbed

---

## 🎯 Project Goal

**Prove that a congestion predictor trained on simulated data works on a real O-RAN network.**

### Two-Team Approach

**Dataset Team (Friend):**
- ✅ Repaired OMNeT++/Simu5G simulator
- ✅ Prepared TRACTOR real O-RAN dataset  
- ✅ Created 5 experiment datasets (E1-E5)
- ⏳ Training models on simulation data
- ⏳ Will test trained model on our testbed data (E6)

**Testbed Team (Us):**
- ✅ Built live O-RAN stack (Core + RIC + gNB + UE)
- ✅ Verified E2 interface (monitoring + control)
- ⏳ **Collecting E6 test data** (our only job)
- ⏳ Will deploy dataset team's trained model
- ⏳ Will measure real-world performance

---

## ⚠️ Critical Clarification: Our Role

### We Do NOT:
- ❌ Train models (dataset team does this on their simulation data)
- ❌ Create features or labels (dataset team's specification)
- ❌ Decide the schema (dataset team defined it)

### We DO:
- ✅ Collect **E6 test data** at 250ms intervals
- ✅ Match dataset team's **6 measurements + label schema**
- ✅ Provide **zero-shot test set** (unseen by their training)
- ✅ Deploy their trained model and measure performance

**Key Point:** Our testbed data is the **E6 experiment** - the final test proving sim-to-reality transfer works on real hardware.

---

## 📊 The Experiments (Dataset Team)

| Exp | Train On | Test On | Question |
|-----|----------|---------|----------|
| **E1** | Simulator | Simulator (held-out) | Does model work? (sanity check) |
| **E2** | Simulator | TRACTOR real data | Does it transfer? (primary result) |
| **E3** | Sim + 5/10/20% real | TRACTOR real | How much real data helps? |
| **E4** | TRACTOR real | TRACTOR real | Upper bound (best possible) |
| **E5** | 4-6 users | 9-10 users | Does it extrapolate to high load? |
| **E6** | Simulator | **Our testbed** | Does it work on live hardware? |

**E6 is our contribution:** Independent validation that sim-trained model works on different hardware/setup.

---

## 🔬 Six Shared Measurements (The Bridge)

**These measurements exist in simulation, TRACTOR, and our testbed:**

| # | Measurement | Purpose | Our Source (E2SM-KPM) | Units |
|---|-------------|---------|----------------------|-------|
| 1 | **Cell Load** | Is cell saturated? | PRB usage / 12,500 | 0-1 |
| 2 | **DL CQI** | Link quality? | `cqi` from gNB JSON | 0-15 |
| 3 | **UL SINR** | Uplink quality? | `pusch_snr_db` | dB |
| 4 | **DL Speed** | Download rate? | `dl_brate` | Mbps |
| 5 | **UL Speed** | Upload rate? | `ul_brate` | Mbps |
| 6 | **UL Error Rate** | Wasted capacity? | `ul_nof_nok / (ok+nok)` | % |

**Reported every:** 250 milliseconds  
**Prediction window:** 10 timesteps (2.5 seconds)  
**Prediction target:** Onset of starvation 1 second ahead (4 intervals)

---

## 📐 Congestion Label Definition

**Universal across all sources (simulation, TRACTOR, our testbed):**

### Starvation (per UE, per 250ms interval):
```
starved = (delivered_bytes / offered_bytes) < 0.5
```

- **Delivered:** What UE actually received
- **Offered:** What UE requested/needed
- **Threshold:** Less than half = starved

### Onset (the prediction target):
```
onset_at_t = NOT starved(t) AND starved(t + 1 second)
```

**Why onset?** Starvation persists (72% still starved 1s later), so predicting onset catches **when congestion begins**.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Dataset Team: Model Training (OMNeT++ & TRACTOR)          │
│                                                              │
│  Simulation (485K intervals) ─┐                            │
│  TRACTOR Real (601K intervals)─┼──► Train Models ──► Best  │
│                                │   (LSTM/TCN/Graph)   Model │
│                                │                      (.h5) │
└────────────────────────────────┼──────────────────────────┘
                                 │ Transfer to Testbed
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Testbed Team: E6 Validation (Live O-RAN Hardware)         │
│                                                              │
│  ┌────┐ ZMQ  ┌──────┐ N2   ┌──────┐                        │
│  │ UE │◄────►│ gNB  │◄────►│ Core │                        │
│  │ x3 │ 2000 │(srsRAN)│10.53│(5GC) │                        │
│  └────┘ 2001 └───┬──┘ 1.2  └──────┘                        │
│                  │ E2 (250ms)                               │
│                  ▼                                           │
│         ┌─────────────────┐                                 │
│         │ RIC (10.0.2.10) │                                 │
│         │  • E2 Term      │                                 │
│         │  • Collector    │                                 │
│         │  • Trained Model│                                 │
│         └─────────────────┘                                 │
│                                                              │
│  Output: e6_testbed_data.csv (our contribution)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Current Status

### ✅ Days 1-2 Complete (Go/No-Go Checkpoint Passed!)
- Infrastructure: Core + RIC + gNB + UE working
- E2 interface: KPM monitoring verified
- E2 control: RC xApp adjusts PRB quota successfully
- Network: UE gets IP, ping works, throughput tested

**This was the risky part - it's done!**

### ⏳ Phase 2: E6 Data Collection (6 Steps)

**Next immediate steps:**

| Step | Task | Status | ETA |
|------|------|--------|-----|
| 1 | Verify 250ms KPM reporting | Ready | 30 min |
| 2 | Confirm CQI table (64-QAM) | Ready | 15 min |
| 3 | Setup 3 UEs | Pending | 1-2 hours |
| 4 | Measure max cell throughput | Pending | 1 hour |
| 5 | Build collector (dataset schema) | Pending | 1 hour |
| 6 | Collect 10min sample → validate | Pending | 30 min |

**After validation:** Full E6 data collection (various scenarios, 1-2 hours)

---

## 📁 Project Structure

```
5G-ORAN-Congestion-Prediction/
├── docs/
│   ├── SETUP_GUIDE.md              # Days 1-2 infrastructure setup
│   ├── RUN_GUIDE.md                # Daily testbed startup
│   ├── PHASE2_E6_GUIDE.md          # Next steps (6-step process)
│   ├── TRANSFER_GUIDE.md           # Share project with others
│   └── extracted_report.txt        # Dataset team's Stage 1 report
│
├── configs/
│   ├── gnb_zmq_simple.yaml         # Backup gNB config
│   └── ue_zmq_simple.conf          # Backup UE config
│
├── scripts/
│   ├── ubuntu_setup.sh             # Automated testbed setup
│   ├── check_environment.ps1       # Windows env checker
│   ├── fix_ric_build.sh            # RIC Docker build fix
│   └── extract_doc.py              # Extract Word docs
│
├── dataset_reports/                # From dataset team
│   ├── 5G_report_midsem.docx       # Stage 1 complete report
│   ├── Model_Comparison_Report.docx # Model analysis
│   └── docs_summary.md             # Reference
│
└── README.md                        # This file
```

---

## 🚀 Quick Start (Tomorrow)

### Morning: Steps 1-2 (Setup Verification)

```bash
# 1. Start testbed (follow RUN_GUIDE.md)
# 6 terminals: Core → RIC → gNB → UE → Routes → Traffic

# 2. Modify gNB config for 250ms reporting
cd ~/oran-sc-ric/e2-agents/srsRAN
nano gnb_zmq.yaml
# Change: du_report_period: 250 (from 1000)
# Enable: enable_json: true

# 3. Restart gNB and check metrics
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json

# 4. Verify 250ms intervals
tail -f /tmp/gnb_metrics.json | grep timestamp

# 5. Check required fields exist
grep -A 50 '"ue_container"' /tmp/gnb_metrics.json | head -60

# 6. Send sample to dataset team for validation
head -300 /tmp/gnb_metrics.json > step1_sample_250ms.json
# Email: "Step 1 complete, please verify fields"
```

**WAIT for dataset team confirmation before proceeding!**

### Afternoon: Steps 3-4 (Multi-UE & Capacity)

```bash
# Only after Steps 1-2 validated:

# Setup 3 UEs (follow PHASE2_E6_GUIDE.md Step 3)
# Run capacity test (Step 4)
# Document findings
# Send to dataset team

# WAIT for validation
```

### Evening: Steps 5-6 (Collector & Sample)

```bash
# Only after Steps 3-4 validated:

# Build proper collector matching their schema (Step 5)
# Collect 10-minute sample (Step 6)
# Send to dataset team for tests.py validation

# WAIT for final approval
```

### Next Day: Full E6 Collection

```bash
# Only after sample validated:

# Collect full E6 dataset
# Various scenarios: light, medium, heavy load
# Multiple runs with different patterns
# Send to dataset team

# They run E6 experiment (test trained model on our data)
# Compare with E4 results
# Measure sim-to-reality transfer success
```

---

## 🎯 Success Criteria

### Our Deliverables:
- ✅ Working testbed with E2 interface
- ⏳ E6 dataset in correct format (250ms, 6 measurements, label formula)
- ⏳ Multiple scenarios (light/medium/heavy load)
- ⏳ 3 UEs, various conditions
- ⏳ Data passes dataset team's validation (tests.py)

### Joint Success:
- 🎯 Model trained on simulation works on our testbed (E6 passes)
- 🎯 Performance gap (E6 vs E4) is measurable and explainable
- 🎯 Sim-to-reality transfer validated end-to-end
- 🎯 Results publishable (novel contribution)

### Metrics (Dataset Team Evaluates):
- Precision-Recall AUC > 0.60 on E6 data
- Recall (onset detection) > 70%
- False alarm rate < 5% on light load
- Inference time < 100ms (near-RT RIC constraint)

---

## 📖 Key Findings So Far

### From Dataset Team (Stage 1):
✅ **Simulator repairs complete:**
- 12 bugs fixed in OMNeT++/Simu5G
- Congestion now realistic: 0.9% (light) → 52.5% (heavy)
- 6 scenarios, 485,546 user-intervals

✅ **TRACTOR real data prepared:**
- 601,592 user-intervals, 188 users
- Starvation: 0% (1 user) → 48% (8 users)
- Episodes short: median 0.75s, 90% under 2.5s

✅ **Sim-to-Real gap measured BEFORE modeling:**
- Starvation prevalence: 34.1% (sim) vs 2.2% (real)
- Distribution gaps: 4 of 6 features differ significantly (KS 0.39-0.76)
- Only uplink SINR aligns well (KS 0.15)

**This sets the challenge:** Models must overcome these gaps to transfer.

### From Testbed Team (Us):
✅ **Infrastructure operational:**
- Full O-RAN stack working (Core, RIC, gNB, UE)
- E2 interface proven (KPM + RC verified)
- Can collect same 6 measurements as datasets

✅ **Control capability demonstrated:**
- PRB quota changes affect throughput
- 20 Mbps → 8 Mbps when quota reduced
- Recovery works when restored

✅ **Ready for E6 collection:**
- Know what measurements to collect
- Understand 250ms requirement
- Have label formula
- Testbed stable

---

## 🤝 Team Integration

### Dataset Team Responsibilities:
- ✅ Stage 1: Data preparation complete
- ⏳ Stage 2A: Train models (E1-E5 experiments)
- ⏳ Stage 2B: Validate our E6 sample
- ⏳ Stage 2C: Test trained model on full E6 data
- ⏳ Stage 2D: Analyze results, write report

### Testbed Team Responsibilities:
- ✅ Days 1-2: Infrastructure complete
- ⏳ Phase 2A: 6-step validation (Steps 1-6)
- ⏳ Phase 2B: Full E6 data collection
- ⏳ Phase 2C: Deploy trained model (if time permits)
- ⏳ Phase 2D: Contribute to final report

### Communication Protocol:
- **Before each step:** Confirm with dataset team
- **After each step:** Send results, wait for validation
- **Never proceed:** Without dataset team approval
- **Sample first:** Always validate before full collection

---

## 🛠️ Technical Specifications

### Hardware (Our Testbed):
- **Host:** Windows 10/11, VMware/VirtualBox
- **VM:** Ubuntu 22.04, 8GB RAM, 8 CPU cores
- **Network:** NAT, ZMQ virtual radio (ports 2000-2005)

### Software Stack:
- **gNB:** srsRAN Project release_25_10
- **UE:** srsRAN 4G release_23_11 (x3 instances)
- **Core:** Open5GS in Docker
- **RIC:** oran-sc-ric commit 621ade2

### Data Collection:
- **Interval:** 250 milliseconds
- **Measurements:** 6 (cell_util, dl_cqi, ul_sinr_db, dl_mbps, ul_mbps, ul_error_pct)
- **Label inputs:** offered_bytes, delivered_bytes
- **UEs:** 3 simultaneous
- **Scenarios:** Light, medium, heavy load

### Format (Dataset Team Schema):
```csv
timestamp,ue_id,cell_util,dl_cqi,ul_sinr_db,dl_mbps,ul_mbps,ul_error_pct,dl_buffer_bytes,offered_bytes,delivered_bytes
```

---

## 📚 Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Project overview | Both teams |
| **SETUP_GUIDE.md** | Days 1-2 setup | Us (reference) |
| **RUN_GUIDE.md** | Daily startup | Us (daily use) |
| **PHASE2_E6_GUIDE.md** | 6-step E6 collection | Us (next steps) |
| **TRANSFER_GUIDE.md** | Share project | Anyone |
| **extracted_report.txt** | Dataset team Stage 1 | Both teams |

---

## 🎓 References

### O-RAN Standards
- [E2SM-KPM Specification](https://www.o-ran.org/specifications) - Key Performance Measurement
- [O-RAN Architecture](https://www.o-ran.org/specifications) - Near-RT RIC

### Software
- [srsRAN Project](https://github.com/srsran/srsRAN_Project)
- [srsRAN 4G](https://github.com/srsran/srsRAN_4G)
- [oran-sc-ric](https://github.com/srsran/oran-sc-ric)
- [OMNeT++](https://omnetpp.org/) - Dataset team's simulator

### Datasets
- [TRACTOR](https://github.com/genesys-neu/TRACTOR) - Real O-RAN telemetry
- J. Groen et al., "TRACTOR: Traffic Analysis and Classification Tool for Open RAN," IEEE ICC, 2024

---

## 📞 Current Status Summary

**Date:** October 18, 2026, 8:06 PM  
**Milestone:** Go/No-Go Checkpoint Passed ✅  
**Next:** E6 Data Collection (6 steps)  
**Blocker:** None - ready to proceed

**Tomorrow's Plan:**
1. Start with Step 1 (250ms verification)
2. Send results to dataset team
3. Wait for validation
4. Proceed step-by-step with their approval

**Communication:**
- Daily updates to dataset team
- Validate at each checkpoint
- Sample before full collection
- Document everything

---

**Project Lead:** Testbed Team  
**Collaborator:** Dataset Team (Friend)  
**Supervisor:** Dr. Radhika Joshi  
**Institution:** COEP Technological University, Pune

**This is NOT a simulation project. This is a sim-to-reality validation project.** 🎯
