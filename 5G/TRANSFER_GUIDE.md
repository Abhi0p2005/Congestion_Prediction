# O-RAN Project Transfer Guide - Give to a Friend

**Purpose:** Complete instructions to transfer this working O-RAN project to another person

**Transfer Methods:** 
1. VM Export (Fastest - 30 min)
2. Fresh Setup (Most reliable - 4-6 hours)

---

## Method 1: VM Export (Recommended for Quick Transfer)

### What You Give Them

**1. VM Export File (~40-50 GB)**
- Entire Ubuntu VM with everything pre-built
- **Your friend needs:** VMware Workstation Pro or VirtualBox

### Steps to Export (Your Side)

#### If using VMware:
1. Shut down the VM completely (not suspend)
2. VMware → File → Export to OVF
3. Choose location with 50GB+ free space
4. Export as `.ova` file (takes 20-30 min)
5. Transfer the `.ova` file to your friend (USB drive, cloud, etc.)

#### If using VirtualBox:
1. Shut down the VM completely
2. VirtualBox → File → Export Appliance
3. Select `ORAN-Ubuntu` VM
4. Format: OVF 2.0
5. Save as `.ova` file
6. Transfer to your friend

### Steps to Import (Their Side)

#### If they have VMware:
1. Install VMware Workstation Pro (or Player)
2. VMware → File → Open
3. Select your `.ova` file
4. Import with these settings:
   - RAM: 8GB (minimum)
   - CPUs: 4+ cores
   - Network: NAT
5. Start the VM
6. Login with your credentials
7. **Change password:** `passwd` command

#### If they have VirtualBox:
1. Install VirtualBox 7.x
2. VirtualBox → File → Import Appliance
3. Select your `.ova` file
4. Keep default settings (8GB RAM, 8 CPU cores)
5. Import
6. Start VM
7. Login and change password

### What to Tell Them

**Username:** `[your username]`  
**Password:** `[your password]` (tell them to change it)

**To test the system:**
```bash
# Check everything is built
ls -l ~/srsRAN_Project/build/apps/gnb/gnb
ls -l ~/srsRAN_4G/build/srsue/src/srsue
docker images

# Read the run guide
cd ~/
cat RUN_GUIDE.md
```

**Give them these files from Windows:**
- `RUN_GUIDE.md` (how to run)
- `SETUP_GUIDE.md` (reference)
- `README.md` (project overview)

---

## Method 2: Fresh Setup (Most Reliable)

### What You Give Them

**Package these files together:**

#### 1. Documentation (from `C:\College\Project\5G\`)
- `SETUP_GUIDE.md` - Complete setup instructions
- `RUN_GUIDE.md` - How to run after setup
- `README.md` - Project overview
- `TRANSFER_GUIDE.md` - This file
- `prompt.txt` - Original specification

#### 2. Code Files
- `ubuntu_setup.sh` - Automated setup script
- `kpm_logger_xapp.py` - Data collection xApp
- `train_model.py` - LSTM training script
- `congestion_prediction_xapp.py` - Main prediction xApp
- `analyze_results.py` - Results analysis
- `test_experiment.sh` - Automated testing

#### 3. Configuration Files (if modified)
- `gnb_zmq_simple.yaml` - Simple gNB config (if you created it)
- `ue_zmq_simple.conf` - Simple UE config (if you created it)

### Their Setup Process (4-6 hours)

**Step 1: Prepare Windows (30 min)**
- Follow `SETUP_GUIDE.md` Part A
- Enable virtualization in BIOS
- Install VMware Workstation Pro or VirtualBox
- Download Ubuntu 22.04 ISO

**Step 2: Create VM (10 min)**
- Follow `SETUP_GUIDE.md` Part B
- 8GB RAM, 8 CPU cores, 80GB disk, NAT network

**Step 3: Install Ubuntu (30 min)**
- Follow `SETUP_GUIDE.md` Part C
- Install guest tools

**Step 4: Automated Build (2 hours)**
- Transfer `ubuntu_setup.sh` to VM
- Run: `chmod +x ubuntu_setup.sh && ./ubuntu_setup.sh`
- Wait for completion

**Step 5: Test (30 min)**
- Follow `RUN_GUIDE.md` startup procedure
- Verify all components work

---

## Method 3: GitHub Repository (For Collaboration)

### Create a Repository

**Structure:**
```
5G-ORAN-xApp/
├── README.md
├── docs/
│   ├── SETUP_GUIDE.md
│   ├── RUN_GUIDE.md
│   ├── TRANSFER_GUIDE.md
│   └── prompt.txt
├── scripts/
│   ├── ubuntu_setup.sh
│   └── test_experiment.sh
├── xApps/
│   ├── kpm_logger_xapp.py
│   ├── congestion_prediction_xapp.py
│   └── analyze_results.py
├── ml/
│   └── train_model.py
├── configs/
│   ├── gnb_zmq_simple.yaml
│   └── ue_zmq_simple.conf
└── .gitignore
```

