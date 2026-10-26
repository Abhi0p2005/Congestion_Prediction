# Tomorrow's Continuation - E6 Data Collection Project

**Date Created:** October 24, 2026, 11:50 PM IST  
**Last Session:** October 24, 2026, 9:00 PM - 11:50 PM IST  
**Status:** Phase 2 in progress - gNB startup issue being debugged

---

## 📊 Current Project Status

### ✅ Completed
- **Days 1-2:** Full O-RAN testbed infrastructure working (verified Oct 18)
  - Core (Open5GS), RIC, gNB, UE all functional
  - E2 interface verified (KPM monitoring, RC control)
- **Phase 2 Preparation:** All corrected files created and copied to VM
  - Wrong code identified: `~/kpm_logger_xapp.py` (deleted)
  - Corrected configs created (250ms, JSON enabled, 3 UE configs)
  - Data collector script created (`testbed_collector.py`)
  - Automated test scripts created (run_step1.sh, run_step2.sh, run_step6.sh)

### ⏳ In Progress
- **Step 1:** Verify 250ms KPM Reporting
  - Script running: `./run_step1.sh`
  - Testbed started successfully in 4 terminals:
    - ✅ Terminal 1: Core running
    - ✅ Terminal 2: RIC running (RMR ready)
    - ✅ Terminal 4: UE connected (IP: 10.45.1.2)
    - ⚠️ Terminal 3: gNB stuck during startup with `tee` redirect

### 🔴 Current Blocker
**gNB startup hanging when using:**
```bash
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json
```

**Config verified correct:**
- ✅ `autostart_stdout_metrics: true`
- ✅ `enable_json: true`
- ✅ `du_report_period: 250`
- ✅ CQI table: qam64

---

## 🔧 Issue Details

### Problem
gNB process hangs when redirecting output with `tee` command. Process starts but terminal becomes unresponsive.

### What Was Tried
1. ✅ Config updated to enable metrics (stdout + JSON)
2. ✅ 60-second cooldown between restarts observed
3. ⚠️ gNB hangs when using `2>&1 | tee /tmp/gnb_metrics.json`

### Not Yet Tried
1. Running gNB without `tee` redirect (direct output only)
2. Checking for ZMQ port conflicts (2000/2001)
3. Verifying gNB log file `/tmp/gnb.log` for errors
4. Checking if UE needs restart due to port conflict

---

## 🚀 Tomorrow's Action Plan

### Step 1: Debug gNB Startup (15 min)

**Terminal 5 (diagnostic terminal):**
```bash
# Check if gNB is running but stuck
ps aux | grep gnb

# Check for port conflicts
sudo netstat -tulpn | grep 2000
sudo netstat -tulpn | grep 2001

# Check gNB logs for errors
cat /tmp/gnb.log | tail -50

# Check if metrics file is being written
ls -lh /tmp/gnb_metrics.json
cat /tmp/gnb_metrics.json
```

**Terminal 3 (gNB):**
```bash
# Try WITHOUT tee redirect first
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml

# After it starts successfully:
# 1. Type 't' to toggle metrics display
# 2. Verify metrics appear every 250ms
# 3. Ctrl+C to stop
```

**If direct output works but tee fails:**
```bash
# Alternative: Redirect stderr to file, stdout to screen
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>/tmp/gnb_metrics.json

# Or use output buffering fix
stdbuf -oL sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json
```

---

### Step 2: Complete Step 1 Validation (30 min)

**Once gNB outputs metrics successfully:**

**Go back to original terminal where `./run_step1.sh` is waiting:**
```bash
# Press Enter to continue the script
# It will:
# 1. Setup routes
# 2. Test connectivity
# 3. Generate traffic
# 4. Collect 1-minute sample
# 5. Create ~/step1_sample_250ms.json
```

**Copy deliverable to Windows:**
```bash
cp ~/step1_sample_250ms.json ~/Desktop/
```

