# O-RAN Congestion Prediction xApp - Quick Start Guide

**Last Updated:** October 18, 2026  
**Purpose:** Run the complete O-RAN testbed whenever you want

---

## 📋 Prerequisites Check

Before starting, verify:
- ✅ Ubuntu 22.04 VM is powered on
- ✅ VM has 8GB RAM allocated
- ✅ At least 20GB free disk space

---

## 🚀 Startup Procedure (6 Terminals)

### Overview
You need to start components in this order:
1. **Core** (5G network core)
2. **RIC** (Near-RT RIC with E2 interface)
3. **gNB** (Base station)
4. **UE** (User equipment / simulated phone)
5. **Traffic** (Generate network activity)
6. **xApp** (Your application)

**Total startup time:** ~3-4 minutes

---

## Terminal 1: Start 5G Core

**What it does:** Runs the Open5GS 5G core network (AMF, SMF, UPF) in Docker

```bash
cd ~/srsRAN_Project/docker
sudo docker compose up 5gc
```

**Wait for:** Logs to settle and show services running (~30 seconds)

**Success indicators:**
- `open5gs-amfd` started
- `open5gs-upfd` started
- `open5gs-webui` ready on port 9999

**Keep this terminal running** - don't close it!

---

## Terminal 2: Start RIC

**What it does:** Starts the Near-RT RIC with 7 containers (E2 termination, subscription manager, xApp runner, etc.)

```bash
cd ~/oran-sc-ric
sudo docker compose up
```

**Wait for:** `RMR is ready now ...` (~60-90 seconds)

**What's happening:**
- `e2term`: E2 interface endpoint (10.0.2.10:36421)
- `e2mgr`: E2 connection manager
- `submgr`: Subscription manager for xApps
- `python_xapp_runner`: Container where xApps run (10.0.2.20)
- `dbaas`: Redis database
- `appmgr`: xApp lifecycle manager
- `rtmgr_sim`: Routing manager

**Keep this terminal running!**

---

## Terminal 3: Start gNB (Base Station)

**What it does:** Starts the 5G gNB with E2 interface enabled, using ZeroMQ virtual radio

```bash
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
```

**Wait for these messages:**
- `N2: Connection to AMF on 10.53.1.2:38412 completed` ✓
- `E2AP: Connection to Near-RT-RIC on 10.0.2.10:36421 completed` ✓
- `==== gNB started ===` ✓

**What's happening:**
- Connects to 5G Core (N2 interface)
- Connects to RIC (E2 interface)
- Creates virtual cell: Band 3, 10 MHz, PCI=1

**Check Terminal 2 (RIC):** Should show `associate-ran-to-e2t` with `ranNamelist: ["gnbd_001_001_00019b_0"]`