**Important:** Don't commit large binaries or built files!

**.gitignore:**
```
# Binaries
*.o
*.so
*.a
gnb
srsue

# Build directories
build/
cmake-build-*/

# VM files
*.ova
*.vmdk
*.vdi

# Logs
*.log
*.pcap

# Data
*.csv
kpm_log.csv

# Models
*.h5
*.pkl

# Temporary
tmp/
/tmp/
```

### Their Process
```bash
git clone https://github.com/your-username/5G-ORAN-xApp.git
cd 5G-ORAN-xApp
# Follow docs/SETUP_GUIDE.md
```

---

## What to Explain to Your Friend

### System Requirements
**Minimum:**
- Windows 10/11 with 16GB RAM (they'll allocate 8GB to VM)
- 4-core CPU with virtualization support
- 100GB free disk space
- VMware Workstation Pro or VirtualBox 7.x

**Recommended:**
- 32GB RAM (better performance)
- 8-core CPU
- 200GB free space
- Good internet for downloads

### Time Commitment

**Method 1 (VM Export):**
- Transfer time: Depends on method (USB: 1 hour, cloud: varies)
- Import time: 15-30 minutes
- Testing: 30 minutes
- **Total: 2-3 hours**

**Method 2 (Fresh Setup):**
- Preparation: 1 hour
- Installation: 30 minutes
- Automated build: 2 hours
- Testing: 30 minutes
- **Total: 4-6 hours**

### Technical Skills Required

**Basic (for Method 1):**
- Install hypervisor (VMware/VirtualBox)
- Import VM
- Basic Linux terminal use

**Intermediate (for Method 2):**
- Enable BIOS virtualization
- Create VM from ISO
- Use Linux terminal
- Run shell scripts
- Troubleshoot errors

### What Works Out of the Box

**After successful transfer:**
- ✅ 5G Core (Open5GS)
- ✅ RIC (7 Docker containers)
- ✅ gNB with E2 interface
- ✅ UE connection
- ✅ Example xApps (KPM monitoring, RC control)
- ✅ All dependencies installed
- ✅ Docker configured
- ✅ Network namespaces set up

**What they need to do:**
- Start components in correct order (see `RUN_GUIDE.md`)
- Generate traffic for testing
- Optionally: train ML model and deploy custom xApp

---

## Transfer Checklist

### Before Transfer

**Your Side:**
- [ ] VM is shut down completely (not suspended)
- [ ] All terminals closed inside VM
- [ ] VM exported successfully
- [ ] Export file tested (try importing yourself)
- [ ] All documentation files collected
- [ ] Code files collected
- [ ] Transfer method decided (USB drive, cloud, etc.)

### Documentation to Include

- [ ] `SETUP_GUIDE.md` - Complete setup reference
- [ ] `RUN_GUIDE.md` - How to run the project
- [ ] `TRANSFER_GUIDE.md` - This file
- [ ] `README.md` - Project overview
- [ ] `prompt.txt` - Original requirements

### Information to Share

**System Credentials:**
- VM username: `_______`
- VM password: `_______` (tell them to change it)
- Open5GS web UI: http://localhost:9999 (admin / 1423)

**Important Details:**
- E2 Node ID: `gnbd_001_001_00019b_0`
- UE IP: `10.45.1.2`
- RIC E2 endpoint: `10.0.2.10:36421`
- Core AMF: `10.53.1.2:38412`

**Key Versions:**
- Ubuntu: 22.04 LTS
- srsRAN Project: release_25_10
- srsRAN 4G: release_23_11
- oran-sc-ric: commit 621ade2

---

## Post-Transfer Support

### First Test Together

**Walk them through:**
1. Start VM
2. Login
3. Open terminals
4. Run startup procedure from `RUN_GUIDE.md`
5. Verify UE gets IP `10.45.1.2`
6. Run KPM monitoring test
7. Run RC control test

### Common Issues After Transfer

**Problem: VM won't start**
- Check virtualization enabled in BIOS
- Check host has enough RAM available
- Try allocating less RAM (6GB minimum)

**Problem: Networking doesn't work**
- Ensure VM network is set to NAT
- Check firewall isn't blocking ports
- Restart VM

**Problem: "Docker permission denied"**
```bash
newgrp docker
```

**Problem: Old processes still running**
```bash
sudo pkill -9 srsue
sudo pkill -9 gnb
sudo ip netns del ue1
```

### Help Them Learn

**Give them these references:**
- [srsRAN Project Docs](https://docs.srsran.com/projects/project/en/latest/)
- [O-RAN Alliance Specs](https://www.o-ran.org/specifications)
- Your contact info for questions

---

## Quick Start for Your Friend

**After importing VM:**

```bash
# 1. Check everything is there
ls -l ~/srsRAN_Project/build/apps/gnb/gnb
ls -l ~/srsRAN_4G/build/srsue/src/srsue
docker images

# 2. Read the run guide
cat ~/RUN_GUIDE.md

# 3. Open 6 terminals and follow RUN_GUIDE.md startup procedure

# 4. Test basic connectivity
sudo ip netns exec ue1 ping -c 5 10.45.1.1
ping -c 5 10.45.1.2

# 5. Test KPM monitoring
cd ~/oran-sc-ric
docker compose exec python_xapp_runner ./kpm_mon_xapp.py --metrics=DRB.UEThpDl,DRB.UEThpUl --kpm_report_style=5

# Success! System is working
```

---

## Files Summary

**Essential files to transfer:**

| File | Size | Purpose |
|------|------|---------|
| VM export (.ova) | 40-50 GB | Complete working system |
| SETUP_GUIDE.md | 100 KB | Complete setup instructions |
| RUN_GUIDE.md | 50 KB | How to run the project |
| TRANSFER_GUIDE.md | 30 KB | This file |
| README.md | 20 KB | Project overview |
| ubuntu_setup.sh | 5 KB | Automated setup script |
| kpm_logger_xapp.py | 2 KB | Data collection xApp |
| train_model.py | 5 KB | ML training |
| congestion_prediction_xapp.py | 7 KB | Main xApp |

**Total transfer size:**
- **Method 1 (VM export):** 40-50 GB
- **Method 2 (Files only):** < 1 MB

---

## Success Criteria

**Your friend's system is working when:**
- ✅ All 6 terminals start without errors
- ✅ UE gets IP 10.45.1.2
- ✅ Ping works both directions
- ✅ KPM xApp receives metrics every 1 second
- ✅ RC xApp can control throughput
- ✅ gNB stats show live UE data

**They can now:**
- Run the full O-RAN testbed
- Test E2 monitoring and control
- Develop custom xApps
- Train and deploy ML models
- Run experiments

---

## Alternative: Cloud VM Transfer

If file size is an issue, consider uploading the VM to:
- Google Drive (15GB free, more with paid)
- Dropbox
- AWS S3 (pay per GB)
- University file server
- Split with 7-Zip into smaller parts

**Split command (Linux):**
```bash
split -b 4G ORAN-Ubuntu.ova ORAN-Ubuntu.ova.part
# Creates: ORAN-Ubuntu.ova.partaa, partab, partac, etc.

# Friend reassembles:
cat ORAN-Ubuntu.ova.part* > ORAN-Ubuntu.ova
```

---

## Legal & Academic Notes

**If this is for academic purposes:**
- Cite the open-source projects: srsRAN, O-RAN SC
- Credit: Your work in integration and ML implementation
- Share within university guidelines
- Don't redistribute without proper attribution

**License compliance:**
- srsRAN Project: AGPLv3
- oran-sc-ric: Apache 2.0
- Your custom code: Specify your own license

---

## Final Checklist for Handoff

**Before giving to friend:**
- [ ] VM exported and tested
- [ ] All documentation prepared
- [ ] Code files collected
- [ ] Credentials documented
- [ ] Test procedure written
- [ ] Your contact info provided
- [ ] Expected behavior documented
- [ ] Known issues listed

**During handoff:**
- [ ] Explain project purpose
- [ ] Show live demonstration
- [ ] Walk through RUN_GUIDE.md
- [ ] Test one complete cycle together
- [ ] Answer initial questions
- [ ] Provide troubleshooting tips

**After handoff:**
- [ ] Available for questions
- [ ] Check in after first week
- [ ] Help with any errors
- [ ] Share any updates/fixes

---

## Contact Info Template

**Fill this out for your friend:**

```
Project: O-RAN Congestion Prediction xApp
Transfer Date: ___________
From: ___________
To: ___________

System Info:
- VM Name: ORAN-Ubuntu
- Username: ___________
- Password: ___________ (change after first login)

Support:
- Your Email: ___________
- Your Phone: ___________
- Best time to ask: ___________

Important Links:
- Project GitHub: ___________
- Google Drive with VM: ___________
- Documentation: ___________

Notes:
___________________________________________
___________________________________________
```

---

**Good luck with the transfer! The system is ready to go.** 🚀
