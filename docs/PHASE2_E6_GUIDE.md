# Phase 2: Data Collection for E6 Experiment
## Testbed Team - Next Steps Guide

**Date:** October 18, 2026  
**Status:** Days 1-2 Complete ✅ | E6 Data Collection Phase Starting  
**Critical:** Follow dataset team's specification exactly

---

## ⚠️ IMPORTANT: Our Role Clarification

### What We Do NOT Do:
- ❌ Train models on our testbed data
- ❌ Use "normal vs congested" labels
- ❌ Create our own feature set
- ❌ Collect 1-second interval data

### What We DO:
- ✅ Collect E6 test data at **250ms intervals**
- ✅ Use dataset team's **6 measurements + label formula**
- ✅ Provide **zero-shot test set** for their trained models
- ✅ Validate sim-to-reality transfer on live hardware

**Key Point:** Dataset team trains models on simulation (E1-E4). Our data is **E6 test set only** to prove their model works on real hardware.

---

## 📋 Six-Step Validation Process

### Step 1: Verify 250ms KPM Reporting ⏰

**Goal:** Confirm gNB reports all 6 measurements every 250ms

**Actions:**

1. **Modify gNB config for 250ms reporting:**

```bash
cd ~/oran-sc-ric/e2-agents/srsRAN
cp gnb_zmq.yaml gnb_zmq.yaml.backup

nano gnb_zmq.yaml
```

Find the `metrics:` section and change:
```yaml
metrics:
  enable_json: true           # Enable JSON metrics output
  autostart_stdout_metrics: false
  periodicity:
    du_report_period: 250     # Change from 1000 to 250ms
    cu_up_report_period: 250
    cu_cp_report_period: 250
```

Save (Ctrl+X, Y, Enter)

2. **Start testbed and check metrics:**

```bash
# Terminal 1: Core
cd ~/srsRAN_Project/docker && sudo docker compose up 5gc

# Terminal 2: RIC
cd ~/oran-sc-ric && sudo docker compose up

# Terminal 3: gNB with JSON metrics to file
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json

# Terminal 4: UE
sudo ip netns add ue1
cd ~/srsRAN_4G/build/srsue/src
sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf

# Terminal 5: Generate traffic
sudo ip ro add 10.45.0.0/16 via 10.53.1.2
sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -u -b 5M -t 60 -R
```

3. **Check metrics arrive every 250ms:**

```bash
# In another terminal, watch the metrics
tail -f /tmp/gnb_metrics.json | grep timestamp
```

**Expected:** New JSON entries every 250ms

4. **Verify required fields exist:**

```bash
# Check one metrics entry
grep -A 50 '"ue_container"' /tmp/gnb_metrics.json | head -60
```

**Required fields per UE:**
- `cqi` → Downlink CQI (0-15)
- `pusch_snr_db` → Uplink SINR (dB)
- `dl_brate` → Download speed (bps, convert to Mbps)
- `ul_brate` → Upload speed (bps, convert to Mbps)
- `ul_nof_ok` and `ul_nof_nok` → For uplink error rate %
- `dl_bs` → Downlink buffer size (bytes)

**Cell-level:**
- PRB usage → Compute `cell_util = used_prbs / 12500`

**Deliverable for Step 1:**
```bash
# Extract 1 minute of metrics
head -300 /tmp/gnb_metrics.json > step1_sample_250ms.json
```

Send `step1_sample_250ms.json` to dataset team with message:
> "Step 1 complete. Attached: 1 minute of 250ms metrics. Please verify fields match your schema before I proceed to Step 2."

---

### Step 2: Confirm CQI Table (64-QAM) 📊

**Goal:** Verify gNB uses 64-QAM CQI table (not 256-QAM)

**Actions:**

1. **Check gNB config:**

```bash
grep -A10 "pdsch:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
```

Look for:
```yaml
pdsch:
  mcs_table: qam64  # Should be qam64, not qam256
```

2. **Check gNB startup logs:**

```bash
grep -i "cqi\|mcs\|table" /tmp/gnb_metrics.json | head -20
```

3. **Verify CQI range during traffic:**

```bash
# Run traffic and collect CQI values
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -u -b 10M -t 60 -R &

# Watch CQI in real-time (in gNB terminal, type 't')
# CQI should range 0-15 for 64-QAM table
```

**Expected:** CQI values between 0-15 (64-QAM table)  
**Not expected:** CQI values above 15 (would indicate 256-QAM)

**Deliverable for Step 2:**

Document findings:
```bash
cat > step2_cqi_verification.txt << EOF
CQI Table Check (Step 2)
========================
Config file setting: [qam64/qam256]
Observed CQI range: [min-max]
Sample CQI values: [list 10 values]
Conclusion: [64-QAM confirmed / needs adjustment]
EOF
```

