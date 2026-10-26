# O-RAN Congestion Prediction xApp - Quick Setup Guide

**Project Start:** October 18, 2026  
**Goal:** Complete O-RAN xApp with LSTM-based congestion prediction + control loop

## Phase 1: Infrastructure Setup (Days 1-2)

### Current Status: Not Started
**Next Action:** Part A - Windows Environment Check

---

## Part A: Windows Environment Verification

### A1. Check Virtualization
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to Performance → CPU
3. Verify "Virtualization: Enabled"
   - If Disabled: Enable Intel VT-x / AMD SVM in BIOS

### A2. Disable Conflicting Features
1. Start → "Turn Windows features on or off"
2. **UNTICK** these features:
   - [ ] Hyper-V
   - [ ] Virtual Machine Platform
   - [ ] Windows Hypervisor Platform
   - [ ] Windows Subsystem for Linux
3. Click OK → Restart

### A3. Install Visual C++ Redistributable
Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe

### A4. Install VirtualBox
1. Download: https://www.virtualbox.org/wiki/Downloads → "Windows hosts"
2. Right-click installer → Run as administrator
3. Accept defaults → Accept network interruption warnings
4. Restart

### A5. Download Ubuntu 22.04
Download: https://releases.ubuntu.com/22.04/
**Must be:** 64-bit PC (AMD64) desktop image (~5 GB)

---

## Part B: Create VM

**VM Name:** ORAN-Ubuntu  
**Specs:**
- RAM: 8192 MB
- Processors: Half of host cores (minimum 4)
- Disk: 80 GB (dynamic allocation)
- ISO: ubuntu-22.04.x-desktop-amd64.iso
- **Important:** Tick "Skip Unattended Installation"

**Settings:**
- Display → Video Memory: 128 MB, Graphics: VMSVGA, 3D Acceleration: OFF
- Network → Adapter 1: NAT

---

## Part C: Install Ubuntu

1. Start VM → Install Ubuntu
2. Normal installation + Download updates
3. Erase disk and install (VM disk only)
4. Create username/password (SAVE IT!)
5. Reboot when prompted

**After reboot - Install Guest Additions:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential dkms linux-headers-$(uname -r)
```

VM Menu: Devices → Insert Guest Additions CD image
```bash
sudo /media/$USER/VBox_GAs_*/VBoxLinuxAdditions.run
sudo reboot
```

After reboot: View → Auto-resize Guest Display

**Verify:**
```bash
lsb_release -a    # Ubuntu 22.04
nproc             # Check cores
free -h           # ~8 GB
df -h ~           # Free space
```

---

## Part D: Install Dependencies

```bash
# srsRAN Project + ZeroMQ
sudo apt install -y git curl cmake make gcc g++ pkg-config \
  libfftw3-dev libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev libzmq3-dev

# srsRAN 4G
sudo apt install -y libboost-program-options-dev libconfig++-dev

# Tools
sudo apt install -y iperf3 net-tools htop

# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

**Log out and log back in**, then verify:
```bash
docker run hello-world
docker compose version
```

---

## Part E: Clone Software

```bash
cd ~
git clone https://github.com/srsran/srsRAN_Project.git
cd srsRAN_Project && git checkout release_25_10 && cd ~

git clone https://github.com/srsran/srsRAN_4G.git
cd srsRAN_4G && git checkout release_23_11 && cd ~

git clone https://github.com/srsran/oran-sc-ric.git
cd oran-sc-ric && git checkout 621ade2 && cd ~
```

**Verify:**
```bash
cd ~/srsRAN_Project && git describe --tags   # release_25_10
cd ~/srsRAN_4G && git describe --tags        # release_23_11
cd ~/oran-sc-ric && git log -1 --oneline     # 621ade2
```

---

## Part F: Build Everything (1-1.5 hours)

### F1. srsRAN Project (gNB)
```bash
cd ~/srsRAN_Project
mkdir -p build && cd build
cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON 2>&1 | tee cmake_out.txt
grep -i zeromq cmake_out.txt     # MUST show "Found libZEROMQ"
make -j$(nproc)
ls -l apps/gnb/gnb               # Verify binary exists
```

### F2. srsRAN 4G (UE)
```bash
cd ~/srsRAN_4G
mkdir -p build && cd build
cmake ../ 2>&1 | tee cmake_out.txt
grep -i zeromq cmake_out.txt     # Must show ZeroMQ found
make -j$(nproc)
ls -l srsue/src/srsue            # Verify binary exists
```

