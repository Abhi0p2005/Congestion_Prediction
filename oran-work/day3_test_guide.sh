#!/bin/bash
# Day 3 Test Guide - Interactive guide for running single-UE tests

echo "=========================================="
echo "Day 3: Single-UE Testing Guide"
echo "=========================================="
echo ""
echo "This script will guide you through Day 3 testing."
echo "You'll need 5 terminal windows open."
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "=========================================="
echo "TERMINAL 1: Start 5GC (Core Network)"
echo "=========================================="
echo ""
echo "In Terminal 1, run:"
echo ""
echo "  cd ~/srsRAN_Project/docker && docker compose up 5gc"
echo ""
echo "Wait until you see: 'Open5GS daemon started'"
echo ""
echo "Press Enter when Terminal 1 is ready..."
read

echo ""
echo "=========================================="
echo "TERMINAL 2: Start RIC"
echo "=========================================="
echo ""
echo "In Terminal 2, run:"
echo ""
echo "  cd ~/oran-sc-ric && docker compose up"
echo ""
echo "Wait until you see: 'RMR is ready now'"
echo ""
echo "Press Enter when Terminal 2 is ready..."
read

echo ""
echo "=========================================="
echo "TERMINAL 3: Start gNB with new config"
echo "=========================================="
echo ""
echo "In Terminal 3, run:"
echo ""
echo "  sudo rm -f /tmp/gnb.log"
echo "  cd ~/srsRAN_Project/build/apps/gnb"
echo "  sudo ./gnb -c ~/oran-work/gnb_single.yaml"
echo ""
echo "Wait until you see: 'Available radio types: zmq'"
echo ""
echo "Press Enter when Terminal 3 is ready..."
read

echo ""
echo "=========================================="
echo "TERMINAL 4: Start UE"
echo "=========================================="
echo ""
echo "In Terminal 4, run:"
echo ""
echo "  sudo ip netns add ue1"
echo "  cd ~/srsRAN_4G/build/srsue/src"
echo "  sudo ./srsue ~/oran-sc-ric/e2-agents/srsRAN/ue_zmq.conf"
echo ""
echo "Wait until you see: 'RRC Connected' and 'PDU Session Establishment successful'"
echo ""
echo "Press Enter when Terminal 4 is ready..."
read

echo ""
echo "=========================================="
echo "TERMINAL 5: Setup routes and traffic"
echo "=========================================="
echo ""
echo "In Terminal 5 (this terminal), we'll now:"
echo "1. Setup network routes"
echo "2. Test connectivity"
echo "3. Verify metrics"
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "Setting up routes..."
sudo ip ro add 10.45.0.0/16 via 10.53.1.2 2>/dev/null || echo "Route already exists"
sudo ip netns exec ue1 ip route add default dev tun_srsue 2>/dev/null || echo "UE route already exists"

echo ""
echo "Testing connectivity..."
sudo ip netns exec ue1 ping -c 3 10.45.1.1

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Connectivity test PASSED!"
else
    echo ""
    echo "✗ Connectivity test FAILED!"
    echo "Check that all terminals are running properly."
    exit 1
fi

echo ""
echo "=========================================="
echo "E1: Verify 250ms metrics"
echo "=========================================="
echo ""
echo "Checking if log file exists..."
sleep 2

if [ -f /tmp/gnb.log ]; then
    echo "✓ Log file found"
    echo ""
    echo "Running metrics_summary.py on last 12 reports..."
    echo ""
    python3 ~/oran-work/metrics_summary.py /tmp/gnb.log 12
    echo ""
    echo "CHECK THE OUTPUT ABOVE:"
    echo "  - wall_ms should be ~250 (reports every 250ms)"
    echo "  - slots should be 250"
    echo "  - time_x should be ~1.00 (real-time speed)"
    echo "  - You should see UE metrics: rnti, cqi, snr_db, dl_Mbps, ul_Mbps, ul_err%, dl_bs"
    echo ""