Send to dataset team.

---

### Step 3: Setup 3 UEs 📱📱📱

**Goal:** Run 3 simultaneous UEs (not just 1) to create multi-user scenarios

**Challenge:** srsRAN 4G srsUE is single-instance. Need GNU Radio approach.

**Actions:**

**Option A: ZMQ Multi-UE (Simpler, Try First)**

1. **Check if srsRAN supports multi-UE with ZMQ:**

```bash
cd ~/srsRAN_4G/build/srsue/src
./srsue --help | grep -i "multi\|instance"
```

2. **Create 3 UE configs with different identities:**

```bash
cd ~
cp ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf ue1_zmq.conf
cp ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf ue2_zmq.conf
cp ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf ue3_zmq.conf
```

**Edit each config:**
- `ue1_zmq.conf`: IMSI `001010123456780` (existing)
- `ue2_zmq.conf`: IMSI `001010123456781`, different ZMQ ports (2002/2003)
- `ue3_zmq.conf`: IMSI `001010123456782`, different ZMQ ports (2004/2005)

3. **Register all 3 UEs in core:**

```bash
# Open http://localhost:9999 (admin/1423)
# Add subscribers:
#   IMSI: 001010123456781, K: 00112233445566778899aabbccddeeff, OPC: 63bfa50ee6523365ff14c1f45f88737d
#   IMSI: 001010123456782, K: 00112233445566778899aabbccddeeff, OPC: 63bfa50ee6523365ff14c1f45f88737d
```

**Option B: GNU Radio Broker (If Option A Fails)**

Follow srsRAN multi-UE tutorial:
https://docs.srsran.com/projects/4g/en/latest/app_notes/source/zeromq/source/index.html#multiple-ues

**Deliverable for Step 3:**

```bash
# Test all 3 UEs connected
ping 10.45.1.2  # UE1
ping 10.45.1.3  # UE2
ping 10.45.1.4  # UE3

# Document
cat > step3_multi_ue.txt << EOF
Multi-UE Setup (Step 3)
=======================
Number of UEs: 3
UE IPs: 10.45.1.2, 10.45.1.3, 10.45.1.4
IMSIs: 001010123456780-782
All connected: [YES/NO]
CPU load during operation: [%]
"Late" warnings: [YES/NO]
EOF
```

---

### Step 4: Max Cell Throughput Test 🚀

**Goal:** Find cell capacity and confirm `cell_util` approaches 1.0 at saturation

**Actions:**

1. **Run max downlink UDP on all 3 UEs:**

```bash
# Terminal A: iperf3 server
iperf3 -s -p 5201

# Terminal B: iperf3 server (UE2)
iperf3 -s -p 5202

# Terminal C: iperf3 server (UE3)
iperf3 -s -p 5203

# Terminal D: UE1 traffic (start conservative, increase)
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 10M -t 60 -R

# Terminal E: UE2 traffic
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 10M -t 60 -R

# Terminal F: UE3 traffic
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 10M -t 60 -R
```

2. **Gradually increase load and watch gNB stats:**

In gNB terminal, type `t` for live stats:
```
 Pci rnti | cqi ri mcs brate ok nok (%) dl_bs | ...
```

3. **Watch for saturation indicators:**
- `dl_bs` (downlink buffer) growing
- `brate` plateaus despite higher offered load
- Cell PRB usage near 100%

4. **Check CPU bottleneck:**

```bash
# In another terminal
htop
# Watch for gNB process at 100% CPU
# If CPU saturates before radio, that's the bottleneck
```

5. **Calculate cell_util at max load:**

From JSON metrics:
```bash
grep "cell_util\|prb" /tmp/gnb_metrics.json | tail -50
```

**Expected:** `cell_util` → 1.0 when throughput plateaus  
**Problem:** If `cell_util` stays low but throughput plateaus → CPU bottleneck

**Deliverable for Step 4:**

```bash
cat > step4_capacity.txt << EOF
Cell Capacity Test (Step 4)
============================
Max total throughput: [XX Mbps] (sum of 3 UEs)
Per-UE throughput at saturation: [XX, XX, XX Mbps]
Cell util at max load: [0.XX]
CPU usage: [XX%]
Bottleneck: [Radio / CPU]
Starvation observed: [YES/NO]
Notes: [Any "late" warnings, packet loss patterns]
EOF
```

---

### Step 5: Build Dataset-Team-Compatible Collector 📝

**Goal:** Collect data in EXACT format matching dataset team's schema

**Schema (from dataset team):**
```
timestamp, ue_id, cell_util, dl_cqi, ul_sinr_db, dl_mbps, ul_mbps, ul_error_pct, 
dl_buffer_bytes, offered_bytes, delivered_bytes
```

