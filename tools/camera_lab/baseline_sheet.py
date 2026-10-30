#!/usr/bin/env python3
"""P0 baseline sheet: one stand photo per back camera / mode of the native camera (Photo 1x, 0.6x ultra-wide, 2x, Ultra HD, Night),
copied to the laptop; only files created by this run are deleted from the phone. Never taps unless the camera is in front.
usage: baseline_sheet.py <out_dir>        then: measure_photos.py <out.csv> <out_dir>
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mode_sweep as m  # noqa: E402  (adb helpers, open_camera, tap_mode, camera_in_front)

CAM = "/sdcard/DCIM/Camera"
SHUTTER = ("540", "2088")
ZOOM = {"0.6x": ("307", "1711"), "2x": ("538", "1711")}  # zoom buttons ("0.6X zoom", "2.0X zoom") above the mode bar
VARIANTS = [("photo_1x", None, None), ("photo_0.6x", None, "0.6x"), ("photo_2x", None, "2x"),
            ("ultra_hd", "Ultra HD", None), ("night", "Night", None)]


def listing():
    return set(l.strip() for l in m.adb("shell", f"ls -1 {CAM}").splitlines() if l.strip())


def tap(x, y):
    if not m.camera_in_front():
        sys.exit("camera not in front - no tap sent")
    m.adb("shell", "input", "tap", x, y)


def shoot(out_dir, name, mode, zoom):
    m.open_camera()
    time.sleep(2)
    if not m.camera_in_front():
        sys.exit("camera not in front - stopping")
    if mode and not m.tap_mode(mode):
        return f"{name}: mode '{mode}' not found"
    time.sleep(4)
    if zoom:
        tap(*ZOOM[zoom])
        time.sleep(3)
    before = listing()
    tap(*SHUTTER)
    new = []
    for _ in range(30):
        time.sleep(1)
        new = sorted(f for f in listing() - before if f.startswith("IMG_") and f.endswith(".jpg"))
        if new:
            break
    if len(new) == 1:  # wait until the processed photo replaced the placeholder (size stable 5 s)
        last, stable = None, 0
        for _ in range(60):
            time.sleep(1)
            size = m.adb("shell", f"stat -c %s '{CAM}/{new[0]}'").strip()
            stable = stable + 1 if size == last else 0
            last = size
            if stable >= 5:
                break
    m.adb("shell", "am", "force-stop", "com.android.camera")
    if len(new) != 1:
        return f"{name}: no single new photo ({new}) - nothing copied or deleted"
    subprocess.run([m.ADB, "pull", f"{CAM}/{new[0]}", os.path.join(out_dir, name + ".jpg")], check=True, capture_output=True)
    m.adb("shell", f"rm '{CAM}/{new[0]}'; content delete --uri content://media/external/file --where \"_display_name='{new[0]}'\"")
    return f"{name}: {new[0]}"


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for name, mode, zoom in VARIANTS:
        print(shoot(out_dir, name, mode, zoom), flush=True)


if __name__ == "__main__":
    main()