From Windows, drag `step1_sample_250ms.json` from Ubuntu Desktop to `C:\College\Project\5G\deliverables\`

---

### Step 3: Run Step 2 - CQI Verification (15 min)

```bash
cd ~
./run_step2.sh

# Creates: ~/step2_cqi_verification.txt
cp ~/step2_cqi_verification.txt ~/Desktop/
```

---

### Step 4: Send to Dataset Team & Wait

**Email/message to dataset team:**
```
Subject: E6 Data Collection - Steps 1-2 Results

Hi [Dataset Team],

Completed validation steps 1-2:

Step 1 (250ms KPM):
- gNB configured for 250ms reporting
- All 6 measurement fields present
- Metrics arriving at 250ms intervals
- Attached: step1_sample_250ms.json (1 min sample)

Step 2 (CQI Table):
- Verified: CQI table is 64-QAM
- CQI range observed: 0-15 (correct)
- Attached: step2_cqi_verification.txt

Questions before proceeding to Steps 3-6:
- Does the JSON structure match your parser expectations?
- Can tests.py validate the format?
- Any adjustments needed before multi-UE setup?

Ready to proceed once you confirm.
```

**⏸️ STOP HERE - Wait for dataset team validation (1-24 hours)**

---

### Step 5: After Dataset Approval - Multi-UE Setup (2-3 hours)

**Only proceed after dataset team confirms Steps 1-2 are correct.**

This is complex and may not work with ZMQ. Be prepared to continue with 1 UE if multi-UE fails.

**See:** `PHASE2_E6_GUIDE.md` Step 3 for detailed multi-UE instructions

---

## 📁 File Locations

### In Ubuntu VM (`~/`)
- ✅ `run_step1.sh` - Step 1 automation script
- ✅ `run_step2.sh` - Step 2 automation script  
- ✅ `run_step6.sh` - Step 6 automation script
- ✅ `testbed_collector.py` - Dataset schema collector
- ✅ `ue2_zmq.conf` - UE2 config (IMSI: ...781)
- ✅ `ue3_zmq.conf` - UE3 config (IMSI: ...782)
- ✅ `~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml` - Corrected gNB config
- ✅ `~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf` - UE1 config (IMSI: ...780)

### In Windows (`C:\College\Project\5G\`)
- ✅ `phase2_corrected/` - All corrected implementation files
- ✅ `phase2_corrected/README_IMPLEMENTATION.md` - Complete implementation guide
- ✅ `phase2_corrected/ANALYSIS_WRONG_CODE.md` - Why kpm_logger_xapp.py is wrong
- ✅ `TOMORROW_PLAN.md` - Original Oct 18 plan (now superseded by this file)
- ✅ `README.md` - Project overview
- ✅ `RUN_GUIDE.md` - Testbed startup guide
- ✅ `PHASE2_E6_GUIDE.md` - Detailed 6-step E6 guide

---

## 🎯 Critical Reminders

### Your Role in E6 Experiment
- ❌ **DO NOT** train models on testbed data
- ❌ **DO NOT** use "normal/congested" manual labels
- ✅ **DO** collect E6 test data at 250ms intervals only
- ✅ **DO** match dataset team's exact schema
- ✅ **DO** wait for validation at each checkpoint

### Wrong Code Already Deleted
- ❌ `~/kpm_logger_xapp.py` - Deleted (was using 1-second intervals, wrong schema)

### Dataset Team Schema (Must Match Exactly)
```csv
timestamp,ue_id,cell_util,dl_cqi,ul_sinr_db,dl_mbps,ul_mbps,ul_error_pct,dl_buffer_bytes,offered_bytes,delivered_bytes
```

### Starvation Label Formula
```python
starved = (delivered_bytes / offered_bytes) < 0.5
```

---

## 📞 Troubleshooting Quick Reference

### gNB won't start
- Wait 60 seconds between restarts (RIC cooldown)
- Check ports: `sudo netstat -tulpn | grep 2000`
- Check logs: `cat /tmp/gnb.log | tail -50`

### No metrics output
- Verify config: `grep -A10 "^metrics:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml`
- Should show: `autostart_stdout_metrics: true`
- Type `t` in gNB terminal to toggle metrics

