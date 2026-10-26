#!/usr/bin/env python3
"""Extract one partition image from an Android OTA payload.bin inside a ROM zip.

Read-only: parses the zip and payload, decompresses full-image operations
(REPLACE / REPLACE_BZ / REPLACE_XZ / REPLACE_ZSTD / ZERO / DISCARD) and writes
<partition>.img. Delta operations are not supported (full ROMs don't use them).

Usage: payload_extract.py <rom.zip> <partition> <out_dir>      (extract)
       payload_extract.py <rom.zip> --list                     (list partitions)
"""
import bz2
import lzma
import os
import struct
import subprocess
import sys
import zipfile


def varint(b, i):
    v = s = 0
    while True:
        c = b[i]; i += 1
        v |= (c & 0x7F) << s; s += 7
        if c < 0x80:
            return v, i


def fields(b):
    """Yield (field_number, wire_type, value) for a protobuf message."""
    i = 0
    while i < len(b):
        key, i = varint(b, i)
        fn, wt = key >> 3, key & 7
        if wt == 0:
            v, i = varint(b, i)
        elif wt == 1:
            v = b[i:i + 8]; i += 8
        elif wt == 2:
            ln, i = varint(b, i); v = b[i:i + ln]; i += ln
        elif wt == 5:
            v = b[i:i + 4]; i += 4
        else:
            raise ValueError(f"unsupported wire type {wt}")
        yield fn, wt, v


def payload_offset(zip_path):
    """Byte offset and size of the stored payload.bin inside the zip."""
    with zipfile.ZipFile(zip_path) as z:
        info = z.getinfo("payload.bin")
        if info.compress_type != zipfile.ZIP_STORED:
            raise SystemExit("payload.bin is compressed inside the zip; unsupported")
    with open(zip_path, "rb") as f:
        f.seek(info.header_offset)
        h = f.read(30)
        name_len, extra_len = struct.unpack("<HH", h[26:30])
        return info.header_offset + 30 + name_len + extra_len, info.file_size


def parse(zip_path):
    base, _ = payload_offset(zip_path)
    f = open(zip_path, "rb")
    f.seek(base)
    hdr = f.read(24)
    if hdr[:4] != b"CrAU":
        raise SystemExit("not an OTA payload")
    version, manifest_size = struct.unpack(">QQ", hdr[4:20])
    sig_size = struct.unpack(">I", hdr[20:24])[0] if version >= 2 else 0
    hdr_len = 24 if version >= 2 else 20
    f.seek(base + hdr_len)
    manifest = f.read(manifest_size)
    data_start = base + hdr_len + manifest_size + sig_size
    block_size = 4096
    parts = {}
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
    zip_path = sys.argv[1]
    f, data_start, bs, parts = parse(zip_path)
    if sys.argv[2] == "--list":
        for n, (size, ops) in parts.items():
            types = sorted({o["type"] for o in ops})
            print(f"{n:24} {size/1e6:10.1f} MB  ops={len(ops):6}  op_types={types}")
        return
    name, out_dir = sys.argv[2], sys.argv[3]
    size, ops = parts[name]
    out = os.path.join(out_dir, name + ".img")
    with open(out, "wb") as o:
        o.truncate(size)
        for n, op in enumerate(ops):
            f.seek(data_start + op["off"])
            data = f.read(op["len"])
            t = op["type"]
            if t == 0:
                pass
            elif t == 1:
                data = bz2.decompress(data)
            elif t == 8:
                data = lzma.decompress(data)
            elif t == 14:
                data = subprocess.run(["zstd", "-d", "-c"], input=data, capture_output=True, check=True).stdout
            elif t in (6, 7):
                continue  # ZERO / DISCARD: file is already zero-filled
            else:
                raise SystemExit(f"unsupported operation type {t} (delta OTA?)")
            pos = 0
            for start, num in op["dst"]:
                chunk = data[pos:pos + num * bs]
                o.seek(start * bs)
                o.write(chunk)
                pos += num * bs
            if n % 200 == 0:
                print(f"  {n}/{len(ops)} operations", flush=True)
    print(f"wrote {out} ({size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
