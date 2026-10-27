#!/bin/bash
# Day 4 Multi-UE Startup Script
# This script starts all components in the correct order with proper delays

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Day 4: Multi-UE Network Startup (Automated)              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a process is running
check_process() {
    pgrep -f "$1" > /dev/null
}

# Step 1: Check if Core and RIC are already running
echo -e "${YELLOW}[1/7] Checking 5GC and RIC status...${NC}"
if docker ps | grep -q "5gc"; then
    echo -e "${GREEN}✓ 5GC is running${NC}"
else
    echo -e "${RED}✗ 5GC is NOT running!${NC}"
    echo "Please start in Terminal 1: cd ~/srsRAN_Project/docker && docker compose up 5gc"
    exit 1
fi

if docker ps | grep -q "ric"; then
    echo -e "${GREEN}✓ RIC is running${NC}"
else
    echo -e "${RED}✗ RIC is NOT running!${NC}"
    echo "Please start in Terminal 2: cd ~/oran-sc-ric && docker compose up"
    exit 1
fi

# Step 2: Create network namespaces
echo -e "\n${YELLOW}[2/7] Creating network namespaces...${NC}"
sudo ip netns add ue1 2>/dev/null || echo "ue1 namespace already exists"
sudo ip netns add ue2 2>/dev/null || echo "ue2 namespace already exists"
sudo ip netns add ue3 2>/dev/null || echo "ue3 namespace already exists"
echo -e "${GREEN}✓ Namespaces ready${NC}"

# Step 3: Start gNB in background
echo -e "\n${YELLOW}[3/7] Starting gNB...${NC}"
if check_process "gnb.*gnb_multi.yaml"; then
    echo "gNB already running, killing..."
    sudo pkill -9 -f "gnb.*gnb_multi.yaml" 2>/dev/null || true
    sleep 2
fi

sudo rm -f /tmp/gnb.log
cd ~/srsRAN_Project/build/apps/gnb
sudo ./gnb -c ~/Desktop/oran-work/gnb_multi.yaml > /tmp/gnb_startup.log 2>&1 &
GNB_PID=$!

# Wait for gNB to connect to AMF
sleep 3
if check_process "gnb.*gnb_multi.yaml"; then
    echo -e "${GREEN}✓ gNB started (PID: $GNB_PID)${NC}"
else
    echo -e "${RED}✗ gNB failed to start! Check /tmp/gnb_startup.log${NC}"
    exit 1
fi

# Step 4: Start GNU Radio Companion (must be done manually for now)
echo -e "\n${YELLOW}[4/7] GNU Radio Broker${NC}"
if pgrep -f "multi_ue_scenario" > /dev/null; then
    echo -e "${GREEN}✓ GNU Radio broker is running${NC}"
else
    echo -e "${YELLOW}⚠ GNU Radio broker NOT running yet${NC}"
    echo "Starting GNU Radio Companion..."
    gnuradio-companion ~/Desktop/oran-work/multi_ue_scenario.grc > /dev/null 2>&1 &
    sleep 3
    echo -e "${YELLOW}→ When GNU Radio opens, click the PLAY button (▶)${NC}"
    echo -e "${YELLOW}→ Press Enter after clicking PLAY to continue...${NC}"
    read -p ""
fi

# Step 5: Start UE1
echo -e "\n${YELLOW}[5/7] Starting UE1...${NC}"
cd ~/srsRAN_4G/build/srsue/src
sudo ./srsue ~/Desktop/oran-work/ue1_zmq.conf > /tmp/ue1_startup.log 2>&1 &
UE1_PID=$!
sleep 8
if grep -q "PDU Session Establishment successful" /tmp/ue1_startup.log; then
    UE1_IP=$(grep "PDU Session Establishment successful" /tmp/ue1_startup.log | grep -oP 'IP: \K[0-9.]+')
    echo -e "${GREEN}✓ UE1 connected: $UE1_IP${NC}"
else
    echo -e "${RED}✗ UE1 failed to connect! Check /tmp/ue1_startup.log${NC}"
fi

# Step 6: Start UE2
echo -e "\n${YELLOW}[6/7] Starting UE2 (waiting 10 seconds)...${NC}"
sleep 10
sudo ./srsue ~/Desktop/oran-work/ue2_zmq.conf > /tmp/ue2_startup.log 2>&1 &
UE2_PID=$!
sleep 8
if grep -q "PDU Session Establishment successful" /tmp/ue2_startup.log; then
    UE2_IP=$(grep "PDU Session Establishment successful" /tmp/ue2_startup.log | grep -oP 'IP: \K[0-9.]+')
    echo -e "${GREEN}✓ UE2 connected: $UE2_IP${NC}"
else
    echo -e "${YELLOW}⚠ UE2 connection in progress... check /tmp/ue2_startup.log${NC}"
fi

# Step 7: Start UE3
echo -e "\n${YELLOW}[7/7] Starting UE3 (waiting 10 seconds)...${NC}"
sleep 10
sudo ./srsue ~/Desktop/oran-work/ue3_zmq.conf > /tmp/ue3_startup.log 2>&1 &
UE3_PID=$!
sleep 8
if grep -q "PDU Session Establishment successful" /tmp/ue3_startup.log; then
    UE3_IP=$(grep "PDU Session Establishment successful" /tmp/ue3_startup.log | grep -oP 'IP: \K[0-9.]+')
    echo -e "${GREEN}✓ UE3 connected: $UE3_IP${NC}"
else
    echo -e "${YELLOW}⚠ UE3 connection in progress... check /tmp/ue3_startup.log${NC}"
fi

# Step 8: Configure routes
echo -e "\n${YELLOW}[8/8] Configuring routes...${NC}"
sudo ip ro add 10.45.0.0/16 via 10.53.1.2 2>/dev/null || true
for i in 1 2 3; do 
    sudo ip netns exec ue$i ip route add default dev tun_srsue 2>/dev/null || true
done
echo -e "${GREEN}✓ Routes configured${NC}"

# Summary
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    STARTUP COMPLETE                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Process IDs:"
echo "  gNB:  $GNB_PID"
echo "  UE1:  $UE1_PID"
echo "  UE2:  $UE2_PID"
echo "  UE3:  $UE3_PID"
echo ""
echo "Logs available at:"
echo "  /tmp/gnb.log"
echo "  /tmp/ue1_startup.log"
echo "  /tmp/ue2_startup.log"
echo "  /tmp/ue3_startup.log"
echo ""
echo "Next steps:"
echo "  1. Verify metrics: python3 ~/Desktop/oran-work/metrics_summary.py /tmp/gnb.log 12"
echo "  2. Test connectivity: for i in 1 2 3; do sudo ip netns exec ue\$i ping -c 2 10.53.1.1; done"
echo ""
echo "To stop everything: sudo pkill -9 -f 'gnb|srsue'"
echo ""
