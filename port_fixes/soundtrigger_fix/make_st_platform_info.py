#!/usr/bin/env python3
"""make_st_platform_info.py <vendor sound_trigger_platform_info.xml> <out>

Google hotword ("Hey Google", vendor_uuid 7038ddc8-30f2-11e6-b0ac-40a8f03d3f15) has an LPI lsm_usecase
with a single handset mic and adm DEFAULT. There is no LPI calibration for that device (acdb 100,
ACDB_CMD_GET_LSM_INSTANCE_TABLE_SIZE returns -19); loading the model puts the ADSP into a restart loop
about once a second, and every audio write is dropped (no sound on speaker or Bluetooth).
This removes only that LPI block, so the hotword uses its NON_LPI_BARGE_IN path (FFECNS, FLUENCE_MIC).
Every other engine and setting is unchanged.
"""
import re
import sys

src, out = sys.argv[1:3]
s = open(src, encoding="utf-8").read()
GOOGLE = "7038ddc8-30f2-11e6-b0ac-40a8f03d3f15"

start = s.index(f'vendor_uuid="{GOOGLE}"')
cfg_start = s.rindex("<sound_model_config>", 0, start)
cfg_end = s.index("</sound_model_config>", start)
cfg = s[cfg_start:cfg_end]

blocks = list(re.finditer(r"[ \t]*<lsm_usecase>.*?</lsm_usecase>\n?", cfg, re.S))
lpi = [b for b in blocks if re.search(r'<param lpi_mode="LPI"\s*/>', b.group(0))]
if len(lpi) != 1:
    sys.exit(f"expected one LPI lsm_usecase in the Google section, found {len(lpi)}")
b = lpi[0]
note = "        <!-- POCO F4: LPI lsm_usecase removed (no LPI calibration for this mic; ADSP restart loop) -->\n"
cfg = cfg[:b.start()] + note + cfg[b.end():]
s = s[:cfg_start] + cfg + s[cfg_end:]
open(out, "w", encoding="utf-8").write(s)
print(f"removed LPI lsm_usecase ({b.end() - b.start()} bytes) from {GOOGLE}")
