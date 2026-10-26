#!/usr/bin/env python3
"""axml2xml.py <binary.xml> <out.xml> : convert Android binary XML (AXML) back to text XML.
Uses tools/axml.py's parser. Typed attribute values are written as Android XML literals
(true/false for booleans, decimal ints, @0x.. references, strings escaped)."""
import os
import sys
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import axml  # noqa: E402

T_REF, T_STRING, T_FLOAT, T_INT_DEC, T_INT_HEX, T_BOOL = 0x01, 0x03, 0x04, 0x10, 0x11, 0x12


def value(a):
    t, d = a["type"], a["data"]
    if a["raw"] is not None:
        return a["raw"]          # original text (e.g. mnc "01"); the typed value would drop the leading zero
    if t == T_STRING:
        return d
    if t == T_BOOL:
        return "true" if d else "false"
    if t == T_INT_DEC:
        return str(d - (1 << 32) if d & 0x80000000 else d)
    if t == T_INT_HEX:
        return "0x%x" % d
    if t == T_REF:
        return "@0x%08x" % d
    if a["raw"] is not None:
        return a["raw"]
    raise ValueError("unsupported attribute type 0x%x" % t)


nodes, _ = axml.parse(open(sys.argv[1], "rb").read())
ns_prefix = {}
out, depth, open_tag = ['<?xml version="1.0" encoding="utf-8"?>'], 0, False
pending_ns = []
had_text = False
for n in nodes:
    if n["t"] == 0x0100:
        ns_prefix[n["uri"]] = n["prefix"]; pending_ns.append(n)
    elif n["t"] == 0x0102:
        attrs = ""
        for ns in pending_ns:
            attrs += " xmlns:%s=%s" % (ns["prefix"], quoteattr(ns["uri"]))
        pending_ns = []
        for a in n["attrs"]:
            name = (ns_prefix[a["ns"]] + ":" if a["ns"] else "") + a["name"]
            attrs += " %s=%s" % (name, quoteattr(value(a)))
        out.append("    " * depth + "<%s%s>" % (n["name"], attrs))
        depth += 1
    elif n["t"] == 0x0103:
        depth -= 1
        if had_text:
            out[-1] += "</%s>" % n["name"]          # keep text exact: no whitespace before the end tag
        elif out[-1].lstrip().startswith("<%s" % n["name"]) and out[-1].endswith(">") and not out[-1].endswith("/>"):
            out[-1] = out[-1][:-1] + " />"
        else:
            out.append("    " * depth + "</%s>" % n["name"])
    elif n["t"] == 0x0104:
        out[-1] += escape(n["cdata"] or "")
    had_text = n["t"] == 0x0104
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
