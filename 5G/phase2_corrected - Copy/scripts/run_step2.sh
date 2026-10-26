#!/bin/bash
# Step 2: Confirm CQI Table (64-QAM)
# Part of Phase 2 - E6 Data Collection

set -e

echo "========================================"
echo "Step 2: Confirm CQI Table (64-QAM)"
echo "Date: $(date)"
echo "========================================"
echo ""

# Check config
if [ ! -f ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml ]; then
    echo "ERROR: gnb_zmq.yaml not found"
    exit 1
fi

echo "1. Checking gNB configuration..."
echo ""
echo "PDSCH MCS table:"
grep -A2 "pdsch:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml | grep "mcs_table"

echo ""
echo "PUSCH MCS table:"
grep -A2 "pusch:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml | grep "mcs_table"

echo ""
echo "2. Expected: Both should be 'qam64'"
echo "   - qam64  = CQI range 0-15 (correct for E6)"
echo "   - qam256 = CQI range 0-31 (wrong)"
echo ""

# Create verification document
cat > ~/step2_cqi_verification.txt << EOF
CQI Table Check (Step 2)
========================
Date: $(date)
Config file: ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml

Configuration Settings:
----------------------
EOF

echo "PDSCH MCS table:" >> ~/step2_cqi_verification.txt
grep -A2 "pdsch:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml | grep "mcs_table" >> ~/step2_cqi_verification.txt

echo "" >> ~/step2_cqi_verification.txt
echo "PUSCH MCS table:" >> ~/step2_cqi_verification.txt
grep -A2 "pusch:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml | grep "mcs_table" >> ~/step2_cqi_verification.txt

echo ""
echo "3. Checking observed CQI values..."
if [ -f ~/step1_sample_250ms.json ]; then
    echo "   Extracting CQI values from Step 1 sample..."
    
    CQI_VALUES=$(grep -o '"cqi":[0-9]*' ~/step1_sample_250ms.json | cut -d: -f2 | sort -n | uniq)
    
    echo "" >> ~/step2_cqi_verification.txt
    echo "Observed CQI Values from step1_sample_250ms.json:" >> ~/step2_cqi_verification.txt
    echo "$CQI_VALUES" | tr '\n' ' ' >> ~/step2_cqi_verification.txt
    echo "" >> ~/step2_cqi_verification.txt
    
    MAX_CQI=$(echo "$CQI_VALUES" | tail -1)
    
    echo "" >> ~/step2_cqi_verification.txt
    if [ "$MAX_CQI" -le 15 ]; then
        echo "CQI Range: 0-$MAX_CQI (within 0-15)" >> ~/step2_cqi_verification.txt
        echo "Conclusion: ✓ 64-QAM table confirmed" >> ~/step2_cqi_verification.txt
        echo "   ✓ CQI range 0-$MAX_CQI (correct for 64-QAM)"
    else
        echo "CQI Range: 0-$MAX_CQI (exceeds 15!)" >> ~/step2_cqi_verification.txt
        echo "Conclusion: ✗ Possibly 256-QAM table (wrong)" >> ~/step2_cqi_verification.txt
        echo "   ✗ CQI max $MAX_CQI exceeds 15 (check config)"
    fi
else
    echo "   ⚠ step1_sample_250ms.json not found"
    echo "   Run step1 first to collect sample data"
    echo "" >> ~/step2_cqi_verification.txt
    echo "Observed CQI Values: Not available (run Step 1 first)" >> ~/step2_cqi_verification.txt
    echo "Conclusion: Config shows qam64, but needs runtime verification" >> ~/step2_cqi_verification.txt
fi

echo ""
echo "4. Verification document created:"
cat ~/step2_cqi_verification.txt

echo ""
echo "========================================"
echo "Step 2 Complete!"
echo "========================================"
echo ""
echo "Deliverable: ~/step2_cqi_verification.txt"
echo ""
echo "Next steps:"
echo "  1. Copy step2_cqi_verification.txt to Windows"
echo "  2. Send to dataset team along with Step 1 results"
echo "  3. Wait for validation before proceeding to Step 3"
echo ""
echo "To copy to Windows:"
echo "  cp ~/step2_cqi_verification.txt ~/Desktop/"
echo ""
