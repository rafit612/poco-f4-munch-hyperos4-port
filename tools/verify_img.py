#!/usr/bin/env python3
"""verify_img.py ORIG_MNT NEW_MNT PAYLOAD_DIR REMOVE_LIST
Checks a rebuilt image against original + payload - removals:
payload files byte-identical, removals gone, kept entries keep mode/uid/gid/selinux/caps."""
import os, sys, hashlib, stat

orig, new, payload, rmlist = sys.argv[1:5]
removes = [l.strip().strip('/') for l in open(rmlist) if l.strip() and not l.startswith('#')] if os.path.exists(rmlist) else []


def removed(rel):
    return any(rel == r or rel.startswith(r + '/') for r in removes)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def meta(p):
    st = os.lstat(p)
    x = {}
    for k in ('security.selinux', 'security.capability'):
        try:
            x[k] = os.getxattr(p, k, follow_symlinks=False)
        except OSError:
            x[k] = None
    return (stat.S_IMODE(st.st_mode), stat.S_IFMT(st.st_mode), st.st_uid, st.st_gid, x['security.selinux'], x['security.capability'])


def walk(root):
    out = set()
    for d, dirs, files in os.walk(root):
        for n in dirs + files:
            out.add(os.path.relpath(os.path.join(d, n), root))
    return out


errs = []
o, n, p = walk(orig), walk(new), walk(payload)
for rel in sorted(p):
    pp, nn = os.path.join(payload, rel), os.path.join(new, rel)
    if rel.endswith('.meta'):
        continue
    if rel not in n:
        errs.append('MISSING payload ' + rel)
    elif os.path.isfile(pp) and not os.path.islink(pp) and sha(pp) != sha(nn):
        errs.append('DIFF payload ' + rel)
    elif os.path.islink(pp) and os.readlink(pp) != os.readlink(nn):
        errs.append('LINK payload ' + rel)
for rel in sorted(n):
    if removed(rel) and rel not in p:
        errs.append('NOT REMOVED ' + rel)
kept = 0
for rel in sorted(o):
    if rel in p or removed(rel):
        continue
    if rel not in n:
        errs.append('LOST ' + rel)
        continue
    mo, mn = meta(os.path.join(orig, rel)), meta(os.path.join(new, rel))
    if mo != mn:
        errs.append('META %s %s -> %s' % (rel, mo, mn))
    kept += 1
nolabel = [r for r in n if meta(os.path.join(new, r))[4] is None]
print('kept-checked', kept, 'payload', len(p), 'new-total', len(n), 'unlabeled', len(nolabel), 'errors', len(errs))
for e in (errs + ['UNLABELED ' + r for r in nolabel])[:40]:
    print(' ', e)
sys.exit(1 if errs or nolabel else 0)
