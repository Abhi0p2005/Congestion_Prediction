#!/bin/bash
# Usage: ./run_traffic.sh <run_name> <seconds> <rate_ue1> <rate_ue2> <rate_ue3>
#   rates like 10M; use 0 for no traffic on that UE. UDP downlink only.
set -e
RUN=~/oran-work/runs/$1; T=$2; mkdir -p "$RUN"
sudo -v
echo "run=$1 start_epoch=$(date +%s.%N) duration_s=$T rates=$3,$4,$5 proto=udp dir=dl" > "$RUN/meta.txt"
i=1
for R in "$3" "$4" "$5"; do
  if [ "$R" != "0" ]; then
    sudo ip netns exec ue$i iperf3 -c 10.53.1.1 -p 520$i -u -b "$R" -R -t "$T" -i 0.25 --forceflush \
      | ts '%.s' > "$RUN/iperf_ue$i.txt" &
  fi
  i=$((i+1))
done
wait
cp /tmp/gnb.log "$RUN/gnb.log"
echo "saved: $RUN"
