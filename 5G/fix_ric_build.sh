#!/bin/bash
# Fix RIC Docker build timeout issues

echo "Fixing RIC Dockerfile for network timeouts..."

cd ~/oran-sc-ric

# Backup original
cp xApps/python/Dockerfile xApps/python/Dockerfile.backup

# Create fixed Dockerfile with retry logic and increased timeout
cat > xApps/python/Dockerfile << 'EOF'
FROM nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu20-c-go:1.0.0 as ubuntu

FROM python:3.8-slim-bookworm

# Install system dependencies
RUN apt-get clean -y && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    git \
    build-essential \
    libsctp-dev \
    lksctp-tools \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip with retry
RUN pip install --default-timeout=100 --retries 5 --upgrade pip

# Install Python packages one at a time with increased timeout
RUN pip install --default-timeout=100 --retries 5 certifi
RUN pip install --default-timeout=100 --retries 5 six
RUN pip install --default-timeout=100 --retries 5 python-dateutil
RUN pip install --default-timeout=100 --retries 5 setuptools
RUN pip install --default-timeout=100 --retries 5 urllib3
RUN pip install --default-timeout=100 --retries 5 logger
RUN pip install --default-timeout=100 --retries 5 requests
RUN pip install --default-timeout=100 --retries 5 inotify-simple
RUN pip install --default-timeout=100 --retries 5 mdclogpy
RUN pip install --default-timeout=100 --retries 5 google-api-python-client
RUN pip install --default-timeout=100 --retries 5 msgpack
RUN pip install --default-timeout=100 --retries 5 ricsdl
RUN pip install --default-timeout=100 --retries 5 asn1tools

RUN mkdir -p /opt/xApps && chmod -R 755 /opt/xApps

WORKDIR /opt/xApps
COPY lib /opt/xApps/lib/
COPY *.py /opt/xApps/

ENV PYTHONPATH=/opt/xApps/lib

CMD ["/bin/bash"]
EOF

echo "✓ Dockerfile fixed"
echo ""
echo "Now rebuilding RIC containers with fixed Dockerfile..."
echo "This will take 15-20 minutes..."
echo ""

docker compose build

echo ""
echo "Build complete!"
