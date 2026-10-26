#!/usr/bin/env python3
"""Minimal Android binary XML (AXML) reader/writer.

  axml.py roundtrip <in.xml> <out.xml>           parse + re-encode unchanged
  axml.py add-pref  <in.xml> <out.xml> <title> <summary> [key] [tag] [after-key]
        insert <tag android:key android:title android:summary/> (tag defaults to
        Preference) after the element whose android:key is after-key, or as the
        last child of the root element (raw strings, no resource references)
  axml.py set-attr  <in.xml> <out.xml> <match-attr> <match-value> <attr> <value> [child-tag]
        on the first element whose <match-attr> is <match-value> (or on its first
        <child-tag> child), set the existing string attribute <attr> to <value>

Strings are kept as decoded text; the pool is rebuilt with every attribute-name
string that carries a resource id first, matching the resource map.
"""
import struct
import sys

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ATTR_IDS = {"key": 0x010101e8, "title": 0x010101e1, "summary": 0x010101e9}
T_STRING = 0x03
NO_INDEX = 0xFFFFFFFF


def u16(b, o): return struct.unpack_from("<H", b, o)[0]
def u32(b, o): return struct.unpack_from("<I", b, o)[0]


def read_pool(b, o):
    count, styles, flags, s_start, st_start = struct.unpack_from("<IIIII", b, o + 8)
    assert styles == 0, "style spans not supported"
    utf8 = bool(flags & 0x100)
    offs = struct.unpack_from("<%dI" % count, b, o + 28)
    out = []
    for off in offs:
        p = o + s_start + off
        if utf8:
            n = b[p]; p += 1
            if n & 0x80: p += 1                    # utf-16 length, 2-byte form
            n = b[p]; p += 1
            if n & 0x80: n = ((n & 0x7F) << 8) | b[p]; p += 1
            out.append(b[p:p + n].decode("utf-8"))
        else:
            n = u16(b, p); p += 2
            if n & 0x8000: n = ((n & 0x7FFF) << 16) | u16(b, p); p += 2
            out.append(b[p:p + 2 * n].decode("utf-16-le"))
    return out, utf8


def enc_len8(n):
    return bytes([n]) if n < 0x80 else bytes([0x80 | (n >> 8), n & 0xFF])