else
    echo "✗ Log file not found at /tmp/gnb.log"
    echo "Check that gNB is running with the correct config."
    exit 1
fi

echo "Press Enter to continue to E2 (JSON feed test)..."
read

echo ""
echo "=========================================="
echo "E2: Verify JSON websocket feed"
echo "=========================================="
echo ""
echo "Testing JSON feed on port 8001..."
echo ""

if [ -f ~/srsRAN_Project/docker/telegraf/ws_adapter.py ]; then
    timeout 5 python3 ~/srsRAN_Project/docker/telegraf/ws_adapter.py 2>/dev/null | head -c 2000
    echo ""
    echo ""
    echo "CHECK: Did you see JSON output with 'cells' and 'ue_list'?"
    echo ""
else
    echo "✗ ws_adapter.py not found"
fi

echo "Press Enter to continue to E3 (KPM test)..."
read

echo ""
echo "=========================================="
echo "E3: Verify KPM at 250ms"
echo "=========================================="
echo ""
echo "This will test E2SM-KPM subscription at 250ms intervals."
echo ""
echo "In a NEW terminal window, run:"
echo ""
echo "  cd ~/oran-sc-ric/xApps/python"
echo "  sed 's/report_period = 1000/report_period = 250/; s/granul_period = 1000/granul_period = 250/' kpm_mon_xapp.py > kpm_mon_250.py"
echo "  chmod +x kpm_mon_250.py"
echo "  cd ~/oran-sc-ric"
echo "  docker compose exec python_xapp_runner ./kpm_mon_250.py --kpm_report_style=1 --metrics=RRU.PrbUsedDl,DRB.UEThpDl"
echo ""
echo "Record: (a) subscription success, (b) 4 or 1 indication per second, (c) RRU.PrbUsedDl values"
echo ""
echo "Press Enter when done..."
read

echo ""
echo "=========================================="
echo "E4: Single-UE Capacity Test"
echo "=========================================="
echo ""
echo "Now we'll test single-UE capacity with increasing traffic."
echo "This will take about 3 minutes."
echo ""
echo "Press Enter to start capacity test..."
read

# Start iperf3 server
iperf3 -s -p 5201 -D

echo ""
echo "Running capacity test (5M -> 50M in steps)..."
echo ""

for R in 5M 10M 20M 30M 40M 50M; do
    echo ""
    echo "========== Testing $R =========="
    sudo ip netns exec ue1 iperf3 -c 10.53.1.1 -p 5201 -u -b $R -R -t 30 -i 5 2>&1 | tail -4 &
    IPERF_PID=$!
    
    # Let it run for 30 seconds
    sleep 32
    
    # Show metrics
    echo ""
    echo "Metrics for $R:"
    python3 ~/oran-work/metrics_summary.py /tmp/gnb.log 4
    echo ""
    
    # Wait for iperf to finish
    wait $IPERF_PID 2>/dev/null
    
    sleep 2
done

echo ""
echo "=========================================="
echo "Capacity Test Complete!"
echo "=========================================="
echo ""
echo "REVIEW THE RESULTS ABOVE:"
echo "  1. Find where delivered rate plateaus (= single-UE capacity)"
echo "  2. At plateau, cell_util should be ~0.9-1.0"
echo "  3. time_x should stay ~1.0 throughout"
echo "  4. No CPU core should be pinned at 100%"
echo ""
echo "If cell_util stays low (<0.8) when throughput plateaus,"
echo "then CPU is the bottleneck - REPORT THIS!"
echo ""
echo ""
echo "=========================================="
echo "Day 3 Testing Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review all outputs above"
echo "2. Document findings in ~/oran-work/day3_results.txt"
echo "3. Send results to your friend for verification"
echo ""
echo "To save full output, you can re-run this script with:"
echo "  ./day3_test_guide.sh 2>&1 | tee ~/oran-work/day3_output.txt"
echo ""
