#!/usr/bin/env python3
"""Summarise srsRAN gNB log metrics, one row per report (= one 250 ms bin).
Usage: python3 metrics_summary.py /tmp/gnb.log [number_of_last_reports]"""
import re, sys
from datetime import datetime

KV = re.compile(r'(\w+)=(\S+)')
SI = {'': 1, 'k': 1e3, 'M': 1e6, 'G': 1e9}

def num(v):
    m = re.match(r'^(-?[\d.]+)([kMG]?)', v or '')
    return float(m.group(1)) * SI[m.group(2)] if m else None

def stamp(line):
    try:
        return datetime.fromisoformat(line.split()[0])
    except Exception:
        return None

reports, cur = [], None
for line in open(sys.argv[1], errors='ignore'):
    if 'Scheduler cell' in line:
        d = dict(KV.findall(line))
        cur = {'t': stamp(line), 'slots': int(d.get('nof_dl_slots', 0)),
               'prbs': int(d.get('nof_prbs', 0)), 'ues': []}
        reports.append(cur)
    elif 'Scheduler UE' in line and cur is not None:
        cur['ues'].append(dict(KV.findall(line)))

n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
print(f"{'wall_ms':>7} {'slots':>5} {'time_x':>6} {'cell_util':>9} | per UE: rnti cqi snr_db dl_Mbps ul_Mbps ul_err% dl_bs")
prev = None
for r in reports[-n:]:
    dt = (r['t'] - prev).total_seconds() * 1000 if (prev and r['t']) else float('nan')
    prev = r['t']
    time_x = r['slots'] / dt if dt == dt and dt > 0 else float('nan')   # ~1.00 = real time
    used = sum(num(u.get('dl_nof_prbs')) or 0 for u in r['ues'])
    util = used / (r['slots'] * r['prbs']) if r['slots'] and r['prbs'] else float('nan')
    cols = []
    for u in r['ues']:
        ok, nok = num(u.get('ul_nof_ok')) or 0, num(u.get('ul_nof_nok')) or 0
        err = 100 * nok / (ok + nok) if ok + nok else float('nan')
        cols.append(f"{u.get('rnti')} {u.get('cqi')} {u.get('pusch_snr_db')} "
                    f"{(num(u.get('dl_brate')) or 0)/1e6:.2f} {(num(u.get('ul_brate')) or 0)/1e6:.2f} "
                    f"{err:.1f} {u.get('dl_bs')}")
    print(f"{dt:7.0f} {r['slots']:5d} {time_x:6.2f} {util:9.3f} | " + " || ".join(cols))
