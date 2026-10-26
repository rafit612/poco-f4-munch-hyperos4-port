#!/usr/bin/env python3
"""rom_compare.py <global_root> <port_root> <out_dir>

Compare a mounted Global ROM (system/system_ext/product/mi_ext subdirs) with the mounted port.
Writes TSV/MD reports: every APK (package, version, signer, partition, priv/app), permission and
sysconfig XMLs (Google features, privapp, default permissions), props by topic, overlays.
Each <root> holds directories named system, system_ext, product, mi_ext (missing ones are skipped).
"""
import os
import re
import subprocess
import sys
import zipfile

g_root, p_root, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
TOOLS = os.path.dirname(os.path.abspath(__file__))
PARTS = ['system', 'system_ext', 'product', 'mi_ext']


def apks(root):
    res = {}
    for part in PARTS:
        base = os.path.join(root, part)
        if not os.path.isdir(base):
            continue
        for d, _, files in os.walk(base):
            for f in files:
                if f.endswith('.apk'):
                    p = os.path.join(d, f)
                    rel = os.path.relpath(p, base)
                    kind = 'priv-app' if '/priv-app/' in '/' + rel else ('overlay' if '/overlay/' in '/' + rel else 'app')
                    res[p] = (part, rel, kind)
    return res


def manifest(p):
    try:
        out_ = subprocess.run([sys.executable, '-I', os.path.join(TOOLS, 'apk_version.py'), p],
                              capture_output=True, text=True, timeout=60).stdout.strip().split('\t')
        subj = subprocess.run([sys.executable, '-I', os.path.join(TOOLS, 'apk_subject.py'), p],
                              capture_output=True, text=True, timeout=60).stdout.strip()
        org = re.search(r'O=([^,]+)', subj)
        return out_[0], out_[1], out_[2], (org.group(1) if org else subj[:30])
    except Exception as e:
        return ('?', '?', '?', str(e)[:30])


def table(root):
    t = {}
    for p, (part, rel, kind) in apks(root).items():
        pkg, vc, vn, signer = manifest(p)
        t[pkg] = (part, rel, kind, vn, signer)
    return t


G, P = table(g_root), table(p_root)
with open(os.path.join(out, 'apps.tsv'), 'w') as f:
    f.write('package\tstatus\tglobal_part\tglobal_path\tglobal_kind\tglobal_version\tglobal_signer\tport_part\tport_path\tport_version\tport_signer\n')
    for pkg in sorted(set(G) | set(P)):
        g, p = G.get(pkg), P.get(pkg)
        st = 'both' if g and p else ('GLOBAL_ONLY' if g else 'PORT_ONLY')
        f.write('\t'.join([pkg, st] + list(g or ('',) * 5) + ([p[0], p[1], p[3], p[4]] if p else [''] * 4)) + '\n')
print('apps: global %d, port %d, global-only %d, port-only %d' % (len(G), len(P), len(set(G) - set(P)), len(set(P) - set(G))))
