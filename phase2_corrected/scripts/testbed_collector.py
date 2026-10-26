#!/usr/bin/env python3
"""
E6 Testbed Data Collector
Matches dataset team schema exactly - 250ms intervals

Usage:
    tail -f /tmp/gnb_metrics.json | python3 testbed_collector.py e6_data.csv --rates ue1=5M,ue2=5M,ue3=5M

Author: Testbed Team
Date: October 24, 2026
"""

import json
import csv
import time
import sys
import argparse
from datetime import datetime


FIELDNAMES = [
    'timestamp',
    'ue_id',
    'cell_util',
    'dl_cqi',
    'ul_sinr_db',
    'dl_mbps',
    'ul_mbps',
    'ul_error_pct',
    'dl_buffer_bytes',
    'offered_bytes',
    'delivered_bytes'
]


class TrafficRateTracker:
    def __init__(self, rate_config):
        self.rates = {}
        if rate_config:
            for pair in rate_config.split(','):
                ue, rate = pair.split('=')
                self.rates[int(ue.replace('ue', ''))] = self._parse_rate(rate)
    
    def _parse_rate(self, rate_str):
        rate_str = rate_str.upper()
        if 'M' in rate_str:
            return float(rate_str.replace('M', '')) * 1e6
        elif 'K' in rate_str:
            return float(rate_str.replace('K', '')) * 1e3
        else:
            return float(rate_str)
    
    def get_offered_bytes(self, ue_id, interval_sec=0.25):
        rate_bps = self.rates.get(ue_id, 0)
        return int((rate_bps / 8) * interval_sec)


class GnbMetricsParser:
    def __init__(self, rate_tracker):
        self.rate_tracker = rate_tracker
        self.max_prbs = 52
        self.last_timestamp = None
    
    def parse_json_line(self, line):
        try:
            data = json.loads(line)
            
            timestamp = time.time()
            rows = []
            
            cell_util = self._extract_cell_util(data)
            
            if 'ue_container' in data:
                for ue_data in data['ue_container']:
                    row = self._parse_ue_metrics(ue_data, timestamp, cell_util)
                    if row:
                        rows.append(row)
            
            return rows
        
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Parse error: {e}", file=sys.stderr)
            return []
    
    def _extract_cell_util(self, data):
        used_prbs = data.get('prb_usage', 0)
        return used_prbs / self.max_prbs if self.max_prbs > 0 else 0.0
    
    def _parse_ue_metrics(self, ue_data, timestamp, cell_util):
        ue_id = ue_data.get('ue_id', 0)
        
        dl_brate = ue_data.get('dl_brate', 0)
        ul_brate = ue_data.get('ul_brate', 0)
        
        ul_nof_ok = ue_data.get('ul_nof_ok', 0)
        ul_nof_nok = ue_data.get('ul_nof_nok', 0)
        ul_error_pct = 0.0
        if (ul_nof_ok + ul_nof_nok) > 0:
            ul_error_pct = (ul_nof_nok / (ul_nof_ok + ul_nof_nok)) * 100
        
        offered_bytes = self.rate_tracker.get_offered_bytes(ue_id)
        delivered_bytes = int((dl_brate / 8) * 0.25)
        
        row = {
            'timestamp': timestamp,
            'ue_id': ue_id,
            'cell_util': round(cell_util, 4),
            'dl_cqi': ue_data.get('cqi', 0),
            'ul_sinr_db': round(ue_data.get('pusch_snr_db', 0.0), 2),
            'dl_mbps': round(dl_brate / 1e6, 3),
            'ul_mbps': round(ul_brate / 1e6, 3),
            'ul_error_pct': round(ul_error_pct, 2),
            'dl_buffer_bytes': ue_data.get('dl_bs', 0),
            'offered_bytes': offered_bytes,
            'delivered_bytes': delivered_bytes
        }
        
        return row


def main():
    parser = argparse.ArgumentParser(
        description='E6 Testbed Data Collector - 250ms intervals',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tail -f /tmp/gnb_metrics.json | python3 testbed_collector.py e6_data.csv --rates ue1=5M,ue2=5M,ue3=5M
  tail -f /tmp/gnb_metrics.json | python3 testbed_collector.py sample.csv --rates ue1=2M,ue2=10M,ue3=30M
        """
    )
    parser.add_argument('output', help='Output CSV file path')
    parser.add_argument('--rates', help='Traffic rates per UE (e.g., ue1=5M,ue2=10M,ue3=30M)')
    
    args = parser.parse_args()
    
    rate_tracker = TrafficRateTracker(args.rates)
    parser_obj = GnbMetricsParser(rate_tracker)
    
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Collecting to {args.output}")
        print(f"[INFO] Reading gNB JSON metrics from stdin (250ms intervals)")
        print(f"[INFO] Traffic rates: {args.rates if args.rates else 'Not specified'}")
        print(f"[INFO] Schema: {', '.join(FIELDNAMES)}")
        print("-" * 70)
        
        row_count = 0
        for line in sys.stdin:
            rows = parser_obj.parse_json_line(line.strip())
            
            for row in rows:
                writer.writerow(row)
                f.flush()
                
                row_count += 1
                if row_count % 100 == 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Collected {row_count} rows", 
                          file=sys.stderr)
                
                starved = "STARVED" if (row['delivered_bytes'] / max(row['offered_bytes'], 1)) < 0.5 else ""
                print(f"UE{row['ue_id']}: CQI={row['dl_cqi']:2d} DL={row['dl_mbps']:6.2f}Mbps "
                      f"Cell={row['cell_util']:.2f} {starved}", file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Collection stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
