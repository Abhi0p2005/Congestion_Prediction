#!/bin/bash
# Quick Fix: Enable stdout metrics for Step 1
# The JSON server approach requires additional setup, so we'll use stdout instead

echo "==========================================="
echo "Quick Fix: Enabling stdout metrics"
echo "==========================================="
echo ""

CONFIG_FILE=~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml

echo "Creating backup..."
cp $CONFIG_FILE ${CONFIG_FILE}.backup_$(date +%s)

echo "Updating metrics section to enable stdout..."

# Use sed to change autostart_stdout_metrics to true
sed -i 's/autostart_stdout_metrics: false/autostart_stdout_metrics: true/g' $CONFIG_FILE

echo ""
echo "✓ Config updated!"
echo ""
echo "Verification:"
grep -A10 "^metrics:" $CONFIG_FILE

echo ""
echo "==========================================="
echo "Now restart the gNB:"
echo "==========================================="
echo ""
echo "1. In Terminal 3, press Ctrl+C to stop gNB"
echo "2. Wait 60 seconds"
echo "3. Start gNB again:"
echo "   sudo ./gnb -c ~/oran-sc-ric/e2-agents/srsRAN/gnb_zmq.yaml 2>&1 | tee /tmp/gnb_metrics.json"
echo ""
echo "You should now see metrics output every 250ms in Terminal 3"
echo "The metrics will also be saved to /tmp/gnb_metrics.json"
echo ""
