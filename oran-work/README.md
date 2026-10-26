# O-RAN Congestion Prediction: Days 3-4 Implementation Guide
**Project:** E6 Testbed Data Collection  
**Date:** October 26, 2026  
**Status:** Ready for Day 3 Testing

---

## 📁 Project Structure

```
~/oran-work/
├── gnb_single.yaml              # Corrected gNB config (250ms, log metrics)
├── metrics_summary.py           # Parse gNB logs into 250ms reports
├── day3_setup_checklist.sh      # Verify all prerequisites
├── day3_test_guide.sh           # Interactive guide for Day 3
├── day3_results_template.txt    # Document your findings
└── runs/                        # Will store Day 4 test runs
```

---

## ✅ What's Been Fixed

### Before (Wrong Approach):
- ❌ Used E2SM-KPM subscription at 1-second intervals
- ❌ Collected via `kpm_logger_xapp.py` 
- ❌ Manual "normal/congested" labels
- ❌ JSON as primary data source

### After (Corrected Approach):
- ✅ gNB log metrics at 250ms intervals
- ✅ Parse via `metrics_summary.py`
- ✅ Calculate labels from delivered÷offered formula
- ✅ Log as primary source (JSON for live xApp later)

---

## 🚀 Quick Start: Day 3

### Step 1: Verify Prerequisites (5 minutes)

```bash
cd ~/oran-work
./day3_setup_checklist.sh
```

**Expected output:** All checks pass ✓

If any checks fail:
- **moreutils not installed:** `sudo apt install -y moreutils`
- **websocket-client not installed:** `pip3 install websocket-client`
- **Configs missing:** Files created in `/home/oran/oran-work/`

---

### Step 2: Run Day 3 Tests (2-3 hours)

```bash
cd ~/oran-work
./day3_test_guide.sh
```

This interactive script will:
1. Guide you through starting 5 terminals (Core, RIC, gNB, UE, Testing)
2. Verify 250ms metrics (E1)
3. Test JSON websocket feed (E2)
4. Test KPM at 250ms (E3)
5. Measure single-UE capacity (E4)
6. Confirm 64-QAM CQI table (E5)

**To save full output:**
```bash
./day3_test_guide.sh 2>&1 | tee ~/oran-work/day3_output.txt
```

---

### Step 3: Document Results

```bash
cp ~/oran-work/day3_results_template.txt ~/oran-work/day3_results.txt
nano ~/oran-work/day3_results.txt
```

Fill in:
- Metrics summary outputs
- Capacity test table
- Single-UE capacity measurement
- Any issues encountered

---

## 🔍 What Day 3 Tests Verify

### E1: 250ms Metrics ✓
**Goal:** Confirm gNB reports every 250ms at real-time speed

**Success criteria:**
- `wall_ms` ≈ 250 (wall clock time between reports)
- `slots` = 250 (gNB time units)
- `time_x` ≈ 1.00 (ratio: proves real-time, not slow-motion)
- All 6 inputs visible per UE

**If time_x < 0.9:** CPU can't keep up → reduce to 2 UEs or report issue

---

### E2: JSON Feed ✓
**Goal:** Verify websocket metrics for future live xApp

**Success criteria:**
- JSON received on port 8001
- Contains UE metrics structure
- Will be used in Day 4+ for live monitoring

---

### E3: KPM 250ms ✓
**Goal:** Check if E2 interface supports 250ms and PRB usage

**Record:**
- Does subscription succeed?
- How many indications per second? (4 = 250ms, 1 = 1s)
- Does `RRU.PrbUsedDl` exist and respond to traffic?

**Result determines:** Whether live xApp can get `cell_util` over E2

---

### E4: Single-UE Capacity ✓
**Goal:** Find maximum throughput and verify radio (not CPU) is bottleneck

**Success criteria:**
- Throughput plateaus at some rate C (your single-UE capacity)
- At plateau: `cell_util` ≈ 0.9-1.0
- Throughout test: `time_x` ≈ 1.0
- No CPU core pinned at 100%

**Warning signs:**
- Throughput plateaus but `cell_util` < 0.8 → CPU bottleneck
- `time_x` drops below 0.9 → emulation too slow

---

### E5: CQI Table ✓
**Goal:** Confirm 64-QAM table (matches TRACTOR dataset)

**Success criteria:**
- Config shows `mcs_table: qam64`
- Observed CQI values: 0-15 only
- No values above 15 (would indicate 256-QAM)

---

## 📊 Expected Day 3 Outcomes

### Good Results:
```
wall_ms   slots time_x cell_util | per UE: rnti cqi snr_db dl_Mbps ul_Mbps ul_err% dl_bs
    250     250   1.00     0.347 | 0x4601 15 28.5 12.34 0.02 0.0 4096

Single-UE Capacity: ~30-50 Mbps (depends on hardware)
At capacity: cell_util → 0.95, time_x = 1.00
```

