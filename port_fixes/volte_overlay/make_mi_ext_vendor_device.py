#!/usr/bin/env python3
"""make_mi_ext_vendor_device.py <current vendor_device.xml> <xiaomi_device_vendor.xml> <out vendor_device.xml> [<CarrierStudio assets/device dir>]

/mi_ext/product/etc/vendor_device.xml is the last layer read by Xiaomi's CarrierStudio
(com.xiaomi.carrierconfig), and TeleService merges CarrierStudio's bundle over the AOSP CarrierConfig one.
CarrierStudio's base (res/xml/vendor_miui.xml) starts with VoLTE / VT / Wi-Fi calling = false for every
operator; a real Xiaomi device turns them on per operator in assets/device/<device>/res/xml/vendor_device.xml.
munch has no such file, so this adds, in Xiaomi's own format (mnc lists and cust_region filters work here):
  1. the current file unchanged (VoLTE globalization + Xiaomi VoLTE blacklist);
  2. optional: every Xiaomi device's per-operator VoLTE / VT / Wi-Fi calling value, by majority vote across
     devices (operator-specific "false" decisions keep winning where most devices make them);
  3. a Global flagship's per-operator VoLTE / VT / Wi-Fi calling entries on top (other keys such as 5G SA / VoNR
     are left out);
  4. Bangladesh: VoLTE on by default, VT, Wi-Fi calling available (off by default, cellular preferred).
"""
import collections
import os
import re
import sys

current, device, out = sys.argv[1:4]
devices_dir = sys.argv[4] if len(sys.argv) > 4 else None
s = open(current, encoding="utf-8").read()
IMS_KEYS = ("carrier_volte_available_bool", "carrier_vt_available_bool", "carrier_wfc_ims_available_bool")
BLOCK = re.compile(r"<carrier_config\s+([^>]*[^/>])>(.*?)</carrier_config>", re.S)  # skips <carrier_config include=".."/>
BOOL = re.compile(r'<boolean name="([^"]+)" value="([^"]+)"\s*/>')

add = [""]
if devices_dir:
    votes = collections.defaultdict(collections.Counter)
    order = []
    for dev in sorted(os.listdir(devices_dir)):
        xml = os.path.join(devices_dir, dev, "res/xml/vendor_device.xml")
        for attrs, body in BLOCK.findall(open(xml, encoding="utf-8", errors="ignore").read()):
            attrs = " ".join(attrs.split())
            for k, v in BOOL.findall(body):
                if k in IMS_KEYS:
                    if (attrs, k) not in votes:
                        order.append((attrs, k))
                    votes[(attrs, k)][v] += 1
    merged = collections.OrderedDict()
    for attrs, k in order:
        c = votes[(attrs, k)]
        merged.setdefault(attrs, []).append((k, "true" if c["true"] >= c["false"] else "false"))
    add.append(f"    <!-- POCO F4: all Xiaomi devices' carrier lists (CarrierStudio assets/device, {len(os.listdir(devices_dir))} devices), majority value -->")
    for attrs, kv in merged.items():
        add.append(f"    <carrier_config {attrs}>\n" + "\n".join(
            f'        <boolean name="{k}" value="{v}" />' for k, v in kv) + "\n    </carrier_config>")
    print(f"all-device blocks: {len(merged)}")

d = open(device, encoding="utf-8").read()
add += ["", "    <!-- POCO F4: Xiaomi Global device carrier list (CarrierStudio assets/device/pudding): VoLTE / VT / Wi-Fi calling -->"]
n = 0
for attrs, body in BLOCK.findall(d):
    lines = [f'        <boolean name="{k}" value="{v}" />'
             for k, v in re.findall(r'<boolean name="([^"]+)" value="([^"]+)"\s*/>', body) if k in IMS_KEYS]
    if lines:
        add.append(f"    <carrier_config {attrs.strip()}>\n" + "\n".join(lines) + "\n    </carrier_config>")
        n += 1

add.append("""
    <!-- POCO F4: Bangladesh - GP (incl. Skitto) 01, Robi 02, Banglalink (incl. Ryze) 03, Teletalk 04, Airtel 07.
         VoLTE on by default, video call, Wi-Fi calling available (GP and Banglalink launched VoWiFi in 2026),
         off by default, cellular preferred. -->
    <carrier_config mcc="470" mnc="01,02,03,04,07">
        <boolean name="carrier_volte_available_bool" value="true" />
        <boolean name="enhanced_4g_lte_on_by_default_bool" value="true" />
        <boolean name="carrier_vt_available_bool" value="true" />
        <boolean name="carrier_wfc_ims_available_bool" value="true" />
        <boolean name="editable_wfc_mode_bool" value="true" />
        <boolean name="carrier_default_wfc_ims_enabled_bool" value="false" />
        <int name="carrier_default_wfc_ims_mode_int" value="1" />
    </carrier_config>
""")
# like a real Xiaomi device file: Xiaomi's shared defaults first, so every rule below overrides them
INCLUDES = ("globalization.xml", "default_v2.9.9.xml")
head = s.index("<carrier_config_list>") + len("<carrier_config_list>")
s = s[:head] + "\n    <!-- POCO F4: CarrierStudio assets/default, as included by current Xiaomi device files -->\n" + "".join(
    f'    <carrier_config include="{f}"/>\n' for f in INCLUDES) + s[head:]
end = s.rindex("</carrier_config_list>")
s = s[:end] + "\n".join(add) + "\n" + s[end:]
open(out, "w", encoding="utf-8").write(s)
print(f"device blocks: {n}")
