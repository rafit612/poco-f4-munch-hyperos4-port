#!/usr/bin/env python3
"""Summarise per-camera specs from a saved `dumpsys media.camera` file."""
import re
import sys

TAGS = {
    "facing": "android.lens.facing",
    "pixel_array": "android.sensor.info.pixelArraySize",
    "active_array": "android.sensor.info.activeArraySize",
    "max_res_pixel_array": "android.sensor.info.pixelArraySizeMaximumResolution",
    "physical_size": "android.sensor.info.physicalSize",
    "aperture": "android.lens.info.availableApertures",
    "focal": "android.lens.info.availableFocalLengths",
    "ois": "android.lens.info.availableOpticalStabilization",
    "min_focus": "android.lens.info.minimumFocusDistance",
    "iso": "android.sensor.info.sensitivityRange",
    "max_analog_iso": "android.sensor.maxAnalogSensitivity",
    "exposure": "android.sensor.info.exposureTimeRange",
    "flash": "android.flash.info.available",
    "af_modes": "android.control.afAvailableModes",
    "video_stab": "android.control.availableVideoStabilizationModes",
    "fps_ranges": "android.control.aeAvailableTargetFpsRanges",
    "hw_level": "android.info.supportedHardwareLevel",
    "caps": "android.request.availableCapabilities",
    "physical_ids": "android.logicalMultiCamera.physicalIds",
    "zoom_ratio": "android.control.zoomRatioRange",
    "xiaomi_role": "com.xiaomi.cameraid.role.cameraId",
    "sensor_vendor_id": "xiaomi.sensor.vendorId",
    "jpeg_sizes": "android.scaler.availableStreamConfigurations",
    "high_speed": "android.control.availableHighSpeedVideoConfigurations",
}
HW = {0: "LIMITED", 1: "FULL", 2: "LEGACY", 3: "LEVEL_3", 4: "EXTERNAL"}
FACING = {0: "front", 1: "back", 2: "external"}
VSTAB = {0: "off", 1: "EIS", 2: "preview-EIS"}
OIS = {0: "off", 1: "on"}


def value_after(lines, i):
    """Collect the bracketed value lines that follow a tag line."""
    out = []
    for line in lines[i + 1:i + 400]:
        s = line.strip()
        if s.startswith("["):
            out.append(s.strip("[] "))
        else:
            break
    return " ".join(out)


def nums(s):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s)]


def main(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    blocks = re.split(r"== Camera HAL device device@[\d.]+/legacy/(\d+) \([^)]*\) static information: ==", text)
    for k in range(1, len(blocks), 2):
        cam_id, body = blocks[k], blocks[k + 1].split("dumpState")[0]
        lines = body.splitlines()
        v = {}
        for i, line in enumerate(lines):
            for key, tag in TAGS.items():
                if key not in v and re.match(rf"\s*{re.escape(tag)} \(", line):
                    v[key] = value_after(lines, i)
        print(f"\n===== Camera ID {cam_id} =====")
        f = nums(v.get("facing", ""))
        print(f"  facing        : {FACING.get(int(f[0]), f) if f else '?'}")
        print(f"  xiaomi role   : {v.get('xiaomi_role', '-')}")
        if v.get("physical_ids"):
            ids = [int(x) for x in nums(v["physical_ids"])]
            chars = "".join(chr(c) for c in ids if c)
            print(f"  LOGICAL camera, physical IDs: {chars!r}")
        pa = nums(v.get("pixel_array", ""))
        if pa:
            print(f"  pixel array   : {int(pa[0])}x{int(pa[1])} = {pa[0]*pa[1]/1e6:.1f} MP")
        mr = nums(v.get("max_res_pixel_array", ""))
        if mr:
            print(f"  max-res array : {int(mr[0])}x{int(mr[1])} = {mr[0]*mr[1]/1e6:.1f} MP (full resolution mode)")
        ps = nums(v.get("physical_size", ""))
        if ps:
            diag = (ps[0] ** 2 + ps[1] ** 2) ** 0.5
            line = f"  sensor size   : {ps[0]:.2f} x {ps[1]:.2f} mm (diag {diag:.2f} mm, ~1/{16/diag:.2f}\")"
            if pa:
                line += f", binned pixel {ps[0]/pa[0]*1000:.2f} um"
            if mr:
                line += f", native pixel {ps[0]/mr[0]*1000:.2f} um"
            print(line)
        ap, fl = nums(v.get("aperture", "")), nums(v.get("focal", ""))
        if ap and fl:
            eq = ""
            if ps:
                crop = 43.27 / ((ps[0] ** 2 + ps[1] ** 2) ** 0.5)
                eq = f" (~{fl[0]*crop:.0f} mm equiv.)"
            print(f"  lens          : f/{ap[0]:.2f}, {fl[0]:.2f} mm{eq}")
        o = nums(v.get("ois", ""))
        if o:
            print(f"  OIS           : {'yes' if 1 in o else 'no'}")
        mf = nums(v.get("min_focus", ""))
        if mf:
            print(f"  autofocus     : {'fixed focus' if mf[0] == 0 else f'yes, closest {100/mf[0]:.1f} cm'}")
        iso = nums(v.get("iso", ""))
        if iso:
            print(f"  ISO range     : {int(iso[0])}-{int(iso[1])}" + (f" (analog max {int(nums(v['max_analog_iso'])[0])})" if v.get("max_analog_iso") else ""))
        ex = nums(v.get("exposure", ""))
        if ex:
            print(f"  shutter range : 1/{1e9/ex[0]:.0f} s to {ex[1]/1e9:.2f} s")
        fa = nums(v.get("flash", ""))
        if fa:
            print(f"  flash         : {'yes' if fa[0] else 'no'}")
        vs = nums(v.get("video_stab", ""))
        if vs:
            print(f"  video stab    : {', '.join(VSTAB.get(int(x), str(x)) for x in vs)}")
        fps = nums(v.get("fps_ranges", ""))
        if fps:
            print(f"  max preview/video fps: {int(max(fps))}")
        hs = nums(v.get("high_speed", ""))
        if hs:
            print(f"  slow-mo       : up to {int(max(hs[3::5]))} fps")
        zr = nums(v.get("zoom_ratio", ""))
        if zr:
            print(f"  zoom ratio    : {zr[0]:.2f}x - {zr[1]:.2f}x")
        hw = nums(v.get("hw_level", ""))
        if hw:
            print(f"  Camera2 level : {HW.get(int(hw[0]), hw[0])}")
        if v.get("caps"):
            print(f"  capabilities  : {v['caps']}")
        sc = v.get("jpeg_sizes", "")
        # stream configs are (format, w, h, output/input) quadruples; JPEG = 33 (0x21)
        q = [int(x) for x in nums(sc)]
        jpeg = [(q[i + 1], q[i + 2]) for i in range(0, len(q) - 3, 4) if q[i] == 33 and q[i + 3] == 0]
        if jpeg:
            w, h = max(jpeg, key=lambda t: t[0] * t[1])
            print(f"  largest JPEG  : {w}x{h} = {w*h/1e6:.1f} MP")


if __name__ == "__main__":
    main(sys.argv[1])
