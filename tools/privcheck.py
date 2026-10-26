#!/usr/bin/env python3
"""privcheck.py PRIV_PERMS_FILE label=root1[,root2]=removelist|- ...
For every priv-app APK in the merged roots, list platform privileged permissions it requests
that no privapp-permissions allowlist (etc/permissions/*.xml in the same roots) grants.
With ro.control_privapp_permissions=enforce a missing entry stops the phone from booting."""
import sys, os, subprocess, xml.etree.ElementTree as ET

AAPT = os.environ.get('AAPT2', os.path.expanduser('~/Android/Sdk/build-tools/37.0.0/aapt2'))
priv = set(l.strip() for l in open(sys.argv[1]) if l.strip())
cfg = [a.split('=', 2) for a in sys.argv[2:]]


def removed(rel, rm):
    return any(rel == r or rel.startswith(r + '/') for r in rm)


apks, xmls = {}, {}
for label, base, rmf in cfg:
    rm = [l.strip().strip('/') for l in open(rmf) if l.strip() and not l.startswith('#')] if rmf != '-' else []
    for b in base.split(','):
        if not os.path.isdir(b):
            continue
        for d, _, fs in os.walk(b):
            for f in fs:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, b)
                if removed(rel, rm):
                    continue
                key = label + '/' + rel
                if '/priv-app/' in '/' + rel and f.endswith('.apk') and '/oat/' not in rel:
                    apks[key] = p
                if rel.startswith('etc/permissions/') and f.endswith('.xml'):
                    xmls[key] = p

allow = {}
for p in xmls.values():
    try:
        r = ET.parse(p).getroot()
    except Exception:
        continue
    for e in r.iter('privapp-permissions'):
        s = allow.setdefault(e.get('package'), set())
        s |= {x.get('name') for x in e if x.tag in ('permission', 'deny-permission')}

bad = 0
for k, p in sorted(apks.items()):
    out = subprocess.run([AAPT, 'dump', 'badging', p], capture_output=True, text=True).stdout
    pk, req = None, []
    for l in out.splitlines():
        if l.startswith('package: name='):
            pk = l.split("'")[1]
        if l.startswith('uses-permission: name='):
            req.append(l.split("'")[1])
    miss = [r for r in req if r in priv and r not in allow.get(pk, set())]
    if miss:
        bad += 1
        print('MISSING', k, pk, miss)
print('priv-apps checked', len(apks), 'with missing', bad)
