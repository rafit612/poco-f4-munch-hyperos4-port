#!/usr/bin/env python3
"""bench_compare.py BEFORE_LABEL AFTER_LABEL -> markdown table of the change in percent.
Reads audit/benchmarks/<label>/results.tsv written by tools/bench.sh."""
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audit', 'benchmarks')
# metric -> True if higher is better
BETTER_HIGH = {'mem_available_mb': True, 'cached_apps': True}


def load(label):
    d = {}
    for line in open(os.path.join(BASE, label, 'results.tsv')):
        k, _, v = line.rstrip('\n').partition('\t')
        d[k] = v
    return d


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


b, a = load(sys.argv[1]), load(sys.argv[2])
print(f'| Metric | Before ({sys.argv[1]}) | After ({sys.argv[2]}) | Change |')
print('|---|---|---|---|')
for k in b:
    x, y = num(b.get(k)), num(a.get(k))
    if x is None or y is None or k in ('uptime_s', 'charging'):
        continue
    if x == 0:
        ch = 'n/a'
    else:
        pct = (y - x) / abs(x) * 100
        good = pct > 0 if BETTER_HIGH.get(k, False) else pct < 0
        ch = f"{pct:+.1f}% {'better' if good and abs(pct) >= 1 else ('worse' if abs(pct) >= 1 else 'same')}"
    print(f'| {k} | {b[k]} | {a[k]} | {ch} |')
