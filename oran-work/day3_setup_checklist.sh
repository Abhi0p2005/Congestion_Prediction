#!/bin/bash
# Day 3 Setup Checklist - Run this to verify all prerequisites

echo "=========================================="
echo "Day 3 Setup Verification Checklist"
echo "=========================================="
echo ""

# Check work directory
echo "✓ Checking work directory..."
if [ -d ~/oran-work/runs ]; then
    echo "  ✓ ~/oran-work/runs exists"
else
    echo "  ✗ ~/oran-work/runs missing"
    exit 1
fi

# Check scripts
echo ""
echo "✓ Checking scripts..."
if [ -f ~/oran-work/metrics_summary.py ]; then
    echo "  ✓ metrics_summary.py exists"
else
    echo "  ✗ metrics_summary.py missing"
    exit 1
fi

if [ -x ~/oran-work/metrics_summary.py ]; then
    echo "  ✓ metrics_summary.py is executable"
else
    echo "  ✗ metrics_summary.py not executable"
    exit 1
fi

# Check config
echo ""
echo "✓ Checking configuration files..."
if [ -f ~/oran-work/gnb_single.yaml ]; then
    echo "  ✓ gnb_single.yaml exists"
    
    # Verify key settings
    if grep -q "du_report_period: 250" ~/oran-work/gnb_single.yaml; then
        echo "  ✓ 250ms reporting enabled"
    else
        echo "  ✗ 250ms reporting NOT configured"
        exit 1
    fi
    
    if grep -q "enable_log: true" ~/oran-work/gnb_single.yaml; then
        echo "  ✓ Log metrics enabled"
    else
        echo "  ✗ Log metrics NOT enabled"
        exit 1
    fi
    
    if grep -q "mcs_table: qam64" ~/oran-work/gnb_single.yaml; then
        echo "  ✓ 64-QAM table configured"
    else
        echo "  ✗ 64-QAM NOT configured"
        exit 1
    fi
    
    if grep -q "remote_control:" ~/oran-work/gnb_single.yaml; then
        echo "  ✓ Remote control (websocket) enabled"
    else
        echo "  ✗ Remote control NOT configured"
        exit 1
    fi
else
    echo "  ✗ gnb_single.yaml missing"
    exit 1
fi

# Check dependencies
echo ""
echo "✓ Checking dependencies..."

if command -v ts &> /dev/null; then
    echo "  ✓ moreutils (ts) installed"
else
    echo "  ✗ moreutils NOT installed - run: sudo apt install -y moreutils"
    exit 1
fi

if command -v python3 &> /dev/null; then
    echo "  ✓ python3 installed"
else
    echo "  ✗ python3 NOT installed"
    exit 1
fi

if python3 -c "import websocket" 2>/dev/null; then
    echo "  ✓ websocket-client installed"
else
    echo "  ✗ websocket-client NOT installed - run: pip3 install websocket-client"
    exit 1
fi

# Check srsRAN installation
echo ""
echo "✓ Checking srsRAN installation..."
if [ -d ~/srsRAN_Project/build/apps/gnb ]; then
    echo "  ✓ srsRAN Project (gNB) found"
else
    echo "  ✗ srsRAN Project (gNB) NOT found"
    exit 1
fi

if [ -d ~/srsRAN_4G/build/srsue/src ]; then
    echo "  ✓ srsRAN 4G (UE) found"
else
    echo "  ✗ srsRAN 4G (UE) NOT found"
    exit 1
fi

if [ -d ~/oran-sc-ric ]; then
    echo "  ✓ oran-sc-ric found"
else
    echo "  ✗ oran-sc-ric NOT found"
    exit 1
fi

if [ -d ~/srsRAN_Project/docker ]; then
    echo "  ✓ 5GC docker configs found"
else
    echo "  ✗ 5GC docker configs NOT found"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ ALL CHECKS PASSED!"
echo "=========================================="
echo ""
echo "You are ready to start Day 3 testing."
echo ""
echo "Next steps:"
echo "1. Run: ./day3_test_guide.sh"
echo "   (This will guide you through starting the stack)"
echo ""
