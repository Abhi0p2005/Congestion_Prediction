#!/bin/bash
# O-RAN xApp Project - Ubuntu Quick Setup Script
# Run this INSIDE the Ubuntu VM after installation

set -e

echo "=========================================="
echo "O-RAN xApp - Ubuntu Setup"
echo "=========================================="
echo ""

# Part D: Install Dependencies and Docker
echo "[Part D] Installing dependencies..."
echo ""

echo "Step 1/5: Updating system..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "Step 2/5: Installing srsRAN Project dependencies..."
sudo apt install -y git curl cmake make gcc g++ pkg-config \
  libfftw3-dev libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev libzmq3-dev

echo ""
echo "Step 3/5: Installing srsRAN 4G dependencies..."
sudo apt install -y libboost-program-options-dev libconfig++-dev

echo ""
echo "Step 4/5: Installing tools..."
sudo apt install -y iperf3 net-tools htop vim

echo ""
echo "Step 5/5: Installing Docker..."
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

echo ""
echo "=========================================="
echo "Part D Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: Log out and log back in for Docker permissions to take effect"
echo ""
read -p "Press Enter to continue to Part E (clone software)..."

# Part E: Clone Software
echo ""
echo "[Part E] Cloning software repositories..."
echo ""

cd ~

if [ ! -d "srsRAN_Project" ]; then
    echo "Cloning srsRAN Project..."
    git clone https://github.com/srsran/srsRAN_Project.git
    cd srsRAN_Project && git checkout release_25_10 && cd ~
    echo "✓ srsRAN Project cloned"
else
    echo "✓ srsRAN Project already exists"
fi

if [ ! -d "srsRAN_4G" ]; then
    echo "Cloning srsRAN 4G..."
    git clone https://github.com/srsran/srsRAN_4G.git
    cd srsRAN_4G && git checkout release_23_11 && cd ~
    echo "✓ srsRAN 4G cloned"
else
    echo "✓ srsRAN 4G already exists"
fi

if [ ! -d "oran-sc-ric" ]; then
    echo "Cloning oran-sc-ric..."
    git clone https://github.com/srsran/oran-sc-ric.git
    cd oran-sc-ric && git checkout 621ade2 && cd ~
    echo "✓ oran-sc-ric cloned"
else
    echo "✓ oran-sc-ric already exists"
fi

echo ""
echo "Verifying versions..."
cd ~/srsRAN_Project && echo "srsRAN Project: $(git describe --tags)"
cd ~/srsRAN_4G && echo "srsRAN 4G: $(git describe --tags)"
cd ~/oran-sc-ric && echo "oran-sc-ric: $(git log -1 --oneline)"
cd ~

echo ""
echo "=========================================="
echo "Part E Complete!"
echo "=========================================="
echo ""
echo "Next: Part F - Build software (will take 1-1.5 hours)"
read -p "Press Enter to start building..."

# Part F: Build
echo ""
echo "[Part F] Building software..."
echo ""

# F1: srsRAN Project (gNB)
echo "Building srsRAN Project (gNB)..."
echo "This will take 30-45 minutes..."
cd ~/srsRAN_Project
mkdir -p build && cd build
cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON 2>&1 | tee cmake_out.txt

if grep -q "Found libZEROMQ" cmake_out.txt; then
    echo "✓ ZeroMQ found"
else
    echo "✗ ERROR: ZeroMQ not found!"
    exit 1
fi

echo "Compiling with $(nproc) cores..."
make -j$(nproc) || make -j2

if [ -f apps/gnb/gnb ]; then
    echo "✓ gNB binary created"
else
    echo "✗ ERROR: gNB binary not found!"
    exit 1
fi

# F2: srsRAN 4G (UE)
echo ""
echo "Building srsRAN 4G (UE)..."
echo "This will take 20-30 minutes..."
cd ~/srsRAN_4G
mkdir -p build && cd build
cmake ../ 2>&1 | tee cmake_out.txt

if grep -i -q "zeromq" cmake_out.txt; then
    echo "✓ ZeroMQ found"
else
    echo "✗ ERROR: ZeroMQ not found!"
    exit 1
fi

echo "Compiling with $(nproc) cores..."
make -j$(nproc) || make -j2

if [ -f srsue/src/srsue ]; then
    echo "✓ srsUE binary created"
else
    echo "✗ ERROR: srsUE binary not found!"
    exit 1
fi

# F3: Docker Images
echo ""
echo "Building Docker images..."
echo "This will take 15-20 minutes..."

echo "Building Open5GS core..."
cd ~/srsRAN_Project/docker
docker compose build 5gc

echo "Building RIC containers..."
cd ~/oran-sc-ric
docker compose build

echo ""
echo "=========================================="
echo "BUILD COMPLETE!"
echo "=========================================="
echo ""
echo "✓ gNB binary: ~/srsRAN_Project/build/apps/gnb/gnb"
echo "✓ UE binary: ~/srsRAN_4G/build/srsue/src/srsue"
echo "✓ Docker images: Open5GS core + RIC"
echo ""
echo "Time: $(date)"
echo ""
echo "Next: Part G - Test 5G Network"
echo "Open SETUP_GUIDE.md and follow Part G instructions"
echo ""
