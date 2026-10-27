#!/usr/bin/env python3
"""props.py <global_mount_root> <port_mount_root> <payload_g64_dir>

Writes the build.prop files of the pure 64-bit Global build into the payload:
Global's file as the base, POCO F4 (munch) hardware values set, Xiaomi 17 (pudding) hardware
values removed, and a fixed list of values carried from the current port (our earlier
decisions and munch tuning). Every change is listed below so it can be reviewed.
"""
import os
import sys

G, P, OUT = sys.argv[1:4]

FILES = {
    "system": "system/system/build.prop",
    "system_ext": "system_ext/etc/build.prop",
    "product": "product/etc/build.prop",
    "mi_ext": "mi_ext/etc/build.prop",
}

# partition -> {key: value} (set or add)
SET = {
    "system_ext": {
        # munch Bluetooth firmware has no LE Audio offload
        "ro.bluetooth.leaudio_offload.supported": "false",
        "persist.bluetooth.leaudio_offload.disabled": "true",
    },
    "product": {
        "ro.product.product.name": "miproduct_munch",
        "ro.sf.lcd_density": "440",
        "persist.miui.density_v2": "440",
        "ro.dalvik.vm.enable_uffd_gc": "false",          # porter's value for the munch kernel
        "ro.vendor.media_performance_class": "0",
        "ro.odm.build.media_performance_class": "0",
        "debug.config.media.video.aie.support": "true",
        "debug.media.video.chipset": "9",                # SM8250
        "ro.miui.affinity.sfui": "4-6",
        "ro.miui.affinity.sfre": "4-6",
        "ro.miui.affinity.sfuireset": "0-6",
        "persist.sys.computility.cpulevel": "4",
        "persist.sys.computility.gpulevel": "4",
        "persist.sys.turbosched.local.csprotect.enable": "6",
        "persist.sys.dexpreload.cpu_cores": "0-7",
        "persist.sys.dexpreload.big_prime_cores": "4-7",
        "persist.sys.dexpreload.other_cores": "0-3",
        # LE Audio profiles off (no LE Audio on this Bluetooth firmware)
        "bluetooth.profile.bap.unicast.client.enabled": "false",
        "bluetooth.profile.csip.set_coordinator.enabled": "false",
        "bluetooth.profile.mcp.server.enabled": "false",
        "bluetooth.profile.ccp.server.enabled": "false",
        "bluetooth.profile.vcp.controller.enabled": "false",
        "bluetooth.profile.bap.broadcast.source.enabled": "false",
        "bluetooth.profile.bap.broadcast.assist.enabled": "false",
        "bluetooth.profile.hap.client.enabled": "false",
    },
    "mi_ext": {
        "ro.product.mod_device": "munch_global",
    },
}

# partition -> keys removed (Xiaomi 17 hardware, or known problems on this phone)
REMOVE = {
    "product": [
        "traced.relay_producer_port",      # vsock: kernel has none, traced crash-loops
        "ro.display.enable_pwm_switch",    # Xiaomi 17 panel
        "persist.sys.xring_extm.enable",   # XRING memory extension (Xiaomi chip)
        "persist.vendor.power_telemetry_support",
        "persist.vendor.service.bt.adv_transport",
    ],
    "mi_ext": [
        "ro.vendor.miui.support_esim",
        "ro.audio.audiozoom",
        "ro.audio.ozo.channelmask.in",
        "vendor.mi_ric.ddr_freq_monitor",
        "ipa_callback_in_displayfeature",
        "ro.vendor.build.ab_ota_partitions",   # replaced by munch's list (carried below)
    ],
}

# keys carried from the port's product build.prop (munch hardware + earlier decisions)
CARRY_PRODUCT_PREFIXES = (
    "persist.vendor.bluetooth.", "vendor.media.vpp.aie.", "ro.vendor.audio.", "audio.offload.",
    "persist.sys.minfree_", "persist.sys.miui_animator_sched.",
)
CARRY_PRODUCT_KEYS = (
    "ro.control_privapp_permissions", "audio.safemedia.bypass", "ro.audio.hifi", "persist.audio.hifi",
    "persist.audio.hifi.volume", "persist.sys.miui.sf_cores", "persist.vendor.display.miui.composer_boost",
    "persist.sys.enable_templimit", "vendor.mm.enable.qcom_parser",
    "ro.surface_flinger.use_content_detection_for_refresh_rate", "ro.surface_flinger.set_idle_timer_ms",
    "ro.surface_flinger.set_touch_timer_ms", "dalvik.vm.image-dex2oat-threads", "dalvik.vm.image-dex2oat-filter",
    "dalvik.vm.heaptargetutilization", "dalvik.vm.heapminfree", "dalvik.vm.background-dex2oat-threads",
    "dalvik.vm.background-dex2oat-cpu-set", "persist.sys.background_blur_supported",
    "persist.sys.background_blur_status_default", "persist.sys.background_blur_version",
    "persist.sys.advanced_visual_release", "ro.miui.support_audiorecord_compress", "ro.miui.allow_app_playbackcapture",
    "ro.config.WlanAntTunerPolicy", "ro.wifi.tvendor.disable1", "ro.thermal.iec.enable",
    "persist.vendor.camera.gesture.emoji.support", "persist.vendor.camera.enablesetnfcpolling",
    "ro.video.recorder.startdelay", "persist.audio.video.large_jpegopt_enable", "ro.miui.build.region",
    "ro.vendor.build.ab_ota_partitions", "debug.sf.latch_unsignaled", "debug.sf.enable_hwc_vds",
    "debug.hwui.use_buffer_age", "persist.sys.gps.agpsOpt", "ro.miui.has_gmscore",
)


def read(path):
    lines = open(path, errors="surrogateescape").read().split("\n")
    return lines


def kv(line):
    s = line.strip()
    if not s or s.startswith("#") or "=" not in s:
        return None
    return s.split("=", 1)


port_product = {}
for line in read(os.path.join(P, FILES["product"])):
    p = kv(line)
    if p:
        port_product[p[0]] = p[1]
carry = {k: v for k, v in port_product.items()
         if k in CARRY_PRODUCT_KEYS or k.startswith(CARRY_PRODUCT_PREFIXES)}
SET.setdefault("product", {}).update({k: v for k, v in carry.items() if k not in SET["product"]})

report = []
for part, rel in FILES.items():
    lines = read(os.path.join(G, rel))
    sets, removes = dict(SET.get(part, {})), set(REMOVE.get(part, []))
    out, seen = [], set()
    for line in lines:
        p = kv(line)
        if p and p[0] in removes:
            report.append(f"{part}: - {p[0]}={p[1]}")
            continue
        if p and p[0] in sets:
            if p[1] != sets[p[0]]:
                report.append(f"{part}: ~ {p[0]}={p[1]} -> {sets[p[0]]}")
            line = f"{p[0]}={sets[p[0]]}"
            seen.add(p[0])
        out.append(line)
    added = [k for k in sets if k not in seen]
    if added:
        while out and out[-1] == "":
            out.pop()
        out += ["", "# POCO F4 (munch) values for the 64-bit Global build"] + [f"{k}={sets[k]}" for k in added] + [""]
        report += [f"{part}: + {k}={sets[k]}" for k in added]
    dst = os.path.join(OUT, part, os.path.relpath(rel, part) if part != "system" else "system/build.prop")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", errors="surrogateescape") as f:
        f.write("\n".join(out))
print("\n".join(report))
print(f"changes: {len(report)}")
