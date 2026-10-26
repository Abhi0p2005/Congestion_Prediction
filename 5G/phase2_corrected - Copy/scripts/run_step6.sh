#!/bin/bash
# Step 6: Collect 10-Minute Validation Sample
# Part of Phase 2 - E6 Data Collection

set -e

echo "========================================"
echo "Step 6: Collect 10-Minute Validation Sample"
echo "Date: $(date)"
echo "========================================"
echo ""

# Prerequisites check
if [ ! -f ~/testbed_collector.py ]; then
    echo "ERROR: testbed_collector.py not found"
    echo "Copy it from phase2_corrected/scripts/"
    exit 1
fi

if [ ! -f /tmp/gnb_metrics.json ]; then
    echo "ERROR: gNB not running with JSON metrics"
    echo "Start gNB with: sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json"
    exit 1
fi

echo "1. Starting 10-minute scenario collection..."
echo "   Scenario breakdown:"
echo "     Minutes 0-3:  Light load (2 Mbps/UE)"
echo "     Minutes 3-6:  Medium load (10 Mbps/UE)"
echo "     Minutes 6-10: Heavy load (30 Mbps/UE - should cause starvation)"
echo ""

# Start collector in background
echo "2. Starting data collector..."
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py ~/e6_sample_10min.csv --rates ue1=2M,ue2=2M,ue3=2M &
COLLECTOR_PID=$!
sleep 2

echo "   ✓ Collector started (PID: $COLLECTOR_PID)"
echo ""

# Start iperf3 servers in background
echo "3. Starting iperf3 servers..."
iperf3 -s -p 5201 -D
iperf3 -s -p 5202 -D
iperf3 -s -p 5203 -D
sleep 1
echo "   ✓ Servers running on ports 5201-5203"
echo ""

# Minutes 0-3: Light load
echo "4. [00:00-03:00] Light load phase (2 Mbps/UE)..."
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 2M -t 180 -R > /dev/null 2>&1 &
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 2M -t 180 -R > /dev/null 2>&1 &
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 2M -t 180 -R > /dev/null 2>&1 &

for i in {1..18}; do
    echo -n "."
    sleep 10
done
echo " Done (3 min)"
echo ""

# Update collector rates for medium load
kill $COLLECTOR_PID
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py ~/e6_sample_10min.csv --rates ue1=10M,ue2=10M,ue3=10M &
COLLECTOR_PID=$!

# Minutes 3-6: Medium load
echo "5. [03:00-06:00] Medium load phase (10 Mbps/UE)..."
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 10M -t 180 -R > /dev/null 2>&1 &
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 10M -t 180 -R > /dev/null 2>&1 &
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 10M -t 180 -R > /dev/null 2>&1 &

for i in {1..18}; do
    echo -n "."
    sleep 10
done
echo " Done (6 min total)"
echo ""

# Update collector rates for heavy load
kill $COLLECTOR_PID
tail -f /tmp/gnb_metrics.json | python3 ~/testbed_collector.py ~/e6_sample_10min.csv --rates ue1=30M,ue2=30M,ue3=30M &
COLLECTOR_PID=$!

# Minutes 6-10: Heavy load
echo "6. [06:00-10:00] Heavy load phase (30 Mbps/UE - expect congestion)..."
sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b 30M -t 240 -R > /dev/null 2>&1 &
sudo ip netns exec ue2 iperf3 -c 10.53.1.1 -p 5202 -u -b 30M -t 240 -R > /dev/null 2>&1 &
sudo ip netns exec ue3 iperf3 -c 10.53.1.1 -p 5203 -u -b 30M -t 240 -R > /dev/null 2>&1 &

for i in {1..24}; do
    echo -n "."
    sleep 10
done
echo " Done (10 min total)"
echo ""

# Stop collector
echo "7. Stopping collector..."
kill $COLLECTOR_PID 2>/dev/null
sleep 2

# Kill iperf3 servers
pkill -9 iperf3 2>/dev/null || true

echo ""
echo "8. Analyzing collected data..."
if [ -f ~/e6_sample_10min.csv ]; then
    ROWS=$(wc -l < ~/e6_sample_10min.csv)
    ROWS=$((ROWS - 1))  # Subtract header
    echo "   Rows collected: $ROWS"
    echo "   Expected: ~7200 (10 min × 60 sec × 4/sec × 3 UEs)"
    
    if [ $ROWS -gt 6000 ]; then
        echo "   ✓ Sample size looks good"
    else
        echo "   ⚠ Lower than expected, but may be acceptable"
    fi
    
    echo ""
    echo "   First 5 rows:"
    head -6 ~/e6_sample_10min.csv
    
    echo ""
    echo "   Last 5 rows:"
    tail -5 ~/e6_sample_10min.csv
    
    # Check for starvation
    STARVED_COUNT=$(awk -F, 'NR>1 {if ($11 > 0 && $10/$11 < 0.5) print}' ~/e6_sample_10min.csv | wc -l)
    echo ""
    echo "   Starvation analysis:"
    echo "     Intervals with starvation (delivered/offered < 0.5): $STARVED_COUNT"
    if [ $STARVED_COUNT -gt 0 ]; then
        echo "     ✓ Congestion detected in dataset"
    else
        echo "     ⚠ No starvation detected - heavy load may not have congested cell"
    fi
else
    echo "   ✗ Output file not found"
    exit 1
fi

echo ""
echo "========================================"
echo "Step 6 Complete!"
echo "========================================"
echo ""
echo "Deliverable: ~/e6_sample_10min.csv"
echo ""
echo "Next steps:"
echo "  1. Copy e6_sample_10min.csv to Windows"
echo "  2. Send to dataset team with message:"
echo ""
echo "     'Completed Steps 1-6. Attached 10-minute E6 sample with:"
echo "      - 3 UEs (ue_id: 0, 1, 2)"
echo "      - Light/medium/heavy load periods"
echo "      - ~$ROWS rows at 250ms intervals"
echo "      - Starvation events: $STARVED_COUNT"
echo ""
echo "      Please run tests.py validation before full collection.'"
echo ""
echo "  3. Wait for dataset team validation"
echo "  4. If validated, proceed with full E6 data collection"
echo ""
