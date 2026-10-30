#!/usr/bin/env python3
"""Take one test photo with the native camera (Photo mode, phone fixed on a stand), copy it to the laptop and delete it from the phone.

Safety: only a photo created by this run is touched — a NEW `IMG_*.jpg` (LMC: `F4_*.jpg`) that was not in DCIM/Camera before the shutter press.
If no new photo appears, nothing is deleted and the script exits with an error (an owner photo must never be picked up).
usage: ab_shot.py [--lmc] <out.jpg> [log_out.txt]      (--lmc: take the photo with LMC 8.4 instead of the Xiaomi camera)
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mode_sweep as m  # noqa: E402  (adb helpers, open_camera)

CAM = "/sdcard/DCIM/Camera"
LMC = "org.codeaurora.snapcam"


def listing():
    return set(l.strip() for l in m.adb("shell", f"ls -1 {CAM}").splitlines() if l.strip())  # LMC names contain spaces


def open_lmc():
    m.adb("shell", "am", "force-stop", LMC)
    m.adb("shell", "monkey", "-p", LMC, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(8)


def main():
    args = sys.argv[1:]
    lmc = "--lmc" in args
    args = [a for a in args if a != "--lmc"]
    out = args[0]
    log_out = args[1] if len(args) > 1 else None
    # Xiaomi camera saves IMG_*.jpg, LMC saves "F4_<date>.<config>.jpg"
    prefix, pkg = ("F4_", LMC) if lmc else ("IMG_", "com.android.camera")
    open_lmc() if lmc else m.open_camera()
    time.sleep(3)
    # never tap blind: if the camera did not come to the front, the tap would land in whatever app is open
    focus = m.adb("shell", "dumpsys window | grep -m1 mCurrentFocus")
    if pkg not in focus:
        sys.exit(f"camera not in front ({focus.strip()}) - no tap sent")
    before = listing()
    m.adb("logcat", "-c")
    if lmc:  # LMC's layout follows the phone's orientation, so a fixed tap can miss its shutter; the camera key works
        m.adb("shell", "input", "keyevent", "KEYCODE_CAMERA")
    else:
        m.adb("shell", "input", "tap", "540", "2088")
    new = []
    for _ in range(15):  # wait up to ~15 s for the JPEG to be written
        time.sleep(1)
        new = sorted(f for f in listing() - before if f.startswith(prefix) and f.endswith(".jpg"))
        if new:
            break
    if len(new) == 1:
        # parallel shots first save a preview-size placeholder and replace it with the processed photo later:
        # wait until the file size has not changed for 5 s (at most ~60 s)
        last, stable = None, 0
        for _ in range(60):
            time.sleep(1)
            size = m.adb("shell", f"stat -c %s '{CAM}/{new[0]}'").strip()
            stable = stable + 1 if size == last else 0
            last = size
            if stable >= 5:
                break
    if log_out:
        open(log_out, "w").write(m.adb("logcat", "-d", timeout=90))
    m.adb("shell", "am", "force-stop", pkg)
    if len(new) != 1:
        sys.exit(f"no single new photo after the shutter press (new files: {new}) - nothing copied or deleted")
    f = new[0]
    subprocess.run([m.ADB, "pull", f"{CAM}/{f}", out], check=True, capture_output=True)
    m.adb("shell", f"rm '{CAM}/{f}'; content delete --uri content://media/external/file --where \"_display_name='{f}'\"")
    print(f"{f} -> {out}")


if __name__ == "__main__":
    main()
