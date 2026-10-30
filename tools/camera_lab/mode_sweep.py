#!/usr/bin/env python3
"""Logged mode sweep of MiuiCamera (MASTER_PLAN P2): open every visible mode once, take no photo, and record
camera id, HAL session opmode, MIA graph nodes and crashes from logcat.

Modes are found by their on-screen label (uiautomator dump), in the mode bar or the "More" panel.
usage: mode_sweep.py <out.md> [label ...]      (default: every label found)
"""
import os
import re
import subprocess
import sys
import time

ADB = os.path.expanduser("~/Android/Sdk/platform-tools/adb")
SKIP = {"Portrait"}  # back Portrait crashes the app (known, see MODE_TEST_RESULTS.md)
BAR = ["Pro", "Video", "Photo", "Portrait", "Documents"]


def adb(*args, timeout=30):
    return subprocess.run([ADB, *args], capture_output=True, text=True, errors="replace", timeout=timeout).stdout


def ui():
    adb("shell", "uiautomator", "dump", "/sdcard/ui_sweep.xml")
    x = adb("shell", "cat", "/sdcard/ui_sweep.xml")
    adb("shell", "rm", "-f", "/sdcard/ui_sweep.xml")
    out = {}
    for m in re.finditer(r'text="([^"]+)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', x):
        out.setdefault(m.group(1), ((int(m.group(2)) + int(m.group(4))) // 2, (int(m.group(3)) + int(m.group(5))) // 2))
    return out


def open_camera():
    adb("shell", "am", "force-stop", "com.android.camera")
    adb("shell", "am", "start", "-n", "com.android.camera/.Camera")
    time.sleep(7)
    for _ in range(3):  # close pop-ups in front of the camera (carrier data-usage dialog, app crash dialogs)
        if "com.android.camera/" in adb("shell", "dumpsys window | grep -m1 mCurrentFocus"):
            break
        adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(1.5)


def open_more_panel():
    adb("shell", "input", "swipe", "540", "1880", "540", "1000", "300")
    time.sleep(2)


def camera_in_front():
    return "com.android.camera/" in adb("shell", "dumpsys window | grep -m1 mCurrentFocus")


def tap_mode(label):
    """Tap a mode by label; returns True when found."""
    if not camera_in_front():  # labels would come from whatever app is open - never tap them
        sys.exit(f"camera not in front - not tapping '{label}'")
    labels = ui()
    if label not in labels:
        open_more_panel()
        labels = ui()
    if label not in labels:
        return False
    x, y = labels[label]
    adb("shell", "input", "tap", str(x), str(y))
    return True


def sweep_one(label):
    open_camera()
    if label == "Photo":  # Photo is already selected after start; leave it first so the switch is logged
        tap_mode("Video")
        time.sleep(5)
    adb("logcat", "-c")
    found = tap_mode(label)
    time.sleep(8)
    log = adb("logcat", "-d", timeout=60)
    crash = adb("logcat", "-d", "-b", "crash")
    pick = lambda pat: list(dict.fromkeys(re.findall(pat, log)))
    return {
        "label": label, "found": found,
        "module": pick(r"enterNewMode: newModule=([A-Za-z]+)"),
        "cid": pick(r"openCamera: cid: \d+ -> (\d+)"),
        # every session start prints "setOperatingMode mode = <decimal>"; shown as hex like the HAL constants
        "opmode": [hex(int(x)) for x in pick(r"setOperatingMode mode = (\d+)")],
        "graph": pick(r"getGraphID:\d+\]:E operation_mode:(0x[0-9a-f]+)[^\n]*camera_mode:(0x[0-9a-f]+)"),
        "nodes": pick(r"createNode node type: (\d+)"),  # MIA nodes built for this mode's own session
        # only crashes of the camera app or the camera HAL count (other apps crash too, e.g. Facebook)
        "crash": "yes" if re.search(r">>> com\.android\.camera <<<|Process: com\.android\.camera|camera\.provider|cameraserver", crash) else "no",
    }


def main():
    out = sys.argv[1]
    labels = sys.argv[2:]
    if not labels:
        open_camera()
        if not camera_in_front():
            sys.exit("camera not in front - no mode labels read, nothing tapped")
        bar = [l for l in BAR if l in ui()]
        open_more_panel()
        more = [l for l in ui() if l not in bar and len(l) < 25 and not re.search(r"\d", l)]
        labels = bar + more
    labels = [l for l in labels if l not in SKIP]
    job = "P2: mode sweep on phone (every mode, no photos)"
    wlog = os.path.expanduser("~/.local/bin/wlog")
    if os.path.exists(wlog):  # live progress on the work dashboard
        subprocess.run([wlog, "job", "start", job, str(len(labels))])
    rows = []
    for i, label in enumerate(labels):
        if os.path.exists(wlog):
            subprocess.run([wlog, "job", "progress", job, str(i), str(len(labels)), f"opening mode: {label}"])
        r = sweep_one(label)
        rows.append(r)
        print(f"{label}: {r['module']} cid={r['cid']} opmode={r['opmode']} crash={r['crash']}", flush=True)
    adb("shell", "am", "force-stop", "com.android.camera")
    if os.path.exists(wlog):
        subprocess.run([wlog, "job", "end", job])
    md = ["# Mode sweep (generated)\n",
          f"{time.strftime('%Y-%m-%d %H:%M')} by `tools/camera_lab/mode_sweep.py`; no photo taken; back Portrait skipped (known crash).\n",
          "| Label | Module | Camera id | Session opmode | MIA graph (opmode, camera_mode) | MIA node types | Crash |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r["found"]:
            md.append(f"| {r['label']} | not found on screen | | | | | |")
            continue
        md.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            r["label"], ", ".join(r["module"]), ", ".join(r["cid"]), ", ".join(r["opmode"]),
            ", ".join("/".join(g) for g in r["graph"]), ", ".join(r["nodes"]), r["crash"]))
    open(out, "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
