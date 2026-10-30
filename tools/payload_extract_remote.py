#!/usr/bin/env python3
"""Extract single partitions from an OTA payload.bin inside a ROM zip on a web server, WITHOUT downloading the whole zip.

Reads only the zip directory, the payload manifest and the byte ranges of the requested partition (HTTP Range requests).
Reuses the parsing helpers of payload_extract.py. Read-only, writes <partition>.img.

Usage: payload_extract_remote.py <zip-url> --list
       payload_extract_remote.py <zip-url> <out_dir> <partition> [<partition> ...]
"""
import bz2
import lzma
import os
import struct
import subprocess
import sys
import time
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from payload_extract import fields  # noqa: E402


class HttpFile:
    """Minimal read-only seekable file over HTTP Range requests."""

    def __init__(self, url):
        self.url, self.pos = url, 0
        req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            self.size = int(r.headers["Content-Range"].split("/")[1])

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def read(self, n=-1):
        if n < 0 or self.pos + n > self.size:
            n = self.size - self.pos
        if n == 0:
            return b""
        for attempt in range(6):
            try:
                req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + n - 1}"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                if len(data) == n:
                    self.pos += n
                    return data
            except OSError:
                pass
            time.sleep(2 * (attempt + 1))
        raise SystemExit(f"download failed at offset {self.pos}")


def load(url):
    f = HttpFile(url)
    with zipfile.ZipFile(f) as z:
        info = z.getinfo("payload.bin")
        if info.compress_type != zipfile.ZIP_STORED:
            raise SystemExit("payload.bin is compressed inside the zip; unsupported")
    f.seek(info.header_offset)
    name_len, extra_len = struct.unpack("<HH", f.read(30)[26:30])
    base = info.header_offset + 30 + name_len + extra_len
    f.seek(base)
    hdr = f.read(24)
    if hdr[:4] != b"CrAU":
        raise SystemExit("not an OTA payload")
    version, manifest_size = struct.unpack(">QQ", hdr[4:20])
    sig_size = struct.unpack(">I", hdr[20:24])[0] if version >= 2 else 0
    manifest = f.read(manifest_size)
    data_start = base + (24 if version >= 2 else 20) + manifest_size + sig_size
    block_size, parts = 4096, {}
    for fn, wt, v in fields(manifest):
        if fn == 3 and wt == 0:
            block_size = v
        elif fn == 13:
            name, ops, size = None, [], 0
            for pf, pw, pv in fields(v):
                if pf == 1:
                    name = pv.decode()
                elif pf == 7:
                    for nf, nw, nv in fields(pv):
                        if nf == 1:
                            size = nv
                elif pf == 8:
                    op = {"type": 0, "off": 0, "len": 0, "dst": []}
                    for of, ow, ov in fields(pv):
                        if of == 1: op["type"] = ov
                        elif of == 2: op["off"] = ov
                        elif of == 3: op["len"] = ov
                        elif of == 6:
                            e = dict((xf, xv) for xf, xw, xv in fields(ov))
                            op["dst"].append((e.get(1, 0), e.get(2, 0)))
                    ops.append(op)
            parts[name] = (size, ops)
    return f, data_start, block_size, parts


def main():
    url = sys.argv[1]
    f, data_start, bs, parts = load(url)
    if sys.argv[2] == "--list":
        for n, (size, ops) in parts.items():
            print(f"{n:24} {size / 1e6:10.1f} MB  ops={len(ops):6}  fetch={sum(o['len'] for o in ops) / 1e6:8.1f} MB")
        return
    out_dir, names = sys.argv[2], sys.argv[3:]
    os.makedirs(out_dir, exist_ok=True)
    for name in names:
        size, ops = parts[name]
        out = os.path.join(out_dir, name + ".img")
        with open(out, "wb") as o:
            o.truncate(size)
            for n, op in enumerate(ops):
                f.seek(data_start + op["off"])
                data = f.read(op["len"])
                t = op["type"]
                if t == 1:
                    data = bz2.decompress(data)
                elif t == 8:
                    data = lzma.decompress(data)
                elif t == 14:
                    data = subprocess.run(["zstd", "-d", "-c"], input=data, capture_output=True, check=True).stdout
                elif t in (6, 7):
                    continue
                elif t != 0:
                    raise SystemExit(f"unsupported operation type {t}")
                pos = 0
                for start, num in op["dst"]:
                    o.seek(start * bs)
                    o.write(data[pos:pos + num * bs])
                    pos += num * bs
                if n % 16 == 0:
                    print(f"  {name}: {n}/{len(ops)}", flush=True)
        print(f"wrote {out} ({size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
