# Phase 2: E6 Data Collection - Implementation Guide

**Date:** October 24, 2026  
**Status:** Ready for implementation  
**Your Role:** Collect E6 test data (not training)

---

## 🎯 Quick Start

All corrected files are in: `C:\College\Project\5G\phase2_corrected\`

### Files Created

#### Configs (`configs/`)
- ✅ `gnb_zmq_corrected.yaml` - 250ms intervals + JSON enabled
- ✅ `ue1_zmq.conf` - UE1 (IMSI: ...780, ports 2000/2001)
- ✅ `ue2_zmq.conf` - UE2 (IMSI: ...781, ports 2002/2003)
- ✅ `ue3_zmq.conf` - UE3 (IMSI: ...782, ports 2004/2005)

#### Scripts (`scripts/`)
- ✅ `testbed_collector.py` - Dataset schema-compliant collector
- ✅ `run_step1.sh` - Verify 250ms reporting
- ✅ `run_step2.sh` - Confirm CQI table
- ✅ `run_step6.sh` - Collect 10-min validation sample

#### Documentation (`docs/`)
- ✅ `ANALYSIS_WRONG_CODE.md` - Why kpm_logger_xapp.py is wrong

---

## 📋 Implementation Steps

### Step 0: Copy Files to VM (5 minutes)

**From Windows, copy the phase2_corrected folder to Ubuntu Desktop:**

1. Drag `C:\College\Project\5G\phase2_corrected\` to Ubuntu VM Desktop
2. Or manually copy files one by one

**In Ubuntu VM terminal:**
```bash
# Copy corrected configs
cp ~/Desktop/phase2_corrected/configs/gnb_zmq_corrected.yaml ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
cp ~/Desktop/phase2_corrected/configs/ue1_zmq.conf ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf
cp ~/Desktop/phase2_corrected/configs/ue2_zmq.conf ~/
cp ~/Desktop/phase2_corrected/configs/ue3_zmq.conf ~/

# Copy scripts
cp ~/Desktop/phase2_corrected/scripts/testbed_collector.py ~/
cp ~/Desktop/phase2_corrected/scripts/run_step1.sh ~/
cp ~/Desktop/phase2_corrected/scripts/run_step2.sh ~/
cp ~/Desktop/phase2_corrected/scripts/run_step6.sh ~/