**Create new collector:**

```bash
nano ~/testbed_collector.py
```

```python
#!/usr/bin/env python3
"""
E6 Testbed Data Collector
Matches dataset team schema exactly - 250ms intervals
"""
import json
import csv
import time
import sys
from datetime import datetime

# Output schema - matches dataset team
FIELDNAMES = [
    'timestamp',      # Unix timestamp (float)
    'ue_id',          # 0, 1, 2 for our 3 UEs
    'cell_util',      # used_prbs / 12500
    'dl_cqi',         # 0-15
    'ul_sinr_db',     # dB
    'dl_mbps',        # Mbps
    'ul_mbps',        # Mbps
    'ul_error_pct',   # (nok / (ok + nok)) * 100
    'dl_buffer_bytes',# Bytes waiting
    'offered_bytes',  # Bytes UE requested (from iperf rate)
    'delivered_bytes' # Bytes UE received (from dl_brate * 0.25s)
]

def parse_gnb_json_metrics(json_line):
    """Parse one line of gNB JSON metrics"""
    try:
        data = json.loads(json_line)
        
        timestamp = time.time()
        rows = []
        
        # Extract cell-level metrics
        # TODO: Parse actual JSON structure from Step 1 output
        cell_util = 0.0  # used_prbs / 12500
        
        # Extract per-UE metrics
        if 'ue_container' in data:
            for ue in data['ue_container']:
                ue_id = ue.get('ue_id', 0)
                
                # Map to dataset schema
                row = {
                    'timestamp': timestamp,
                    'ue_id': ue_id,
                    'cell_util': cell_util,
                    'dl_cqi': ue.get('cqi', 0),
                    'ul_sinr_db': ue.get('pusch_snr_db', 0.0),
                    'dl_mbps': ue.get('dl_brate', 0) / 1e6,
                    'ul_mbps': ue.get('ul_brate', 0) / 1e6,
                    'ul_error_pct': 0.0,  # Calculate from ul_nof_ok/nok
                    'dl_buffer_bytes': ue.get('dl_bs', 0),
                    'offered_bytes': 0,   # From iperf rate
                    'delivered_bytes': 0  # From dl_brate * 0.25
                }
                
                # Calculate ul_error_pct
                ok = ue.get('ul_nof_ok', 0)
                nok = ue.get('ul_nof_nok', 0)
                if ok + nok > 0:
                    row['ul_error_pct'] = (nok / (ok + nok)) * 100
                
                rows.append(row)
        
        return rows
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return []

def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'e6_testbed_data.csv'
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        
        print(f"Collecting to {output_file}. Reading gNB metrics from stdin...")
        print("Format: tail -f /tmp/gnb_metrics.json | python3 testbed_collector.py")
        
        for line in sys.stdin:
            rows = parse_gnb_json_metrics(line.strip())
            for row in rows:
                writer.writerow(row)
                f.flush()  # Write immediately
                print(f"Collected: UE {row['ue_id']}, CQI {row['dl_cqi']}, "
                      f"DL {row['dl_mbps']:.2f} Mbps", file=sys.stderr)

if __name__ == '__main__':
    main()
```

**Note:** You'll need to adjust the JSON parsing based on actual gNB output from Step 1.

Make executable:
```bash
chmod +x ~/testbed_collector.py
```

**Test collector:**
```bash
# Feed it Step 1 sample
cat step1_sample_250ms.json | python3 ~/testbed_collector.py test_output.csv

# Check output
head test_output.csv
# Should show: timestamp,ue_id,cell_util,dl_cqi,ul_sinr_db,dl_mbps,ul_mbps,ul_error_pct,dl_buffer_bytes,offered_bytes,delivered_bytes
```

---

### Step 6: Collect 10-Minute Sample for Dataset Team ✅

**Goal:** Collect sample data and get dataset team's validation before full collection

**Scenario:** Mix of loads

```bash
# Start collection
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py e6_sample_10min.csv &
COLLECTOR_PID=$!

# Run 10-minute scenario with varying load
# Minutes 0-3: Light load (2 Mbps per UE)
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 2M -t 180 -R &
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 2M -t 180 -R &
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 2M -t 180 -R &
sleep 180

# Minutes 3-6: Medium load (10 Mbps per UE)
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 10M -t 180 -R &
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 10M -t 180 -R &
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 10M -t 180 -R &
sleep 180

# Minutes 6-10: Heavy load (30 Mbps per UE - should congest)
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 30M -t 240 -R &
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 30M -t 240 -R &
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 30M -t 240 -R &
sleep 240

# Stop collector
kill $COLLECTOR_PID
```

