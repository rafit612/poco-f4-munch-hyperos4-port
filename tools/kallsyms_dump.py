#!/usr/bin/env python3
"""Dump symbol names from an arm64 kernel Image's compressed kallsyms tables.

  kallsyms_dump.py <Image> > names.txt

Finds kallsyms_token_table by its run of single-digit tokens, kallsyms_markers
just before it, and kallsyms_names just before that (located by checking that
parsing from a candidate start lands exactly on markers[1] and markers[2]).
Prints one "<type> <name>" per symbol.
"""
import struct
import sys

d = open(sys.argv[1], "rb").read()

# token table: 256 NUL-terminated tokens; digits 0-9 usually appear as a run
run = b"".join(bytes([c]) + b"\0" for c in b"0123456789")
pos = d.find(run)
while pos >= 0:
    # walk back to the start of the token table: 256 tokens must end at token_index
    start = pos
    # tokens before the digits: step back over NUL-terminated strings
    cand = None
    for back in range(0, 4096):
        s = pos - back
        if s <= 0:
            break
        if d[s - 1] != 0:
            continue
        # try parsing 256 tokens from s
        p = s; ok = True; toks = []
        for _ in range(256):
            e = d.find(b"\0", p, p + 64)
            if e < 0 or e == p:
                ok = False; break
            toks.append(d[p:e]); p = e + 1
        if not ok:
            continue
        idx_off = (p + 7) & ~7
        for align in (idx_off, (p + 3) & ~3, p + (p & 1)):
            idx = struct.unpack_from("<256H", d, align)
            if idx[0] == 0 and all(idx[i] < idx[i + 1] for i in range(255)) and idx[255] == sum(len(t) + 1 for t in toks[:255]):
                cand = (s, toks)
                break
        if cand:
            break
    if cand:
        break
    pos = d.find(run, pos + 1)
if not cand:
    sys.exit("token table not found")
tt_start, toks = cand

# markers: u32 (or u64) array right before the token table, starting at 0, ascending
def find_markers(width):
    fmt = "<I" if width == 4 else "<Q"
    p = (tt_start & ~(width - 1)) - width
    vals = []
    while p > 0:
        v = struct.unpack_from(fmt, d, p)[0]
        if vals and v >= vals[-1]:
            break
        vals.append(v)
        if v == 0:
            return p, list(reversed(vals))
        p -= width
    return None

for width in (8, 4):
    # skip padding zeros between markers and token table
    r = None
    for pad in range(0, 64, width):
        save = tt_start
        tt_start -= pad
        r = find_markers(width)
        tt_start = save
        if r and len(r[1]) > 10:
            break
        r = None
    if r:
        break
if not r:
    sys.exit("markers not found")
mk_start, markers = r

def parse(start, count):
    p = start; offs = []
    for _ in range(count):
        offs.append(p - start)
        n = d[p]; p += 1 + n
    return offs, p

names_start = None
for s in range(mk_start - markers[-1] - 1, max(0, mk_start - markers[-1] - 400000), -1):
    if s + markers[2] >= mk_start:
        continue
    offs, _ = parse(s, 513)
    if offs[256] == markers[1] and offs[512] == markers[2]:
        names_start = s
        break
if names_start is None:
    sys.exit("names not found")

p = names_start
out = sys.stdout
count = 0
while p < mk_start:
    n = d[p]
    if n == 0:
        break
    sym = b"".join(toks[b] for b in d[p + 1:p + 1 + n])
    p += 1 + n
    out.write(chr(sym[0]) + " " + sym[1:].decode("latin-1") + "\n")
    count += 1
print(f"# {count} symbols", file=sys.stderr)
