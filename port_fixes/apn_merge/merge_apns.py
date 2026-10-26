#!/usr/bin/env python3
"""merge_apns.py <xiaomi apns-conf.xml> <extra apns-conf.xml> <out apns-conf.xml>

TelephonyProvider on HyperOS loads APNs from Xiaomi's CarrierStudioApn (com.xiaomi.apn, its own
assets/apns-conf.xml) instead of /product/etc/apns-conf.xml. The port disables that source with an
overlay, so /product/etc/apns-conf.xml must hold everything: Xiaomi's list unchanged, plus every
entry of the extra file (Global ROM list with added IMS APNs) that Xiaomi's list does not have.
Entries are compared by mcc, mnc, apn, type, mvno_type and mvno_match_data; raw entry text is kept.
"""
import re
import sys

xiaomi, extra, out = sys.argv[1:4]
ENTRY = re.compile(r"<apn\s.*?/>", re.S)
ATTR = re.compile(r'(\w+)="([^"]*)"')


def key(entry):
    a = dict(ATTR.findall(entry))
    return tuple(a.get(k, "") for k in ("mcc", "mnc", "apn", "type", "mvno_type", "mvno_match_data"))


x = open(xiaomi, encoding="utf-8").read()
have = {key(e) for e in ENTRY.findall(x)}
added = []
for e in ENTRY.findall(open(extra, encoding="utf-8").read()):
    k = key(e)
    if k not in have:
        have.add(k)
        added.append("    " + e)
end = x.rindex("</apns>")
block = "\n    <!-- POCO F4: entries from the Global ROM list (incl. IMS APNs) that Xiaomi's list lacks -->\n" + "\n\n".join(added) + "\n"
open(out, "w", encoding="utf-8").write(x[:end] + block + x[end:])
print(f"xiaomi entries: {len(ENTRY.findall(x))}, added: {len(added)}")
for e in added:
    print("  +", key(e))
