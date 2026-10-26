#!/usr/bin/env python3
"""make_vendor_xml.py <global_vendor.xml> <xiaomi_globalization.xml> <xiaomi_device_vendor.xml> <out vendor.xml>

Builds res/xml/vendor.xml for the VoLTE overlay on com.android.carrierconfig (AOSP CarrierConfig).
An overlay replaces the whole resource, so the output is the Global ROM's common overlay rules
(CarrierConfigResCommon_Sys of Xiaomi 17 Global, 236 blocks) with these additions:
  1. right after the unfiltered default block: VoLTE available, switch visible and editable,
     off by default (the user turns it on) - applies to every operator in every country;
  2. all existing operator-specific blocks unchanged, so their explicit decisions still win;
  3. Xiaomi's per-device carrier list (CarrierStudio assets/device/<device>/res/xml/vendor_device.xml
     of a Global flagship): only VoLTE / video call / Wi-Fi calling availability per operator;
  4. Xiaomi's VoLTE blacklist (assets/default/globalization.xml of CarrierStudio);
  5. Bangladesh, one block per operator: VoLTE on by default, video call, Wi-Fi calling
     available but off by default, cellular preferred.
CarrierConfig applies matching blocks in file order; later blocks override earlier ones.
AOSP filters compare mnc as an exact string (no comma lists) and a block with an unknown
attribute (Xiaomi's cust_region / build_region) never matches, so such blocks are expanded or skipped.
"""
import re
import sys

base, globalization, device, out = sys.argv[1:5]
s = open(base, encoding="utf-8").read()

AOSP_ATTRS = {"mcc", "mnc", "spn", "imsi", "gid1", "gid2", "iccid", "cid", "name", "device"}
IMS_KEYS = ("carrier_volte_available_bool", "carrier_vt_available_bool", "carrier_wfc_ims_available_bool")

ALL_OPERATORS = """    <!-- POCO F4: VoLTE for every operator in every country (switch shown, off by default) -->
    <carrier_config>
        <boolean name="carrier_volte_available_bool" value="true" />
        <boolean name="editable_enhanced_4g_lte_bool" value="true" />
        <boolean name="hide_enhanced_4g_lte_bool" value="false" />
        <boolean name="enhanced_4g_lte_on_by_default_bool" value="false" />
    </carrier_config>
"""


def block(attrs, lines):
    body = "\n".join(f"        {l}" for l in lines)
    return f"    <carrier_config {attrs}>\n{body}\n    </carrier_config>"


# 1. insert after the first (unfiltered) block
first_end = s.index("</carrier_config>") + len("</carrier_config>\n")
s = s[:first_end] + ALL_OPERATORS + s[first_end:]
tail = []

# 3. Xiaomi device carrier list: IMS availability only, AOSP-compatible filters
d = open(device, encoding="utf-8").read()
dev_blocks, skipped = 0, 0
tail.append("    <!-- Xiaomi Global device carrier list (CarrierStudio vendor_device.xml): VoLTE / VT / Wi-Fi calling -->")
for attrs, body in re.findall(r"<carrier_config\s+([^>]*)>(.*?)</carrier_config>", d, re.S):
    names = dict(re.findall(r'(\w+)="([^"]*)"', attrs))
    lines = [f'<boolean name="{k}" value="{v}" />'
             for k, v in re.findall(r'<boolean name="([^"]+)" value="([^"]+)"\s*/>', body) if k in IMS_KEYS]
    if not lines:
        continue
    if set(names) - AOSP_ATTRS or "mcc" not in names:
        skipped += 1
        continue
    for mnc in names.get("mnc", "").split(",") if "mnc" in names else [None]:
        a = dict(names)
        if mnc is not None:
            a["mnc"] = mnc.strip()
        tail.append(block(" ".join(f'{k}="{v}"' for k, v in a.items()), lines))
        dev_blocks += 1

# 4. Xiaomi blacklist: carrier_config filters copied from globalization.xml, VoLTE not available
g = open(globalization, encoding="utf-8").read()
black = re.findall(r'<carrier_config (mcc="[^>]*)>\s*<boolean name="carrier_volte_unavailable_bool" value="true" />', g)
tail.append("    <!-- Xiaomi VoLTE blacklist (CarrierStudio globalization.xml) -->")
for attrs in black:
    tail.append(block(attrs, ['<boolean name="carrier_volte_available_bool" value="false" />']))

# 5. Bangladesh: GP (incl. Skitto) 01, Robi 02, Banglalink (incl. Ryze) 03, Teletalk 04, Airtel 07
tail.append("    <!-- Bangladesh: VoLTE on by default, video call, Wi-Fi calling available (off by default, cellular preferred) -->")
for mnc in ("01", "02", "03", "04", "07"):
    tail.append(block(f'mcc="470" mnc="{mnc}"', [
        '<boolean name="carrier_volte_available_bool" value="true" />',
        '<boolean name="enhanced_4g_lte_on_by_default_bool" value="true" />',
        '<boolean name="carrier_vt_available_bool" value="true" />',
        '<boolean name="carrier_wfc_ims_available_bool" value="true" />',
        '<boolean name="editable_wfc_mode_bool" value="true" />',
        '<boolean name="carrier_default_wfc_ims_enabled_bool" value="false" />',
        '<int name="carrier_default_wfc_ims_mode_int" value="1" />',
    ]))

end = s.rindex("</carrier_config_list>")
s = s[:end] + "\n".join(tail) + "\n" + s[end:]
open(out, "w", encoding="utf-8").write(s)
print(f"device blocks: {dev_blocks} (skipped {skipped} with Xiaomi-only filters), blacklist blocks: {len(black)}")