### Problem Results:
```
# Time scale issue (emulation too slow)
wall_ms   slots time_x cell_util
    500     250   0.50     0.150   ← PROBLEM: time_x = 0.5 means half speed

# CPU bottleneck
Offered 50M, delivered 30M, cell_util = 0.60  ← PROBLEM: should be near 1.0
htop shows: CPU core at 100%
```

---

## 🔧 Troubleshooting

| Symptom | Cause → Fix |
|---------|-------------|
| No metrics in `/tmp/gnb.log` | `enable_log: false` → check gnb_single.yaml line 66 |
| `wall_ms` ≈ 1000 instead of 250 | `du_report_period` not applied → check indentation in yaml |
| `time_x` << 1.0 | CPU too slow → close apps, add VM cores, or report |
| JSON test shows nothing | `remote_control` missing → check gnb_single.yaml |
| UE won't attach | Wait 60 seconds after stopping gNB before restart |
| iperf3 connection refused | Server not running: `iperf3 -s -p 5201 -D` |

---

## 📦 Backup & Safety

### Automatic Backup:
Created at `/home/oran/Desktop/backups/backup_20261026_200723.tar.gz`

### Restore if needed:
```bash
cd /home/oran/Desktop/backups
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz -C /home/oran/Desktop/
```

### Manual backup before major changes:
```bash
cd /home/oran/Desktop
tar -czf backups/backup_before_day4_$(date +%Y%m%d_%H%M%S).tar.gz oran-work/ 5G/ phase2_corrected/
```

---

## 📤 What to Send After Day 3

### To Your Friend (for verification):
1. Output of `metrics_summary.py` showing 12-20 rows
2. KPM 250ms test results
3. Capacity test table with cell_util values
4. Peak CPU % and lowest time_x observed
5. Any issues or anomalies

### Example message:
```
Day 3 Complete - Results:

E1: 250ms confirmed, time_x = 1.02 average
E2: JSON feed working
E3: KPM subscription works, 4 indications/sec, RRU.PrbUsedDl present
E4: Single-UE capacity = 42 Mbps, cell_util reached 0.94 at plateau
E5: CQI table = qam64, observed range 8-15

No CPU bottleneck detected. Ready for Day 4?

Attached: day3_results.txt
```

---

## 🎯 Day 3 Success Criteria

- [x] All files created in ~/oran-work/
- [ ] day3_setup_checklist.sh passes all checks
- [ ] 250ms reports confirmed (wall_ms ≈ 250)
- [ ] Real-time speed confirmed (time_x ≈ 1.0)
- [ ] All 6 measurements visible
- [ ] Single-UE capacity measured
- [ ] cell_util reaches ~0.9-1.0 at saturation
- [ ] No CPU bottleneck
- [ ] Results documented in day3_results.txt
- [ ] Friend approves before Day 4

---

## 🔜 After Day 3 Approval

Day 4 will add:
- GNU Radio broker for multi-UE
- 3 UE configs (different ports/IMSIs)
- Multi-UE gNB config
- Traffic run scripts
- Cell capacity measurement
- **Real congestion** (starvation events)

**Estimated time:** 3-4 hours

---

## 📞 Quick Commands Reference

```bash
# Verify setup
cd ~/oran-work && ./day3_setup_checklist.sh

# Run Day 3 tests (interactive)
cd ~/oran-work && ./day3_test_guide.sh

# Check metrics manually
python3 ~/oran-work/metrics_summary.py /tmp/gnb.log 12

# Test JSON feed manually
timeout 5 python3 ~/srsRAN_Project/docker/telegraf/ws_adapter.py | head -c 2000

# Manual capacity test
iperf3 -s -p 5201 -D
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 20M -R -t 30

# View last metrics
python3 ~/oran-work/metrics_summary.py /tmp/gnb.log 4
```

---

## 📚 Key Files Reference

### Configuration:
- `~/oran-work/gnb_single.yaml` - Day 3 gNB config (250ms, log enabled)
- `~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf` - UE config (unchanged)

### Scripts:
- `~/oran-work/metrics_summary.py` - Parse gNB logs
- `~/oran-work/day3_setup_checklist.sh` - Pre-flight check
- `~/oran-work/day3_test_guide.sh` - Interactive testing

### Data:
- `/tmp/gnb.log` - gNB metrics output (primary data source)
- `~/oran-work/day3_results.txt` - Your documented results

---

## ⏱️ Time Estimate

| Phase | Duration |
|-------|----------|
| Setup verification | 5-10 min |
| Start stack (5 terminals) | 10-15 min |
| E1-E3 verification | 20-30 min |
| E4 capacity test | 30-45 min |
| Documentation | 15-30 min |
| **Total Day 3** | **~2-3 hours** |

---

**Status:** Ready to begin! Start with `./day3_setup_checklist.sh`

**Questions?** Review troubleshooting section or consult with your friend.

**Critical:** Do NOT proceed to Day 4 without friend's approval of Day 3 results.