# Make scripts executable
chmod +x ~/*.sh
chmod +x ~/testbed_collector.py

# Delete wrong code
rm ~/kpm_logger_xapp.py

echo "✓ Files copied and wrong code deleted"
```

---

### Step 1: Verify 250ms Reporting (30 min)

**Run automated script:**
```bash
cd ~
./run_step1.sh
```

**What it does:**
1. Verifies gnb_zmq.yaml has correct settings
2. Guides you through starting testbed (4 terminals)
3. Generates traffic and collects 1-min sample
4. Validates required fields exist
5. Creates `~/step1_sample_250ms.json`

**Deliverable:** 
- `step1_sample_250ms.json` (copy to Windows Desktop, send to dataset team)

---

### Step 2: Confirm CQI Table (15 min)

**Run automated script:**
```bash
cd ~
./run_step2.sh
```

**What it does:**
1. Checks config for qam64 settings
2. Analyzes Step 1 sample for CQI values
3. Verifies CQI range is 0-15 (correct)
4. Creates `~/step2_cqi_verification.txt`

**Deliverable:**
- `step2_cqi_verification.txt` (copy to Windows Desktop, send to dataset team)

**⏸️ WAIT FOR DATASET TEAM VALIDATION BEFORE STEP 3**

---

### Step 3: Setup 3 UEs (2-3 hours)

**Note:** Multi-UE with ZMQ is complex. Dataset team may accept 2 UEs or 1 UE.

**Register UE2 and UE3 in core:**
1. Open http://localhost:9999 (admin / 1423)
2. Add subscribers:
   - IMSI: `001010123456781`, K: `00112233445566778899aabbccddeeff`, OPC: `63bfa50ee6523365ff14c1f45f88737d`
   - IMSI: `001010123456782`, K: `00112233445566778899aabbccddeeff`, OPC: `63bfa50ee6523365ff14c1f45f88737d`

**Attempt multi-UE:**
```bash
# Terminal 4: UE1
sudo ip netns add ue1
cd ~/srsRAN_4G/build/srsue/src
sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf

# Terminal 5: UE2 (may not work with ZMQ)
sudo ip netns add ue2
sudo ./srsue ~/ue2_zmq.conf

# Terminal 6: UE3 (may not work with ZMQ)
sudo ip netns add ue3
sudo ./srsue ~/ue3_zmq.conf
```

**If ZMQ multi-UE doesn't work:**
- Proceed with 1 UE only
- Document limitation
- Dataset team can still use data with adjusted schema

---

### Step 6: Collect 10-Min Validation Sample (15 min)

**Prerequisites:**
- Testbed running (Core, RIC, gNB with JSON, UE(s))
- Collector script copied

**Run automated script:**
```bash
cd ~
./run_step6.sh
```

**What it does:**
1. Starts testbed_collector.py in background
2. Runs traffic scenario:
   - 0-3 min: Light (2 Mbps/UE)
   - 3-6 min: Medium (10 Mbps/UE)
   - 6-10 min: Heavy (30 Mbps/UE - congestion)
3. Collects data in dataset team's schema
4. Analyzes starvation events
5. Creates `~/e6_sample_10min.csv`

**Deliverable:**
- `e6_sample_10min.csv` (~7200 rows, copy to Windows Desktop)

**Send to dataset team:**
```
Subject: E6 Sample Data - Ready for Validation

Completed Steps 1-6. Attached:
1. step1_sample_250ms.json (250ms metrics verification)
2. step2_cqi_verification.txt (CQI table confirmed as 64-QAM)
3. e6_sample_10min.csv (10-min sample in your schema)

Sample details:
- 3 UEs (or 1 if multi-UE failed) at 250ms intervals
- Light/medium/heavy load periods
- ~7200 rows
- Starvation events detected during heavy load

Please run tests.py validation. Ready for full E6 collection once approved.
```

**⏸️ WAIT FOR DATASET TEAM FINAL VALIDATION**

---

## 🚀 After Validation: Full E6 Collection

Once dataset team approves the sample:

```bash
# Collect full E6 dataset (multiple scenarios, 1-2 hours)
# Light load scenario (30 min)
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py ~/e6_light.csv --rates ue1=2M,ue2=2M,ue3=2M

# Medium load scenario (30 min)
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py ~/e6_medium.csv --rates ue1=10M,ue2=10M,ue3=10M

# Heavy load scenario (30 min)
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py ~/e6_heavy.csv --rates ue1=30M,ue2=30M,ue3=30M

# Combine and send to dataset team
cat e6_light.csv > e6_full_dataset.csv
tail -n +2 e6_medium.csv >> e6_full_dataset.csv
tail -n +2 e6_heavy.csv >> e6_full_dataset.csv
```

---

## 🔧 Troubleshooting

### Problem: Multi-UE doesn't work
**Solution:** Proceed with 1 UE, document limitation, dataset team can still use data

### Problem: No JSON metrics output
**Check:** `enable_json: true` in gnb_zmq.yaml line 88
**Check:** gNB started with `2>&1 | tee /tmp/gnb_metrics.json`

### Problem: Collector fails with "rate not specified"
**Solution:** Always use `--rates` parameter: `--rates ue1=5M,ue2=5M,ue3=5M`

### Problem: Testbed stopped working
**Solution:** Restart from scratch following RUN_GUIDE.md, wait 60s between gNB restarts

---

## 📊 Expected Timeline

| Phase | Duration | Wait Time |
|-------|----------|-----------|
| Step 0: Copy files | 5 min | - |
| Step 1: 250ms verify | 30 min | - |
| Step 2: CQI verify | 15 min | - |
| **WAIT: Dataset approval** | - | 1-24 hours |
| Step 3: Multi-UE | 2-3 hours | - |
| **WAIT: Dataset approval** | - | 1-24 hours |
| Step 6: 10-min sample | 15 min | - |
| **WAIT: Final validation** | - | 1-24 hours |
| Full E6 collection | 1-2 hours | - |

**Total implementation time:** 4-5 hours (excluding waits)  
**Total project time:** 3-5 days (with dataset team checkpoints)

---

## ✅ Success Criteria

- [x] Config corrected (250ms, JSON enabled, qam64)
- [x] Wrong code identified and deleted
- [x] Collector script matches dataset schema exactly
- [x] Step scripts automate validation process
- [ ] Step 1-2 validated by dataset team
- [ ] 10-min sample passes tests.py
- [ ] Full E6 dataset collected
- [ ] Dataset team runs E6 experiment
- [ ] Sim-to-reality transfer measured

---

## 📞 Support

**If stuck:**
1. Check RUN_GUIDE.md for testbed startup
2. Check PHASE2_E6_GUIDE.md for detailed step explanations
3. Check ANALYSIS_WRONG_CODE.md for what not to do

**Dataset team communication is critical:**
- Always wait for validation before proceeding
- Send deliverables after each checkpoint
- Document any deviations (e.g., 1 UE instead of 3)

---

**You're ready to start! Begin with Step 0 (copy files to VM).**