**Check sample:**
```bash
wc -l e6_sample_10min.csv
# Should have ~2400 rows (10 min * 60 s * 4 intervals/s * 3 UEs)

head -20 e6_sample_10min.csv
tail -20 e6_sample_10min.csv
```

**Send to dataset team:**

Email/message:
```
Subject: E6 Sample Data - Ready for Validation

Hi [Dataset Team],

Completed Steps 1-6. Attached:
1. step1_sample_250ms.json - Raw gNB metrics at 250ms
2. step2_cqi_verification.txt - CQI table confirmed
3. step3_multi_ue.txt - 3 UEs working
4. step4_capacity.txt - Cell capacity measured
5. e6_sample_10min.csv - 10 minutes in your schema format

Please run your tests.py validation script on the CSV.
Let me know if format matches before I collect full E6 dataset.

The sample includes:
- 3 UEs (ue_id: 0, 1, 2)
- Light/medium/heavy load periods
- Expected starvation in heavy load period
- ~2400 rows at 250ms intervals

Waiting for your validation before full collection.
```

---

## 🚫 Files to Delete (Not Needed)

```bash
cd ~/College/Project/5G

# Delete these - they were based on wrong assumptions:
rm -f train_model.py  # Dataset team trains, not us
rm -f analyze_results.py  # Their analysis, not ours
rm -f test_experiment.sh  # Wrong 1s intervals
rm -f kpm_logger_xapp.py  # Wrong schema
rm -f congestion_prediction_xapp.py  # Premature, wait for their model

# Keep these:
# - SETUP_GUIDE.md
# - RUN_GUIDE.md  
# - TRANSFER_GUIDE.md
# - README.md (but needs update)
# - testbed_collector.py (new, correct one)
# - prompt.txt
# - ubuntu_setup.sh
# - gnb_zmq_simple.yaml, ue_zmq_simple.conf (backups)
```

---

## 📅 Tomorrow's Workflow

### Morning Session (Steps 1-2): ~1 hour
```bash
# 1. Start testbed (RUN_GUIDE.md)
# 2. Modify gnb config for 250ms
# 3. Collect step1_sample_250ms.json
# 4. Send to dataset team
# 5. Check CQI table, document step2_cqi_verification.txt
# 6. Send to dataset team
# WAIT for their confirmation before proceeding
```

### Afternoon Session (Steps 3-4): ~2 hours
```bash
# After dataset team confirms Steps 1-2:
# 3. Setup 3 UEs (try ZMQ multi-UE first)
# 4. Run capacity test
# 5. Document findings
# 6. Send to dataset team
```

### Evening Session (Steps 5-6): ~2 hours
```bash
# After Steps 3-4 validated:
# 5. Fix testbed_collector.py based on actual JSON structure
# 6. Collect 10-minute sample
# 7. Send to dataset team for validation
# WAIT for their tests.py results
```

### Following Day: Full Collection
```bash
# Only after dataset team validates sample:
# - Collect full E6 dataset (various scenarios, 1-2 hours)
# - Send to dataset team
# - They test their trained model on our data (E6 experiment)
# - Compare E6 results with E4 (their upper bound)
# - Measure sim-to-reality transfer gap
```

---

## ✅ Success Criteria

**Step 1:** gNB outputs JSON every 250ms with all 6 measurement fields  
**Step 2:** CQI table is 64-QAM (values 0-15)  
**Step 3:** 3 UEs connected simultaneously, no "late" warnings  
**Step 4:** Cell util → 1.0 at saturation (not CPU-bound)  
**Step 5:** Collector outputs dataset team's exact schema  
**Step 6:** Dataset team's tests.py passes on our sample

**Only proceed to next step after current step validated by dataset team!**

---

## 🆘 If Things Go Wrong

**Problem:** Can't get 3 UEs working  
**Fallback:** Start with 2 UEs, document limitation

**Problem:** CPU bottleneck (cell_util low at saturation)  
**Solution:** Reduce VM to 2 UEs, OR increase VM CPU cores, OR note limitation

**Problem:** Dataset team says schema doesn't match  
**Solution:** They provide fixed parser/collector code

**Problem:** gNB doesn't output JSON metrics  
**Solution:** Check srsRAN docs for metrics configuration, may need different output format

---

## 📞 Communication Template

**Daily Update to Dataset Team:**

```
Date: [Date]
Status: Step [X] of 6

Completed today:
- [What you did]

Results:
- [Key findings]

Attached:
- [Files]

Blockers:
- [Any issues]

Next:
- [Tomorrow's plan]

Questions:
- [Anything unclear]
```

---

**Start tomorrow with Step 1. Don't proceed without dataset team validation at each step!** 🚀
