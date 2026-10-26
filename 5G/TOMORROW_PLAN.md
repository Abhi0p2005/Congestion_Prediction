# Tomorrow's Action Plan - E6 Phase Start
**Date:** October 18, 2026, 8:38 PM  
**Read this before starting work tomorrow morning**

---

## 🎯 What Changed

You received critical feedback from your dataset team partner:

### The Problem We Had:
- ❌ Old code assumed 1-second intervals (wrong - should be 250ms)
- ❌ Old code used only 2 metrics (wrong - should be 6)
- ❌ Old code labeled "normal vs congested" (wrong - should use delivered/offered formula)
- ❌ Old code trained on our testbed data (wrong - we only test, don't train)

### Why This Matters:
- **Training on our data breaks the sim-to-reality claim** - the whole point is proving their simulation-trained model works on OUR hardware without retraining
- **Schema mismatch** means our data won't be usable for their analysis
- **Wrong intervals/metrics** = incompatible with their datasets

### What We Fixed:
- ✅ Deleted all incorrect code
- ✅ Created **PHASE2_E6_GUIDE.md** with 6 validation steps
- ✅ Updated README to explain our role correctly
- ✅ Prepared step-by-step process with dataset team checkpoints

---

## 📋 Tomorrow's Work (Steps 1-2 Only)

### Step 1: Verify 250ms KPM Reporting (30 min)
**Goal:** Confirm gNB outputs all 6 measurements every 250ms

**What to do:**
1. Modify `gnb_zmq.yaml`: change `du_report_period: 1000` → `250`
2. Start testbed (6 terminals as usual)
3. Generate traffic (UE ping or iperf)
4. Check gNB JSON metrics every 250ms
5. Verify these fields exist: `cqi`, `pusch_snr_db`, `dl_brate`, `ul_brate`, `ul_nof_ok`, `ul_nof_nok`, `dl_bs`
6. Save 1-minute sample as `step1_sample_250ms.json`

**Success:** JSON metrics appear every 250ms with all 6 fields

**Deliverable:** `step1_sample_250ms.json`

---

### Step 2: Confirm CQI Table (15 min)
**Goal:** Verify gNB uses 64-QAM (CQI 0-15, not 256-QAM)

**What to do:**
1. Check `gnb_zmq.yaml` for `mcs_table: qam64`
2. Run traffic and watch CQI values
3. Document: is CQI range 0-15? (yes = correct)
4. Create `step2_cqi_verification.txt` with findings

**Success:** CQI values are between 0-15

**Deliverable:** `step2_cqi_verification.txt`

---

## ⚠️ CRITICAL: Wait for Dataset Team Approval

**After completing Steps 1-2:**
1. Send both deliverables to dataset team
2. **DO NOT PROCEED** to Steps 3-4 until they confirm
3. They will check:
   - Are the JSON fields exactly what they expect?
   - Is the CQI table correct?
   - Can they parse the data format?

**Why wait?** If we collect data in wrong format, it's wasted effort.

---

## 📁 Files You Need Tomorrow

**Read/Reference:**
- `PHASE2_E6_GUIDE.md` - Detailed 6-step guide
- `RUN_GUIDE.md` - How to start testbed
- `README.md` - Project overview

**Keep backed up:**
- `gnb_zmq.yaml` - Your working gNB config
- `ue_zmq_simple.conf` - Your working UE config

**Deleted (don't try to use):**
- ~~train_model.py~~ (we don't train)
- ~~analyze_results.py~~ (we don't analyze)
- ~~test_experiment.sh~~ (wrong schema)
- ~~kpm_logger_xapp.py~~ (wrong format)
- ~~congestion_prediction_xapp.py~~ (premature)

---

## 🚀 Tomorrow's Timeline

### 9:00 AM - Start Testbed
- Terminal 1: Core
- Terminal 2: RIC
- Terminal 3: gNB (with 250ms reporting enabled)
- Terminal 4: UE
- Terminal 5: Routes
- Terminal 6: Traffic generator

### 9:15 AM - Run Step 1
- Check metrics every 250ms
- Extract sample
- Save `step1_sample_250ms.json`

### 9:45 AM - Run Step 2
- Check CQI values
- Document findings
- Save `step2_cqi_verification.txt`

### 10:00 AM - Send to Dataset Team
- Email/message with both files
- Wait for approval before proceeding
- Use this time to review PHASE2_E6_GUIDE.md for Steps 3-6

---

## 🎓 Key Concept: E6 Experiment

```
Dataset Team's Work              Your Work (Testbed)
═════════════════════════════════════════════════════════
Simulation Data (E1-E5)          Our Testbed Data (E6)
   ↓                                    ↑
Train Models                     [Don't train, just collect]
   ↓
Test on:
- E2: Sim → TRACTOR real        
- E4: TRACTOR → TRACTOR         
- E6: Sim → OUR TESTBED  ◄───────────────────────────
   ↓
Compare E6 vs E4 = Sim-to-Reality Transfer Gap
```

**Your role:** Provide the E6 test set. Nothing else.

---

## ✅ Success Criteria for Steps 1-2

- [ ] 250ms JSON metrics from gNB
- [ ] All 6 required fields present
- [ ] CQI values 0-15 confirmed
- [ ] Dataset team approves format
- [ ] No errors in Step 1 sample
- [ ] No CQI table mismatches

---

## 🆘 If Something Goes Wrong

**No JSON metrics:**
- Check: `enable_json: true` in gnb_zmq.yaml
- Check: Traffic is actually running (ping or iperf)
- Try: Restart gNB with updated config

**Wrong CQI values:**
- Check: `mcs_table: qam64` in gnb_zmq.yaml
- Try: Restart gNB

**Can't modify config:**
- Check: Correct path? `~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml`
- Try: `cat gnb_zmq.yaml | grep du_report_period`

**Dataset team says format wrong:**
- Ask them: What exactly is different?
- Adjust collector based on their feedback
- Re-collect sample

---

## 📞 Dataset Team Communication

**Email template for tomorrow:**

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
- Any adjustments needed?

Ready to proceed once you confirm.
```

---

## 📊 What's Next (After Approval)

### Steps 3-4 (Multi-UE & Capacity)
- Setup 3 UEs
- Measure max cell throughput
- Confirm cell saturates properly

### Steps 5-6 (Data Collection)
- Build proper collector in dataset team's schema
- Collect 10-minute sample
- Get their final validation

### Full Collection
- Collect complete E6 dataset
- Multiple scenarios
- Send to dataset team
- They run E6 experiment
- Compare E6 vs E4 results

---

## 🎯 The Big Picture

You're at the **Go/No-Go checkpoint**. You passed! ✅

Now comes the **data validation phase**:
1. Prove our testbed can collect the right measurements (Steps 1-2)
2. Prove we can handle multiple UEs (Steps 3-4)
3. Provide dataset team with clean, usable data (Steps 5-6)
4. Their trained model gets tested on our data (E6 experiment)
5. Measure how well simulation transfers to reality

This is the **key validation** for the entire project.

---

## 📋 Quick Checklist Before Bed

- [ ] Read PHASE2_E6_GUIDE.md completely
- [ ] Understand Steps 1-2 (what exactly to do)
- [ ] Have dataset team contact info ready
- [ ] Know what `step1_sample_250ms.json` should contain
- [ ] Know what `step2_cqi_verification.txt` should contain
- [ ] Understand why we WAIT after Step 2

---

**See you tomorrow morning. Let's collect E6 data! 🚀**

One step at a time. Validate at each checkpoint. Don't skip ahead.