**E2 Node ID:** `gnbd_001_001_00019b_0` (you'll need this for xApps)

**Keep this terminal running!**

---

## Terminal 4: Start UE (User Equipment)

**What it does:** Starts simulated phone in network namespace, connects via ZeroMQ virtual radio

```bash
sudo ip netns add ue1
cd ~/srsRAN_4G/build/srsue/src
sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf
```

**Wait for these messages:**
- `Attaching UE.`
- `Random Access Transmission...`
- `Random Access Complete. C-rnti=0x4601`
- `RRC Connected` ✓
- **`PDU Session Establishment successful. IP: 10.45.1.2`** ✓✓

**What's happening:**
- UE performs random access to gNB
- Completes RRC connection
- Gets IP address from core network
- Ready for data transfer

**Success:** UE has IP `10.45.1.2`

**Keep this terminal running!**

---

## Terminal 5: Setup Routes & Test Connectivity

**What it does:** Configures IP routes and verifies end-to-end connectivity

```bash
# Add route from host to UE network
sudo ip ro add 10.45.0.0/16 via 10.53.1.2

# Add default route inside UE namespace
sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue

# Test uplink (UE → Core)
sudo ip netns exec ue1 ping -c 5 10.45.1.1
```

**Expected:** 5 pings succeed, 0% packet loss

```bash
# Test downlink (Host → UE)
ping -c 5 10.45.1.2
```

**Expected:** 5 pings succeed, 0% packet loss

**Success:** Both directions work!

---

## Terminal 6: Start Background Traffic (for xApps)

**What it does:** Generates continuous traffic so xApps can monitor KPIs

```bash
# Continuous ping (generates ~8 kbps uplink)
sudo ip netns exec ue1 ping -i 0.1 10.45.1.1
```

**Keep this running when testing xApps!**

---

## 🎯 Startup Complete!

All components are now running:
- ✅ Core: Open5GS
- ✅ RIC: 7 containers
- ✅ gNB: Connected to Core & RIC
- ✅ UE: IP 10.45.1.2
- ✅ Traffic: Ping running

---

## 🧪 Testing & Monitoring

### View gNB Live Statistics

In Terminal 3 (gNB), type `t` and press Enter:

```
|--------------------DL---------------------|-------------------------UL----------------------------------
 Pci rnti | cqi ri mcs brate ok nok (%) dl_bs | pusch rsrp ri mcs brate ok nok (%) bsr ta phr
 1 4601 | 15 1.0 28  8M 100  0  0%   512k |  4.5  ovl 1  9   8k  10  0  0%  0 520n n/a
```

**Columns explained:**
- `rnti`: Radio Network Temporary Identifier (UE ID)
- `cqi`: Channel Quality Indicator
- `mcs`: Modulation and Coding Scheme
- `brate`: Bitrate (throughput)
- `ok/nok`: Successful/failed transmissions
- `pusch`: Physical Uplink Shared Channel quality

### Test KPM Monitoring (Part I)

Open a new terminal:

```bash
cd ~/oran-sc-ric
docker compose exec python_xapp_runner ./kpm_mon_xapp.py --metrics=DRB.UEThpDl,DRB.UEThpUl --kpm_report_style=5
```

**Expected output every 1 second:**
```
RIC Indication Received from gnbd_001_001_00019b_0 for Subscription ID: 1
--UE_id: 0
---Metric: DRB.UEThpDl, Value: [8.0]
---Metric: DRB.UEThpUl, Value: [8.0]
```

**What this proves:** E2 KPM interface is working, RIC receiving live metrics

Stop with Ctrl+C when done.

### Test RC Control (Part J)

**Terminal A: Start iperf server**
```bash
iperf3 -s -i 1
```

**Terminal B: Start heavy downlink traffic**
```bash
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -i 1 -t 300 -u -b 20M -R
```

**Terminal C: Run RC control xApp**
```bash
cd ~/oran-sc-ric
docker compose exec python_xapp_runner ./simple_rc_xapp.py
```

**Expected:** 
- xApp alternates PRB quota: 30% → 50% → 70%
- Throughput in iperf drops and recovers accordingly
- gNB stats (type `t`) show `brate` changing

**What this proves:** E2 RC control is working, xApps can control the network

Stop all with Ctrl+C when done.

---

## 🛑 Shutdown Procedure

**Always shut down in reverse order:**

1. Stop xApps (Ctrl+C in xApp terminals)
2. Stop UE (Ctrl+C in Terminal 4)
3. Stop gNB (Ctrl+C in Terminal 3) - **Wait 60 seconds before restarting!**
4. Stop RIC (Ctrl+C in Terminal 2)
5. Stop Core (Ctrl+C in Terminal 1)

**Important:** After stopping gNB, the RIC enforces a 60-second cooldown. If you restart gNB too quickly, you'll get `E2 SETUP FAILURE`.

### Clean Shutdown Commands

```bash
# Kill all processes
sudo pkill -9 srsue
sudo pkill -9 gnb

# Stop Docker containers
cd ~/srsRAN_Project/docker && sudo docker compose down
cd ~/oran-sc-ric && sudo docker compose down

# Remove network namespace
sudo ip netns del ue1
```

---

## 🔧 Troubleshooting

### Problem: UE won't connect ("Attaching UE" forever)

**Cause:** gNB not running or crashed

**Solution:**
1. Check Terminal 3 - is gNB still running?
2. Restart gNB (wait 60s after stopping)
3. Restart UE

### Problem: `E2 SETUP FAILURE` in gNB

**Cause:** Restarted gNB within 60 seconds

**Solution:** Wait 60 seconds, then restart gNB

### Problem: `Address already in use` (ZMQ port 2000/2001)

**Cause:** Old gNB or UE process still running

**Solution:**
```bash
sudo pkill -9 gnb
sudo pkill -9 srsue
```
Then restart.

### Problem: Docker permission denied

**Cause:** Docker group not applied to current session

**Solution:**
```bash
newgrp docker
```
Then retry the command.

### Problem: UE has no IP address

**Cause:** SIM not registered in core

**Solution:**
1. Open http://localhost:9999 (admin / 1423)
2. Add subscriber: IMSI `001010123456780`, K `00112233445566778899aabbccddeeff`, OPC `63bfa50ee6523365ff14c1f45f88737d`
3. Restart UE

### Problem: Ping fails

**Cause:** Routes not configured

**Solution:**
```bash
sudo ip ro add 10.45.0.0/16 via 10.53.1.2
sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue
```

### Problem: RIC won't start (port conflicts)

**Cause:** Old containers still running

**Solution:**
```bash
cd ~/oran-sc-ric
sudo docker compose down
sudo docker compose up
```

---

## 📊 Network Architecture Reference

```
┌─────────────────────────────────────────────────────────────┐
│  Host Machine (Ubuntu 22.04 VM)                             │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │ UE (srsUE)   │ ZMQ     │ gNB          │                 │
│  │ Namespace    │◄───────►│ (srsRAN)     │                 │
│  │ 10.45.1.2    │ 2000/   │ 10.53.1.1    │                 │
│  └──────────────┘ 2001    └──────┬───────┘                 │
│                                   │ N2                       │
│  ┌────────────────────────────────┼──────────────────┐      │
│  │ Docker: Open5GS Core           ▼                  │      │
│  │  ┌────────┐  ┌────────┐  ┌────────┐             │      │
│  │  │  AMF   │  │  SMF   │  │  UPF   │             │      │
│  │  │10.53.  │  │        │  │        │             │      │
│  │  │  1.2   │  │        │  │        │             │      │
│  │  └────────┘  └────────┘  └────────┘             │      │
│  └────────────────────────────────────────────────┘      │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │ Docker: oran-sc-ric (10.0.2.0/24)             │         │
│  │                                  E2            │         │
│  │  ┌────────┐  ┌────────┐  ◄──────┘            │         │
│  │  │ e2term │  │ e2mgr  │  10.0.2.10:36421     │         │
│  │  │  .10   │  │  .11   │                       │         │
│  │  └────────┘  └────────┘                       │         │
│  │  ┌────────┐  ┌────────┐  ┌────────┐         │         │
│  │  │ submgr │  │python_ │  │ dbaas  │         │         │
│  │  │  .13   │  │xapp .20│  │  .12   │         │         │
│  │  └────────┘  └────────┘  └────────┘         │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Key Networks:**
- **10.45.0.0/16**: UE data network (UE gets IP from here)
- **10.53.1.0/24**: N2/N3 interface (gNB ↔ Core)
- **10.0.2.0/24**: E2 interface (gNB ↔ RIC)
- **127.0.0.1:2000/2001**: ZMQ virtual radio

---

## 📝 Key File Locations

### Configuration Files
- gNB config: `~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml`
- UE config: `~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf`
- Core compose: `~/srsRAN_Project/docker/docker-compose.yml`
- RIC compose: `~/oran-sc-ric/docker-compose.yml`

### Binaries
- gNB: `~/srsRAN_Project/build/apps/gnb/gnb`
- UE: `~/srsRAN_4G/build/srsue/src/srsue`

### xApp Files (inside container)
- Location: `/opt/xApps/` (inside python_xapp_runner container)
- Examples: `kpm_mon_xapp.py`, `simple_rc_xapp.py`, `simple_xapp.py`
- Your custom xApps: Copy to `~/oran-sc-ric/xApps/python/` before starting RIC

### Logs
- gNB: `/tmp/gnb.log`
- UE: `/tmp/ue.log`
- Core: Docker logs (visible in Terminal 1)
- RIC: Docker logs (visible in Terminal 2)

---

## 🎓 Understanding the System

### What is E2?
E2 is the interface between the RAN (gNB) and the Near-RT RIC. It allows:
- **Monitoring (KPM):** RIC receives live KPIs every 1 second
- **Control (RC):** RIC can adjust RAN parameters (PRB quotas, handover, etc.)

### What are xApps?
xApps are applications running in the RIC that:
1. Subscribe to metrics via E2SM-KPM
2. Process the data (AI/ML, rules, etc.)
3. Send control actions via E2SM-RC

### E2 Service Models Used
- **E2SM-KPM (RAN Function ID 2):** Key Performance Metrics monitoring
  - Report styles: 1-5 (style 4/5 give per-UE data)
  - Available metrics: DRB.UEThpDl, DRB.UEThpUl, DRB.RlcPacketDropRateDl, etc.
  
- **E2SM-RC (RAN Function ID 3):** RAN Control
  - Control Service Style 2, Action 6: Slice-level PRB quota
  - Parameters: min_prb_ratio, max_prb_ratio (0-100%)

### Data Flow
```
UE generates traffic
  ↓
gNB processes and measures
  ↓
E2 KPM: gNB reports metrics to RIC (every 1s)
  ↓
xApp receives metrics, processes with AI/logic
  ↓
E2 RC: xApp sends control action to gNB
  ↓
gNB adjusts parameters (PRB quota, etc.)
  ↓
Network behavior changes
```

---

## 🚀 Next Steps: Phase 2 (ML Training & Custom xApp)

Once the basic system works, proceed to:
1. Collect training data with KPM logger
2. Train LSTM congestion prediction model
3. Deploy custom congestion prediction xApp
4. Run experiments (xApp ON vs OFF)
5. Document results

See `PHASE2_ML_GUIDE.md` for detailed instructions.

---

## 📞 Support

**Common issues documented in:** `SETUP_GUIDE.md` (Troubleshooting section)

**Configuration reference:** `prompt.txt` (original project specification)

**Remember:**
- gNB needs 60s cooldown after stopping
- Always start: Core → RIC → gNB → UE
- Always stop: xApp → UE → gNB → RIC → Core
- Keep traffic running when testing xApps

---

**Last tested:** October 18, 2026  
**System:** Ubuntu 22.04, srsRAN Project release_25_10, srsRAN 4G release_23_11, oran-sc-ric commit 621ade2
