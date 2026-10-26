#!/usr/bin/env python3
"""erofs_symlink_check.py <image.erofs>

Lists inline (FLAT_INLINE) symlinks whose target data crosses a 4 KB block boundary.
The 4.19 kernel EROFS driver cannot read those: symlinks fail with "erofs_fill_symlink: inline data
cross block boundary" (ls: Structure needs cleaning). Newer erofs-utils (1.9) can produce them.
Exit 1 if any are found.
"""
import struct, sys

img = open(sys.argv[1], 'rb')
img.seek(1024)
sb = img.read(128)
magic, _, _, blkszbits, _, root_nid, inos, _, _, blocks, meta_blkaddr, xattr_blkaddr = \
    struct.unpack_from('<IIIBBHQQIIII', sb, 0)
assert magic == 0xE0F5E1E2, 'not EROFS'
bs = 1 << blkszbits
META = meta_blkaddr * bs
data = img.seek(0, 2)

def inode(nid):
    img.seek(META + nid * 32)
    raw = img.read(64)
    fmt, xcnt, mode = struct.unpack_from('<HHH', raw, 0)
    compact = (fmt & 1) == 0
    layout = (fmt >> 1) & 7
    if compact:
        size, = struct.unpack_from('<I', raw, 8); u, = struct.unpack_from('<I', raw, 16); isize = 32
    else:
        size, = struct.unpack_from('<Q', raw, 8); u, = struct.unpack_from('<I', raw, 16); isize = 64
    xsize = 12 + (xcnt - 1) * 4 if xcnt else 0
    return mode, layout, size, u, isize, xsize

def read_inline(nid, isize, xsize, size):
    img.seek(META + nid * 32 + isize + xsize)
    return img.read(size)

def dir_entries(nid):
    mode, layout, size, u, isize, xsize = inode(nid)
    nblocks = (size + bs - 1) // bs
    for b in range(nblocks):
        last = b == nblocks - 1
        if layout == 2 and last:
            blk = read_inline(nid, isize, xsize, size - b * bs)
        else:
            img.seek((u + b) * bs); blk = img.read(min(bs, size - b * bs))
        first_off, = struct.unpack_from('<H', blk, 8)
        n = first_off // 12
        ents = [struct.unpack_from('<QHBB', blk, i * 12) for i in range(n)]
        for i, (cnid, noff, ftype, _) in enumerate(ents):
            end = ents[i + 1][1] if i + 1 < n else len(blk)
            name = blk[noff:end].split(b'\0')[0].decode('utf-8', 'replace')
            if name not in ('.', '..'):
                yield name, cnid

bad = 0; seen = 0
stack = [('', root_nid)]
while stack:
    path, nid = stack.pop()
    for name, cnid in dir_entries(nid):
        p = path + '/' + name
        mode, layout, size, u, isize, xsize = inode(cnid)
        typ = mode & 0o170000
        if layout == 2 and typ == 0o120000:  # only fast symlinks are refused; inline file/dir tails are read fine
            seen += 1
            # kernel 4.19: m_pofs = blkoff(inode) + inode size + xattr size, no wrap-around
            start = (META + cnid * 32) % bs + isize + xsize
            tail = size % bs if typ != 0o120000 else size
            if typ == 0o040000 or typ == 0o100000:
                tail = size % bs
            if start + tail > bs:
                bad += 1
                print('CROSS', 'symlink' if typ == 0o120000 else oct(typ), p)
        if typ == 0o040000:
            stack.append((p, cnid))
print(f'inline inodes {seen}, crossing block boundary {bad}')
sys.exit(1 if bad else 0)
