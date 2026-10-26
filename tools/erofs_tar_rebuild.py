#!/usr/bin/env python3
"""erofs_tar_rebuild.py <orig_mount> <payload_dir> <remove_list> <out.tar>

Rebuild a partition tree as a PAX tar for `mkfs.erofs --tar=f`, keeping the original
owner, mode, symlink target and every xattr (security.selinux, security.capability, ...)
read from an erofsfuse mount of the original image.

- payload_dir mirrors the partition layout; a file there replaces the original file's content
  (metadata stays the original's). A payload file with no original gets the metadata of the
  original file it is named after via '<name>.meta' (uid gid octal-mode selinux-label), or
  otherwise its parent directory's owner/label with mode 0644.
- remove_list: one partition-relative path per line; that path (and anything under it) is dropped.
"""
import os
import sys
import tarfile

orig, payload, remove_list, out = sys.argv[1:5]
removed = {l.strip().strip('/') for l in open(remove_list) if l.strip() and not l.startswith('#')}


def is_removed(rel):
    return any(rel == r or rel.startswith(r + '/') for r in removed)


def xattrs(path):
    return {k: os.getxattr(path, k, follow_symlinks=False) for k in os.listxattr(path, follow_symlinks=False)}


def pax(xa):
    return {'SCHILY.xattr.' + k: v.decode('utf-8', 'surrogateescape') for k, v in xa.items()}


def info(rel, st, xa, kind, size=0, link=''):
    ti = tarfile.TarInfo(rel if rel else '.')
    ti.uid, ti.gid, ti.mode, ti.mtime = st.st_uid, st.st_gid, st.st_mode & 0o7777, 0
    ti.uname = ti.gname = ''
    ti.type, ti.size, ti.linkname = kind, size, link
    ti.pax_headers = pax(xa)
    return ti


seen, stats = set(), {'kept': 0, 'replaced': 0, 'added': 0, 'removed': 0}
with tarfile.open(out, 'w', format=tarfile.PAX_FORMAT) as tar:
    for root, dirs, files in os.walk(orig):
        dirs.sort()
        rel_root = os.path.relpath(root, orig).replace('.', '', 1) if root == orig else os.path.relpath(root, orig)
        if rel_root and is_removed(rel_root):
            dirs[:] = []
            continue
        st = os.lstat(root)
        tar.addfile(info(rel_root, st, xattrs(root), tarfile.DIRTYPE))
        for name in sorted(files + [d for d in dirs if os.path.islink(os.path.join(root, d))]):
            p = os.path.join(root, name)
            rel = os.path.join(rel_root, name) if rel_root else name
            seen.add(rel)
            if is_removed(rel):
                stats['removed'] += 1
                continue
            st, xa = os.lstat(p), xattrs(p)
            if os.path.islink(p):
                tar.addfile(info(rel, st, xa, tarfile.SYMTYPE, link=os.readlink(p)))
                stats['kept'] += 1
                continue
            src = os.path.join(payload, rel)
            if os.path.isfile(src):
                stats['replaced'] += 1
            else:
                src = p
                stats['kept'] += 1
            with open(src, 'rb') as f:
                tar.addfile(info(rel, st, xa, tarfile.REGTYPE, size=os.path.getsize(src)), f)
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
    # payload files that do not exist in the original image
    def nearest_orig(rel_dir):
        while rel_dir and not os.path.isdir(os.path.join(orig, rel_dir)):
            rel_dir = os.path.dirname(rel_dir)
        return os.path.join(orig, rel_dir)

    for root, dirs, files in os.walk(payload):
        dirs.sort()
        rel_dir = os.path.relpath(root, payload)
        if rel_dir != '.' and not os.path.isdir(os.path.join(orig, rel_dir)):
            # new directory: owner and label of the nearest existing parent, mode 0755
            par = nearest_orig(rel_dir)
            pst = os.lstat(par)
            st = os.stat_result((0o40755, 0, 0, 1, pst.st_uid, pst.st_gid, 0, 0, 0, 0))
            tar.addfile(info(rel_dir, st, {'security.selinux': os.getxattr(par, 'security.selinux')}, tarfile.DIRTYPE))
            stats['added'] += 1
        for name in sorted(files):
            if name.endswith('.meta'):
                continue
            rel = os.path.relpath(os.path.join(root, name), payload)
            if rel in seen:
                continue
            src = os.path.join(root, name)
            meta = src + '.meta'
            parent = os.path.join(orig, os.path.dirname(rel))
            if os.path.isfile(meta):
                uid, gid, mode, label = open(meta).read().split()
                st = os.stat_result((0o100000 | int(mode, 8), 0, 0, 1, int(uid), int(gid), 0, 0, 0, 0))
                xa = {'security.selinux': label.encode()}
            else:
                pst = os.lstat(nearest_orig(os.path.dirname(rel)))
                parent = nearest_orig(os.path.dirname(rel))
                st = os.stat_result((0o100644, 0, 0, 1, pst.st_uid, pst.st_gid, 0, 0, 0, 0))
                xa = {'security.selinux': os.getxattr(parent, 'security.selinux')}
            if os.path.islink(src):
                # new symlink: target kept, label/owner from its .meta (or parent), mode 0644 like AOSP
                lst = os.stat_result((0o120644, 0, 0, 1, st.st_uid, st.st_gid, 0, 0, 0, 0))
                tar.addfile(info(rel, lst, xa, tarfile.SYMTYPE, link=os.readlink(src)))
            else:
                with open(src, 'rb') as f:
                    tar.addfile(info(rel, st, xa, tarfile.REGTYPE, size=os.path.getsize(src)), f)
            stats['added'] += 1
print(stats)