### F3. Docker Images
```bash
cd ~/srsRAN_Project/docker && docker compose build 5gc
cd ~/oran-sc-ric && docker compose build
```

---

## Part G: Test 5G Network

**Order:** Core → gNB → UE

### Terminal 1: 5G Core
```bash
cd ~/srsRAN_Project/docker
docker compose up 5gc
```

### Terminal 2: gNB
```bash
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
```
Expect: `==== gNB started ===`

### Terminal 3: UE
```bash
sudo ip netns add ue1
cd ~/srsRAN_4G/build/srsue/src
sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf
```
Expect: `PDU Session Establishment successful. IP: 10.45.1.2`

### Terminal 4: Test Connectivity
```bash
sudo ip ro add 10.45.0.0/16 via 10.53.1.2
sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue

sudo ip netns exec ue1 ping -c 5 10.45.1.1
ping -c 5 10.45.1.2
```

**Throughput Test:**
```bash
# Terminal 4
iperf3 -s -i 1

# Terminal 5
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -i 1 -t 60 -u -b 10M
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -i 1 -t 60 -u -b 20M -R
```

**Shutdown:** Ctrl+C: UE → gNB → Core

---

## Part H-J: RIC Setup (Day 2)

### Full Startup Order: Core → RIC → gNB → UE

### Terminal 1: Core
```bash
cd ~/srsRAN_Project/docker && docker compose up 5gc
```

### Terminal 2: RIC
```bash
cd ~/oran-sc-ric
docker compose up
```
Wait for: `RMR is ready now ...`

### Terminal 3: gNB
```bash
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
```
Note the E2 node ID from RIC logs (default: `gnbd_001_001_00019b_0`)

### Terminal 4: UE + Routes
```bash
sudo ip netns add ue1
cd ~/srsRAN_4G/build/srsue/src
sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf
```

In another tab:
```bash
sudo ip ro add 10.45.0.0/16 via 10.53.1.2
sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue
sudo ip netns exec ue1 ping -i 0.1 10.45.1.1
```

### Terminal 5: Test KPM Monitoring
```bash
cd ~/oran-sc-ric
docker compose exec python_xapp_runner ./kpm_mon_xapp.py --metrics=DRB.UEThpDl,DRB.UEThpUl --kpm_report_style=5
```
Should print KPIs every 1 second.

### Test RC Control
```bash
# Start heavy downlink
iperf3 -s -i 1
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -i 1 -t 300 -u -b 20M -R

# Run RC xApp
docker compose exec python_xapp_runner ./simple_rc_xapp.py
```
Type `t` in gNB terminal - watch DL brate drop/recover.

---

## Phase 2: LSTM Model & xApp Development

### Next Steps:
1. Create KPM logger to collect training data
2. Design LSTM model (8 features, 10-timestep window)
3. Train model on normal vs congested traffic
4. Build prediction xApp
5. Build control xApp
6. Test closed loop

---

## Quick Reference

### Available E2 Metrics (KPM):
- DRB.UEThpDl, DRB.UEThpUl
- DRB.RlcSduTransmittedVolumeDL, DRB.RlcSduTransmittedVolumeUL
- DRB.RlcPacketDropRateDl
- DRB.PacketSuccessRateUlgNBUu

### Control Action (RC):
- Service Style 2, Action ID 6: Slice-level PRB quota
- Acts on downlink PRBs
- Range: min_prb_ratio, max_prb_ratio (0-100)

### Key Addresses:
- Open5GS Core: 10.53.1.2:38412
- RIC E2 Termination: 10.0.2.10:36421
- xApp Runner: 10.0.2.20
- UE IP: 10.45.1.2
- Open5GS Web UI: http://localhost:9999 (admin/1423)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Virtualization disabled | Enable VT-x/AMD-V in BIOS |
| ZeroMQ not found | `sudo apt install libzmq3-dev`, rebuild |
| Build killed | Out of RAM → `make -j2` |
| Docker permission denied | Log out and back in after usermod |
| E2 SETUP FAILURE | Wait 60s after stopping gNB |
| xApp no output | Restart xApp once, ensure traffic running |

---

**Status Legend:**
- ✅ Complete
- ⏳ In Progress  
- ⏸️ Blocked
- ❌ Failed
- ⏹️ Not Started
