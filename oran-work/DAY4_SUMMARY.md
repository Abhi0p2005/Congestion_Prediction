# Day 4 Setup - Summary and Next Steps

**Date:** October 27, 2026  
**Status:** ✅ All Day 4 preparation files generated and committed to git

---

## ✅ What Was Just Completed

### Files Generated (7 new files in ~/Desktop/oran-work/)

1. **gnb_multi.yaml** - gNB configuration for 3-UE setup
   - Extended PRACH config: 64 preambles, reduced collision probability
   - Same 250ms metrics reporting, 64-QAM MCS table
   
2. **ue1_zmq.conf** - UE1 configuration
   - IMSI: 001010123456780
   - ZMQ ports: TX 2101 / RX 2100
   - Network namespace: ue1
   
3. **ue2_zmq.conf** - UE2 configuration
   - IMSI: 001010123456781
   - ZMQ ports: TX 2201 / RX 2200
   - Network namespace: ue2
   - Key: ...ccddef00 (different from UE1)
   
4. **ue3_zmq.conf** - UE3 configuration
   - IMSI: 001010123456782
   - ZMQ ports: TX 2301 / RX 2300
   - Network namespace: ue3
   - Key: ...ccddef01 (different from UE1)
   
5. **multi_ue_scenario.grc** - GNU Radio broker flow graph
   - Downloaded from srsRAN docs
   - **Modified slow_down_ratio from 4 → 1** (real-time speed)
   - Sample rate: 11.52 MHz (matching configs)
   
6. **run_traffic.sh** - Traffic orchestration script
   - Usage: `./run_traffic.sh <name> <seconds> <rate_ue1> <rate_ue2> <rate_ue3>`
   - Runs iperf3 UDP downlink with timestamped output
   - Saves logs + metadata to `~/Desktop/oran-work/runs/<name>/`
   
7. **day4_setup_guide.txt** - Comprehensive visual guide
   - Step-by-step terminal commands
   - Success criteria and troubleshooting
   - Restart checklist

### Core Network Preparation

8. **~/srsRAN_Project/docker/open5gs/subscriber_db.csv** - Created with 3 UEs
   - UE1: IMSI ...780, IP 10.45.1.2
   - UE2: IMSI ...781, IP 10.45.2.2
   - UE3: IMSI ...782, IP 10.45.3.2

9. **~/srsRAN_Project/docker/open5gs/open5gs.env** - Updated
   - Changed from single-line IMSI → `SUBSCRIBER_DB=subscriber_db.csv`

### Git Repository

✅ **Committed and pushed to GitHub:**
- Repository: https://github.com/Abhi0p2005/Congestion_Prediction
- Branch: master
- Commit: "Add Day 4 multi-UE setup files: 3-UE configs, GNU Radio broker, traffic script, and comprehensive guide"

---

## ⚠️ One Critical Step Remaining Before Day 4

**YOU MUST REBUILD THE 5GC DOCKER CONTAINER** to load the 3 subscribers:

```bash
cd ~/srsRAN_Project/docker
docker compose up --build 5gc
```

This is required **ONE TIME ONLY** because the subscriber database CSV is copied into the container at BUILD time.

**Verify it worked:** Open http://localhost:9999 in browser
- Login: admin / 1423
- You should see 3 subscribers (IMSI ending in ...780, ...781, ...782)

---

## 📋 Day 4 Quick Start (After Rebuild)

Once the 5GC rebuild is complete, follow the terminal sequence in `day4_setup_guide.txt`:

**Order:** Core → RIC → gNB → UE1, UE2, UE3 → GNU Radio Broker

1. **Terminal 1:** `cd ~/srsRAN_Project/docker && docker compose up 5gc`
2. **Terminal 2:** `cd ~/oran-sc-ric && docker compose up`
3. **Terminal 3:** `sudo ./gnb -c ~/Desktop/oran-work/gnb_multi.yaml`
4. **Terminal 4-6:** Three UE instances (after creating namespaces)
5. **Terminal 7:** `gnuradio-companion ~/Desktop/oran-work/multi_ue_scenario.grc`
   - Click PLAY button when UEs are waiting
6. **Terminal 8:** Verify, measure capacity, run overload tests

---

## 🎯 Day 4 Goals

1. ✅ Get all 3 UEs attached simultaneously
2. ✅ Verify `time_x ≈ 1.0` (real-time speed with 3 UEs)
3. ✅ Measure cell capacity **C** (total delivered throughput at plateau)
4. ✅ Run overload traffic at 1.3×C and 1.5×C
5. ✅ Confirm starvation bins (delivered < 50% offered) exist in logs

---

## 📂 File Locations Reference

| Item | Path |
|------|------|
| Day 4 Guide | `~/Desktop/oran-work/day4_setup_guide.txt` |
| Multi-UE gNB Config | `~/Desktop/oran-work/gnb_multi.yaml` |
| UE Configs | `~/Desktop/oran-work/ue{1,2,3}_zmq.conf` |
| GNU Radio Broker | `~/Desktop/oran-work/multi_ue_scenario.grc` |
| Traffic Script | `~/Desktop/oran-work/run_traffic.sh` |
| Metrics Parser | `~/Desktop/oran-work/metrics_summary.py` |
| Run Output | `~/Desktop/oran-work/runs/<run_name>/` |

---

## 🔍 What to Check Before Starting

✅ Day 3 was successful (verified yesterday):
- 250ms metrics working
- Single-UE capacity measured (~15-20 Mbps)
- `time_x ≈ 0.85-0.90` (acceptable for single UE)

⚠️ **Critical for Day 4:** `time_x` must stay **≥ 0.90** with 3 UEs
- If it drops below 0.85 → VM cannot handle 3 UEs in real time
- Options: Close all apps, add VM cores, or reduce to 2 UEs

---

## 📞 Next Communication Point

After you complete Day 4 setup and runs, share:
1. Output of `metrics_summary.py` for one overload run (20 lines)
2. Measured cell capacity C
3. Lowest `time_x` observed with 3 UEs
4. First 20 lines of `runs/over_150/iperf_ue1.txt`

This confirms the testbed can produce valid E6 test data before the dataset team proceeds with their pipeline integration.

---

**Status:** Ready to begin Day 4 testing! 🚀
