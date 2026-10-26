# SETUP COMPLETE - Day 3 Ready to Start
**Date:** October 26, 2026, 14:41 UTC  
**Status:** ✅ All files created and verified  
**Next Action:** Run setup checklist

---

## 🎉 What's Been Completed

### ✅ Files Created (7 total)

1. **~/oran-work/gnb_single.yaml** (5.5 KB)
   - 250ms reporting enabled (`du_report_period: 250`)
   - Log metrics enabled (`enable_log: true`)
   - JSON feed enabled (`enable_json: true`)
   - 64-QAM table configured (`mcs_table: qam64`)
   - Remote control websocket on port 8001

2. **~/oran-work/metrics_summary.py** (2.0 KB, executable)
   - Parses gNB log into 250ms report summaries
   - Shows: wall_ms, slots, time_x, cell_util, per-UE metrics

3. **~/oran-work/day3_setup_checklist.sh** (3.4 KB, executable)
   - Verifies all prerequisites
   - Checks dependencies (moreutils, python3, websocket-client)
   - Validates configuration settings
   - Confirms srsRAN installations

4. **~/oran-work/day3_test_guide.sh** (6.9 KB, executable)
   - Interactive guide for running Day 3 tests
   - Step-by-step terminal setup
   - Automated verification tests (E1-E4)
   - Capacity measurement automation

5. **~/oran-work/day3_results_template.txt** (3.0 KB)
   - Structured template for documenting findings
   - Tables for capacity test results
   - Checklists for each verification step

6. **~/oran-work/README.md** (8.2 KB)
   - Complete Day 3 guide
   - Troubleshooting reference
   - Success criteria
   - Command reference

