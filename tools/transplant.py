#!/usr/bin/env python3
"""transplant.py <src_mount> <payload_dir> <list_file>

Copy files (or whole directories) from a mounted source image into a payload tree for
erofs_tar_rebuild.py, writing '<file>.meta' (uid gid octal-mode selinux-label) from the source,
so files that do not exist in the target image keep their original metadata.
list_file: one partition-relative path per line ('#' comments allowed). Symlinks are copied as links.
"""
import os
import shutil
import sys

src_root, payload, list_file = sys.argv[1:4]
count = 0


def write_meta(src, dst):
    st = os.lstat(src)
    label = os.getxattr(src, 'security.selinux', follow_symlinks=False).decode().rstrip('\0')
    with open(dst + '.meta', 'w') as m:
        m.write(f"{st.st_uid} {st.st_gid} {st.st_mode & 0o7777:o} {label}\n")


def copy_one(rel):
    global count
    src, dst = os.path.join(src_root, rel), os.path.join(payload, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.islink(src):
        if os.path.lexists(dst):
            os.remove(dst)
        os.symlink(os.readlink(src), dst)
    else:
        shutil.copyfile(src, dst)
    write_meta(src, dst)
    count += 1


for line in open(list_file):
    rel = line.split('#', 1)[0].strip().strip('/')
    if not rel:
        continue
    path = os.path.join(src_root, rel)
    if not os.path.lexists(path):
        sys.exit(f"missing in source: {rel}")
    if os.path.isdir(path) and not os.path.islink(path):
        for root, dirs, files in os.walk(path):
            for name in sorted(files):
                copy_one(os.path.relpath(os.path.join(root, name), src_root))
    else:
        copy_one(rel)
print(f"transplanted {count} files into {payload}")