### UE won't connect
- Check gNB is running: `ps aux | grep gnb`
- Check UE has IP: Look for "IP: 10.45.1.2" in Terminal 4
- Restart order: Core → RIC → gNB (wait for started) → UE

### Docker containers stopped
```bash
cd ~/srsRAN_Project/docker && sudo docker compose up 5gc    # Terminal 1
cd ~/oran-sc-ric && sudo docker compose up                   # Terminal 2
```

---

## 📊 Expected Timeline (After gNB Fixed)

| Task | Duration | Wait |
|------|----------|------|
| Fix gNB startup | 15 min | - |
| Complete Step 1 | 30 min | - |
| Complete Step 2 | 15 min | - |
| **Dataset validation** | - | 1-24 hours |
| Steps 3-4 (Multi-UE) | 2-3 hours | - |
| **Dataset validation** | - | 1-24 hours |
| Steps 5-6 (Collector) | 2 hours | - |
| **Final validation** | - | 1-24 hours |
| Full E6 collection | 1-2 hours | - |

**Total work time:** 5-7 hours (excluding waits)  
**Total project time:** 3-5 days (with checkpoints)

---

## 🔍 What to Check First Tomorrow

**In order of priority:**

1. ✅ **Is testbed still running?**
   - Check Terminals 1, 2, 4 are still active
   - If not, restart from scratch (see RUN_GUIDE.md)

2. ✅ **Try gNB without tee redirect**
   - Terminal 3: `sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml`
   - Type `t` to see metrics
   - If this works, issue is with tee/redirect

3. ✅ **Check for port conflicts**
   - `sudo netstat -tulpn | grep 2000`
   - If ports busy, restart UE

4. ✅ **Complete Step 1 once gNB works**
   - Return to terminal where `./run_step1.sh` is waiting
   - Press Enter to continue

---

## 🎓 Key Learnings from Today

### What Worked
- ✅ File organization and correction approach was correct
- ✅ Config changes were properly identified
- ✅ Scripts created successfully
- ✅ Core, RIC, UE all started without issues
- ✅ Systematic debugging approach

### What Needs Investigation
- ⚠️ gNB hangs with `tee` redirect (buffering issue?)
- ⚠️ May need alternative metrics capture method
- ⚠️ Multi-UE with ZMQ may be challenging (prepare 1-UE fallback)

### Alternative Approaches if Current Method Fails
1. **Metrics via gNB stdout + screen recording**
2. **Metrics via E2 subscription (1-second, not ideal but acceptable)**
3. **Continue with 1 UE instead of 3 (document limitation)**

---

## 📋 Tomorrow's Checklist

```
[ ] Check if testbed containers still running (docker ps -a)
[ ] Try gNB without tee redirect
[ ] Debug why tee causes hang (buffering, stderr vs stdout)
[ ] Get gNB outputting metrics successfully
[ ] Complete run_step1.sh (collect 1-min sample)
[ ] Run run_step2.sh (CQI verification)
[ ] Copy step1_sample_250ms.json and step2_cqi_verification.txt to Windows
[ ] Send to dataset team for validation
[ ] Wait for their response before proceeding
```

---

## 🚦 Success Criteria for Tomorrow

**Minimum (Must achieve):**
- ✅ gNB starts and outputs metrics
- ✅ Step 1 complete (1-min sample collected)
- ✅ Step 2 complete (CQI verified)
- ✅ Deliverables sent to dataset team

**Ideal (If time permits):**
- ✅ Dataset team responds same day
- ✅ Begin Step 3 (multi-UE setup)

**Stretch (Bonus):**
- ✅ Complete Steps 3-6
- ✅ Send 10-min validation sample

---

**Good night! Resume tomorrow with debugging the gNB startup issue.** 🌙

**First command to run tomorrow:**
```bash
# In Terminal 3
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
# (without tee redirect first)
```

If that works, we know the issue is with the tee redirect and can solve it from there.
