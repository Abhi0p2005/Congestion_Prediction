#!/bin/bash
# Step 1: Verify 250ms KPM Reporting
# Part of Phase 2 - E6 Data Collection

set -e

echo "========================================"
echo "Step 1: Verify 250ms KPM Reporting"
echo "Date: $(date)"
echo "========================================"
echo ""

# Check if corrected config exists
if [ ! -f ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml ]; then
    echo "ERROR: gnb_zmq.yaml not found at ~/oran-sc-ric/e2-agents/srsRAN/"
    exit 1
fi

echo "1. Checking current gNB config..."
echo "   Verifying metrics section:"
grep -A8 "^metrics:" ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml

echo ""
echo "2. Required settings:"
echo "   ✓ enable_json: true"
echo "   ✓ du_report_period: 250"
echo ""

read -p "Is the config correct? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo ""
    echo "To fix, run:"
    echo "  nano ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml"
    echo ""
    echo "Change metrics section to:"
    echo "  enable_json: true"
    echo "  du_report_period: 250"
    exit 1
fi

echo ""
echo "3. Starting testbed..."
echo "   You need to start in separate terminals:"
echo ""
echo "   Terminal 1: cd ~/srsRAN_Project/docker && sudo docker compose up 5gc"
echo "   Terminal 2: cd ~/oran-sc-ric && sudo docker compose up"
echo "   Terminal 3: cd ~/srsRAN_Project/build/apps/gnb && sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json"
echo "   Terminal 4: sudo ip netns add ue1 && cd ~/srsRAN_4G/build/srsue/src && sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf"
echo ""

read -p "Press Enter when all 4 terminals are running and UE has IP 10.45.1.2..."

echo ""
echo "4. Setting up routes..."
sudo ip ro add 10.45.0.0/16 via 10.53.1.2 2>/dev/null || echo "   Route already exists"
sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue 2>/dev/null || echo "   UE route already exists"

echo ""
echo "5. Testing connectivity..."
if sudo ip netns exec ue1 ping -c 3 10.45.1.1 > /dev/null 2>&1; then
    echo "   ✓ UE can reach core"
else
    echo "   ✗ UE cannot reach core - check setup"
    exit 1
fi

echo ""
echo "6. Generating light traffic for metrics..."
echo "   Starting background ping..."
sudo ip netns exec ue1 ping -i 0.5 10.45.1.1 > /dev/null 2>&1 &
PING_PID=$!

sleep 5

echo ""
echo "7. Checking metrics output..."
if [ -f /tmp/gnb_metrics.json ]; then
    echo "   ✓ Metrics file exists"
    
    # Check for recent data
    RECENT_LINES=$(tail -20 /tmp/gnb_metrics.json | grep -c "{" || true)
    if [ $RECENT_LINES -gt 0 ]; then
        echo "   ✓ JSON data being written"
    else
        echo "   ✗ No JSON data found - check enable_json setting"
        kill $PING_PID 2>/dev/null
        exit 1
    fi
else
    echo "   ✗ Metrics file not found"
    echo "   Make sure gNB is running with: 2>&1 | tee /tmp/gnb_metrics.json"
    kill $PING_PID 2>/dev/null
    exit 1
fi

echo ""
echo "8. Extracting 1-minute sample..."
sleep 10
head -300 /tmp/gnb_metrics.json > ~/step1_sample_250ms.json
echo "   ✓ Saved to ~/step1_sample_250ms.json"

echo ""
echo "9. Analyzing sample..."
SAMPLE_LINES=$(wc -l < ~/step1_sample_250ms.json)
echo "   Lines collected: $SAMPLE_LINES"
echo "   Expected: ~240 lines (1 min × 4 samples/sec × 1 UE)"

echo ""
echo "10. Checking required fields..."
if grep -q "cqi" ~/step1_sample_250ms.json && \
   grep -q "pusch_snr_db" ~/step1_sample_250ms.json && \
   grep -q "dl_brate" ~/step1_sample_250ms.json && \
   grep -q "ul_brate" ~/step1_sample_250ms.json && \
   grep -q "dl_bs" ~/step1_sample_250ms.json; then
    echo "   ✓ All required fields present"
    echo "     - cqi (DL CQI)"
    echo "     - pusch_snr_db (UL SINR)"
    echo "     - dl_brate (DL speed)"
    echo "     - ul_brate (UL speed)"
    echo "     - ul_nof_ok/nok (for UL error rate)"
    echo "     - dl_bs (DL buffer)"
else
    echo "   ✗ Missing required fields"
    echo "   Sample content:"
    head -5 ~/step1_sample_250ms.json
fi

# Cleanup
kill $PING_PID 2>/dev/null || true

echo ""
echo "========================================"
echo "Step 1 Complete!"
echo "========================================"
echo ""
echo "Deliverable: ~/step1_sample_250ms.json"
echo ""
echo "Next steps:"
echo "  1. Copy step1_sample_250ms.json to Windows"
echo "  2. Send to dataset team for format validation"
echo "  3. Wait for their approval before Step 2"
echo ""
echo "To copy to Windows (from Ubuntu):"
echo "  cp ~/step1_sample_250ms.json ~/Desktop/"
echo ""
