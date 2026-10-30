#!/usr/bin/env python3
"""Read a Qualcomm CamX Chromatix parameter file (com.qti.tuned.*.bin): sections, symbols, top-level modules.

Format as documented by go-chromatix2libcamera (github.com/W-Floyd/go-chromatix2libcamera, chromatix/chromatix.go): header with a
section table at 0x98; section 0 = symbol table (0x48-byte records: id, name[32], version, group, data offset, data size), section 1 =
data, section 2 = index of top-level modules. Data is a run of 8-byte slots; a (count, symbol id) slot pair refers to another symbol.
usage: chromatix_read.py <file.bin> modules [name-regex]
       chromatix_read.py <file.bin> tree <symbol id> [depth]
"""
import re
import struct
import sys

SYM = 0x48


class Chromatix:
    def __init__(self, path):
        self.buf = open(path, "rb").read()
        b = self.buf
        assert b.startswith(b"QTI Chromatix Header"), "not a Chromatix file"
        toff, cnt = struct.unpack_from("<II", b, 0x98)
        self.sections = {}
        for i in range(cnt):
            t, o, s = struct.unpack_from("<QQQ", b, toff + i * 24)
            self.sections[t] = (o, s)
        so, ss = self.sections[0]
        self.data_off = self.sections[1][0]
        self.syms, self.by_id = [], {}
        for i in range(ss // SYM):
            r = so + i * SYM
            sid = struct.unpack_from("<Q", b, r)[0]
            name = b[r + 8:r + 40].split(b"\0")[0].decode("latin1")
            ver, grp, off, size = struct.unpack_from("<QQQQ", b, r + 40)
            s = dict(id=sid, name=name, ver=ver, group=grp, off=off, size=size, rec=r)
            self.by_id[sid] = s
            self.syms.append(s)

    def data(self, s):
        o = self.data_off + s["off"]
        return self.buf[o:o + s["size"]]

    def modules(self):
        return [s for s in self.syms if s["group"] != 0xffffffff]

    def refs(self, s):
        """(slot index, count, referenced symbol) for every (count, id) pair that fits the referenced symbol's size."""
        d = self.data(s)
        n = len(d) // 8
        out, i = [], 0
        while i + 1 < n:
            c, rid = struct.unpack_from("<QQ", d, i * 8)
            r = self.by_id.get(rid)
            if 0 < c < 1 << 20 and r and r["size"] and r["group"] == 0xffffffff and (r["size"] % c == 0 or c * 4 <= r["size"]):
                out.append((i, c, r))
                i += 2
                continue
            i += 1
        return out


def tree(cx, s, depth, ind=0):
    print(f"{'  ' * ind}{s['name']} id={s['id']:#x} size={s['size']}")
    if depth:
        for i, c, r in cx.refs(s):
            print(f"{'  ' * ind}  [slot {i}] x{c}")
            tree(cx, r, depth - 1, ind + 2)


def main():
    cx = Chromatix(sys.argv[1])
    if sys.argv[2] == "modules":
        pat = re.compile(sys.argv[3] if len(sys.argv) > 3 else ".")
        for s in cx.modules():
            if pat.search(s["name"]):
                v = s["ver"]
                print(f"{s['id']:#7x} group={s['group']:<4} v{v & 0xffff}.{(v >> 16) & 0xffff}.{v >> 32} size={s['size']:<8} {s['name']}")
    elif sys.argv[2] == "tree":
        tree(cx, cx.by_id[int(sys.argv[3], 0)], int(sys.argv[4]) if len(sys.argv) > 4 else 2)


if __name__ == "__main__":
    main()
