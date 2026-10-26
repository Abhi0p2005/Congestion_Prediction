# Quick Start Guide - Resume Session (Oct 25, 2026)

**Read this first when you return to work**

---

## 🎯 Where You Left Off

You were running Step 1 validation (`./run_step1.sh`) when the gNB got stuck during startup in Terminal 3.

**Current situation:**
- ✅ Core running (Terminal 1)
- ✅ RIC running (Terminal 2)  
- ⚠️ gNB stuck (Terminal 3)
- ✅ UE connected (Terminal 4)
- ⏸️ Step 1 script waiting for you to press Enter (original terminal)

---

## 🚀 What to Do First (5 minutes)

### Check if everything is still running:

```bash
# Check Docker containers
docker ps -a | grep -E "5gc|ric"

# Check gNB and UE processes
ps aux | grep -E "gnb|srsue"
```

**If containers stopped:** Restart from scratch (see `RUN_GUIDE.md`)

**If still running:** Continue to Step 2 below

---

## 🔧 Step 2: Fix gNB Startup (15 minutes)

**The issue:** gNB hangs when using `2>&1 | tee /tmp/gnb_metrics.json`

**Solution to try:** Run gNB WITHOUT the tee redirect first

### In Terminal 3:

```bash
# If gNB is stuck, press Ctrl+C
# Wait 60 seconds
sleep 60

# Try without tee
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml
```

**Wait for:**
```
==== gNB started ===
```

**Then type:** `t` (and press Enter) to toggle metrics display

**You should see metrics updating every 250ms like:**
```
pci rnti | cqi  mcs  brate   ok  nok  (%)  dl_bs | pusch  mcs  brate
  1 4601 |  15   28    8M   100    0   0%   512k |  4.5    9    8k
```

---

## ✅ Step 3: If Metrics Appear

**Good news!** The gNB works, just not with `tee` redirect.

**Alternative solution:** In a NEW terminal (Terminal 6):

```bash
# Monitor and save metrics in background
tail -f /tmp/gnb.log > ~/gnb_metrics_output.txt &
```

Or use this workaround when starting gNB:

```bash
stdbuf -oL sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json
```

---

## 📋 Step 4: Continue with Step 1 Script

Once gNB is running and showing metrics:

**Go back to the original terminal** where `./run_step1.sh` is waiting

**Press Enter**

The script will automatically:
1. Setup routes
2. Test connectivity
3. Generate traffic  
4. Collect 1-minute sample
5. Create `~/step1_sample_250ms.json`

---

## 📤 Step 5: Complete Step 2 and Send Results

```bash
# Run Step 2
./run_step2.sh

# Copy deliverables to Desktop
cp ~/step1_sample_250ms.json ~/Desktop/
cp ~/step2_cqi_verification.txt ~/Desktop/
```

**Drag both files from Ubuntu Desktop to Windows:**
`C:\College\Project\5G\deliverables\`

**Send to dataset team** (see email template in `TOMORROW_CONTINUATION.md`)

---

## ⏸️ Then STOP and WAIT

**Do NOT proceed to Steps 3-6 until dataset team validates Steps 1-2**

This is critical - if the format is wrong, you'll waste time collecting bad data.

---

## 📞 If Something Goes Wrong

### Testbed stopped working
- See `RUN_GUIDE.md` to restart from scratch
- Remember: Core → RIC → gNB (wait for started) → UE

### gNB still won't start
- Check ports: `sudo netstat -tulpn | grep 2000`
- Check logs: `cat /tmp/gnb.log | tail -50`
- May need to restart UE too

### Can't find the files
- All scripts are in `~/` (home directory)
- Config is at `~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml`
- Documentation is in `C:\College\Project\5G\` on Windows

---

## 📚 Reference Documents

- `TOMORROW_CONTINUATION.md` - Full detailed context
- `CLI_CONTEXT_TOMORROW.md` - Context for CLI assistant
- `phase2_corrected/README_IMPLEMENTATION.md` - Complete guide
- `RUN_GUIDE.md` - How to start testbed
- `PHASE2_E6_GUIDE.md` - Detailed step-by-step

---

## ✅ Success = Today's Goal Achieved

**Minimum success criteria:**
- [x] gNB outputs metrics
- [x] Step 1 complete (1-min sample)
- [x] Step 2 complete (CQI verified)
- [x] Files sent to dataset team

**You're on track as long as you get Steps 1-2 validated today!**

---

**Time estimate:** 1-2 hours if gNB fix works quickly

**Good luck!** 🚀