def write_pool(strings, utf8):
    data = bytearray(); offs = []
    for s in strings:
        offs.append(len(data))
        if utf8:
            raw = s.encode("utf-8")
            data += enc_len8(len(s.encode("utf-16-le")) // 2) + enc_len8(len(raw)) + raw + b"\0"
        else:
            raw = s.encode("utf-16-le"); n = len(raw) // 2
            data += (struct.pack("<H", n) if n < 0x8000 else struct.pack("<HH", 0x8000 | (n >> 16), n & 0xFFFF)) + raw + b"\0\0"
    while len(data) % 4: data += b"\0"
    s_start = 28 + 4 * len(strings)
    body = struct.pack("<%dI" % len(strings), *offs) + bytes(data)
    hdr = struct.pack("<HHIIIIII", 0x0001, 28, 28 + len(body), len(strings), 0, 0x100 if utf8 else 0, s_start, 0)
    return hdr + body


def parse(b):
    assert u16(b, 0) == 0x0003
    o = u16(b, 2)
    pool, utf8 = read_pool(b, o); o += u32(b, o + 4)
    resmap = []
    if u16(b, o) == 0x0180:
        n = (u32(b, o + 4) - 8) // 4
        resmap = list(struct.unpack_from("<%dI" % n, b, o + 8)); o += u32(b, o + 4)
    S = lambda i: None if i == NO_INDEX else pool[i]
    nodes = []
    while o < len(b):
        t, hs, size = struct.unpack_from("<HHI", b, o)
        line, comment = struct.unpack_from("<II", b, o + 8)
        e = o + hs
        n = {"t": t, "line": line, "comment": S(comment)}
        if t in (0x0100, 0x0101):
            n["prefix"], n["uri"] = S(u32(b, e)), S(u32(b, e + 4))
        elif t == 0x0102:
            ns, name, a_start, a_size, a_count, id_i, cls_i, sty_i = struct.unpack_from("<IIHHHHHH", b, e)
            n.update(ns=S(ns), name=S(name), idx=(id_i, cls_i, sty_i), attrs=[])
            for k in range(a_count):
                p = e + a_start + k * a_size
                ans, aname, raw, vsize, res0, dtype, data = struct.unpack_from("<IIIHBBI", b, p)
                n["attrs"].append({"ns": S(ans), "name": S(aname), "resid": resmap[aname] if aname < len(resmap) else None,
                                   "raw": S(raw), "type": dtype, "data": pool[data] if dtype == T_STRING else data})
        elif t == 0x0103:
            n["ns"], n["name"] = S(u32(b, e)), S(u32(b, e + 4))
        elif t == 0x0104:
            n["cdata"] = S(u32(b, e)); n["typed"] = b[e + 4:e + 12]
        else:
            raise ValueError("unknown chunk 0x%x" % t)
        nodes.append(n); o += size
    return nodes, utf8


def build(nodes, utf8):
    res_names = []   # (name, resid) pairs, in first-seen order
    others = []
    def need(s):
        if s is not None and s not in others: others.append(s)
    for n in nodes:
        for a in n.get("attrs", []):
            if a["resid"] is not None and (a["name"], a["resid"]) not in res_names:
                res_names.append((a["name"], a["resid"]))
    for n in nodes:
        for k in ("comment", "prefix", "uri", "ns", "name", "cdata"):
            need(n.get(k))
        for a in n.get("attrs", []):
            need(a["ns"]); need(a["raw"])
            if a["resid"] is None: need(a["name"])
            if a["type"] == T_STRING: need(a["data"])
    strings = [s for s, _ in res_names] + others
    ridx = {s: i for i, (s, _) in enumerate(res_names)}
    oidx = {s: len(res_names) + i for i, s in enumerate(others)}
    I = lambda s: NO_INDEX if s is None else oidx[s]
    out = bytearray()
    for n in nodes:
        t = n["t"]
        if t in (0x0100, 0x0101):
            ext = struct.pack("<II", I(n["prefix"]), I(n["uri"]))
        elif t == 0x0102:
            attrs = sorted(n["attrs"], key=lambda a: (a["resid"] is None, a["resid"] or 0))
            ext = struct.pack("<IIHHHHHH", I(n["ns"]), I(n["name"]), 20, 20, len(attrs), *n["idx"])
            for a in attrs:
                name_i = ridx[a["name"]] if a["resid"] is not None else I(a["name"])
                data = I(a["data"]) if a["type"] == T_STRING else a["data"]
                ext += struct.pack("<IIIHBBI", I(a["ns"]), name_i, I(a["raw"]), 8, 0, a["type"], data)
        elif t == 0x0103:
            ext = struct.pack("<II", I(n["ns"]), I(n["name"]))
        else:
            ext = struct.pack("<I", I(n["cdata"])) + n["typed"]
        out += struct.pack("<HHIII", t, 16, 16 + len(ext), n["line"], I(n["comment"])) + ext
    pool = write_pool(strings, utf8)
    rmap = struct.pack("<HHI", 0x0180, 8, 8 + 4 * len(res_names)) + struct.pack("<%dI" % len(res_names), *[r for _, r in res_names])
    body = pool + rmap + bytes(out)
    return struct.pack("<HHI", 0x0003, 8, 8 + len(body)) + body


def add_pref(nodes, title, summary, key, tag="Preference", after=None):
    depth = 0; root_end = None
    for i, n in enumerate(nodes):
        if n["t"] == 0x0102: depth += 1
        elif n["t"] == 0x0103:
            depth -= 1
            if depth == 0: root_end = i
    pos = root_end
    if after:
        start = next(i for i, n in enumerate(nodes) if n["t"] == 0x0102
                     and any(at["name"] == "key" and at["raw"] == after for at in n["attrs"]))
        depth = 0
        for i in range(start, len(nodes)):
            if nodes[i]["t"] == 0x0102: depth += 1
            elif nodes[i]["t"] == 0x0103:
                depth -= 1
                if depth == 0: pos = i + 1; break
    line = nodes[pos - 1]["line"]
    def a(name, val):
        return {"ns": ANDROID_NS, "name": name, "resid": ATTR_IDS[name], "raw": val, "type": T_STRING, "data": val}
    start = {"t": 0x0102, "line": line, "comment": None, "ns": None, "name": tag, "idx": (0, 0, 0),
             "attrs": [a("key", key), a("title", title), a("summary", summary)]}
    end = {"t": 0x0103, "line": line, "comment": None, "ns": None, "name": tag}
    nodes[pos:pos] = [start, end]


def set_attr(nodes, match_attr, match_value, attr, value, child=None):
    i = next(i for i, n in enumerate(nodes) if n["t"] == 0x0102
             and any(a["name"] == match_attr and a["raw"] == match_value for a in n["attrs"]))
    if child:
        depth = 0
        for j in range(i, len(nodes)):
            if nodes[j]["t"] == 0x0102:
                depth += 1
                if depth == 2 and nodes[j]["name"] == child: i = j; break
            elif nodes[j]["t"] == 0x0103:
                depth -= 1
                if depth == 0: sys.exit("no <%s> child" % child)
    a = next(a for a in nodes[i]["attrs"] if a["name"] == attr)
    assert a["type"] == T_STRING, "only string attributes"
    a["raw"] = a["data"] = value


if __name__ == "__main__":
    cmd, src, dst = sys.argv[1:4]
    nodes, utf8 = parse(open(src, "rb").read())
    if cmd == "add-pref":
        add_pref(nodes, sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else "maintainer",
                 sys.argv[7] if len(sys.argv) > 7 else "Preference", sys.argv[8] if len(sys.argv) > 8 else None)
    elif cmd == "set-attr":
        set_attr(nodes, *sys.argv[4:8], sys.argv[8] if len(sys.argv) > 8 else None)
    elif cmd != "roundtrip":
        sys.exit("unknown command")
    open(dst, "wb").write(build(nodes, utf8))