7. **~/oran-work/runs/** (directory)
   - Ready for Day 4 test run storage

---

## 🔧 Configuration Verification

### gNB Config (gnb_single.yaml) ✓

```yaml
✓ du_report_period: 250     # 250ms intervals
✓ enable_log: true           # Primary data source
✓ enable_json: true          # For future live xApp
✓ mcs_table: qam64          # 64-QAM (matches TRACTOR)
✓ remote_control: enabled    # Websocket on port 8001
✓ all_level: warning         # Keep log small
```

All critical settings verified!

---

## 🚀 How to Start Day 3 (Right Now)

### Step 1: Verify Prerequisites (5 minutes)

Open a terminal and run:

```bash
cd ~/oran-work
./day3_setup_checklist.sh
```

**Expected output:**
```
✓ ~/oran-work/runs exists
✓ metrics_summary.py exists
✓ metrics_summary.py is executable
✓ gnb_single.yaml exists
✓ 250ms reporting enabled
✓ Log metrics enabled
✓ 64-QAM table configured
✓ Remote control (websocket) enabled
✓ moreutils (ts) installed
✓ python3 installed
✓ websocket-client installed
✓ srsRAN Project (gNB) found
✓ srsRAN 4G (UE) found
✓ oran-sc-ric found
✓ 5GC docker configs found

ALL CHECKS PASSED!
```

**If any checks fail:**
- `moreutils NOT installed` → Run: `sudo apt install -y moreutils`
- `websocket-client NOT installed` → Run: `pip3 install websocket-client`

---

### Step 2: Run Day 3 Tests (2-3 hours)

Once checklist passes, start the interactive test guide:

```bash
cd ~/oran-work
./day3_test_guide.sh
```

Or save full output:

```bash
cd ~/oran-work
./day3_test_guide.sh 2>&1 | tee day3_output.txt
```

The script will:
1. Guide you to open 5 terminals
2. Walk through starting: Core → RIC → gNB → UE
3. Verify connectivity
4. Run all verification tests (E1-E4)
5. Measure single-UE capacity
6. Generate results for documentation

---

### Step 3: Document Results (15 minutes)

After tests complete:

```bash
cp ~/oran-work/day3_results_template.txt ~/oran-work/day3_results.txt
nano ~/oran-work/day3_results.txt
```

Fill in the template with your actual measurements.

---

### Step 4: Send to Friend for Approval

Send these to your friend:
1. `~/oran-work/day3_results.txt` (completed)
2. Output from `metrics_summary.py` (sample from tests)
3. Capacity test findings
4. Any issues encountered

**Do NOT proceed to Day 4 without approval!**

---

## 📋 Quick Reference: What Gets Tested

| Test | Checks | Success Criteria |
|------|--------|------------------|
| **E1: 250ms metrics** | Reporting interval & timing | wall_ms≈250, time_x≈1.0, all 6 inputs visible |
| **E2: JSON feed** | Websocket metrics | JSON received on port 8001 |
| **E3: KPM 250ms** | E2 interface capability | Subscription works, check indication rate |
| **E4: Single-UE capacity** | Radio vs CPU bottleneck | Throughput plateaus with cell_util≈0.9-1.0 |
| **E5: CQI table** | 64-QAM confirmation | Config & observed CQI values 0-15 |

---

## ⚠️ Critical Success Criteria for Day 3

### Must Pass ✓
- [ ] `time_x` ≈ 1.0 throughout all tests (proves real-time)
- [ ] All 6 measurements visible in metrics output
- [ ] Single-UE capacity measured successfully
- [ ] `cell_util` reaches ~0.9-1.0 at saturation
- [ ] No CPU core pinned at 100% during capacity test

### Warning Signs ⚠️
- `time_x < 0.9` → CPU too slow, can't do 3 UEs
- `cell_util < 0.8` at throughput plateau → CPU bottleneck
- Missing measurements → config error

**If you see warning signs:** Document them and report to your friend BEFORE Day 4.

---

## 🔄 Backup Status

### Already Created:
- `/home/oran/Desktop/backups/backup_20261026_200723.tar.gz` (3.9M)
  - Contains: 5G/, phase2_corrected/, vm_export/, vm_shared/

### To Create Before Day 4:
```bash
cd /home/oran/Desktop
tar -czf backups/backup_before_day4_$(date +%Y%m%d_%H%M%S).tar.gz oran-work/
```

### To Restore if Needed:
```bash
cd /home/oran/Desktop/backups
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz
```

---

## 📊 Expected Timeline

| Activity | Time | Status |
|----------|------|--------|
| Setup verification | 5-10 min | Ready ✓ |
| Install any missing deps | 0-5 min | May be needed |
| Start 5 terminals | 10-15 min | Pending |
| Run E1-E3 tests | 20-30 min | Pending |
| Run E4 capacity test | 30-45 min | Pending |
| Document results | 15-30 min | Pending |
| **Total Day 3** | **~2-3 hours** | **Ready to start** |

---

## 🎯 What This Fixes From Before

### The Problem:
- Previous `kpm_logger_xapp.py` was **completely wrong**:
  - Used 1-second intervals (should be 250ms)
  - Used E2 subscription (should use gNB logs)
  - Manual labels (should calculate from formula)
  - Would have invalidated the E6 experiment

### The Solution (What You Have Now):
- ✅ Correct 250ms intervals from gNB log metrics
- ✅ Proper data source (log, not E2)
- ✅ Ready for proper label calculation (delivered/offered)
- ✅ E6 remains a pure test set (not contaminated by training)

---

## 📞 If You Get Stuck

### Common Issues & Fixes:

1. **Checklist fails on dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y moreutils python3-pip
   pip3 install websocket-client
   ```

2. **Can't execute scripts:**
   ```bash
   chmod +x ~/oran-work/*.sh
   ```

3. **gNB won't start:**
   - Check YAML indentation (spaces, not tabs)
   - Wait 60 seconds after stopping before restart

4. **UE won't attach:**
   - Make sure Core and RIC are fully started first
   - Check namespace: `sudo ip netns list`

5. **No metrics in /tmp/gnb.log:**
   - Verify gNB started with correct config: `-c ~/oran-work/gnb_single.yaml`
   - Check `enable_log: true` in config

---

## 🎓 Key Learnings & Context

### Why 250ms Matters:
- Dataset team's simulation uses 250ms bins
- TRACTOR real data uses 250ms bins
- Prediction window is 10 timesteps = 2.5 seconds
- E6 must match to be valid test set

### Why time_x Matters:
- Proves emulation runs at real speed
- If time_x < 1.0, timing is wrong
- Wrong timing → wrong labels → invalid data

### Why cell_util Matters:
- Proves radio saturation, not CPU bottleneck
- Real congestion needs radio overload
- CPU bottleneck would create fake congestion

### Your Role in E6:
- ❌ Don't train models (dataset team does)
- ✅ Do collect clean test data at 250ms
- ✅ Do measure real radio congestion
- ✅ Do provide zero-shot validation set

---

## 📂 File Locations Quick Reference

```
~/oran-work/                              # Main work directory
├── README.md                             # Full guide (this info)
├── gnb_single.yaml                       # Day 3 gNB config
├── metrics_summary.py                    # Parse gNB logs
├── day3_setup_checklist.sh              # Pre-flight checks
├── day3_test_guide.sh                   # Interactive testing
├── day3_results_template.txt            # Documentation template
└── runs/                                # For Day 4

~/oran-sc-ric/e2-agents/srsRAN/          # Original configs
├── gnb_zmq.yaml                         # Original (backup)
└── ue_zmq.conf                          # UE config

/tmp/gnb.log                             # gNB metrics output
/home/oran/Desktop/backups/              # Project backups
```

---

## ✅ Ready to Start!

Everything is prepared and verified. You can now:

1. **Start immediately:** `cd ~/oran-work && ./day3_setup_checklist.sh`
2. **Read the guide:** `cat ~/oran-work/README.md`
3. **Review configuration:** `cat ~/oran-work/gnb_single.yaml`

**Your next command:**
```bash
cd ~/oran-work && ./day3_setup_checklist.sh
```

---

## 📧 After Day 3 - What to Send

Your friend needs:
1. **Results document** with all tables filled
2. **Sample metrics output** (12-20 rows from metrics_summary.py)
3. **Capacity measurement** (throughput, cell_util, time_x)
4. **Any warnings or issues** encountered
5. **Confirmation:** Ready for Day 4? YES/NO

**Wait for approval before Day 4!**

---

**Project Status:** ✅ Day 3 READY  
**Created:** 2026-10-26 20:11 UTC  
**Next:** Run setup checklist to begin testing
