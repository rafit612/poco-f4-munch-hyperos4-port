#!/bin/bash
# Patch the camera app's watermark device name: the port's MiuiCamera 6.7 loads a fixed "Marble" device profile whose
# watermark table (com.mi.device.Marble.d()) is {"XIAOMI", "17 PRO"}; this sets it to {"POCO", "F4 5G"}.
# It also sets the profile's filter set (Marble.E1(), {17} = no Leica looks) to {25} = LC_CUSTOM_BACK: Leica Vivid,
# Natural, Chrome, Classic, Contemporary, Eternal, Brass, Teal, IModelA. Photo filters are LUTs inside the app.
# Portrait: Marble.C() (largest bokeh picture width) 4000 -> 4625 like the official app's Munch_pro profile, so the
# depth stream uses the OV64B40's native 4624x3472 instead of a forced 4000x3000.
# Short video: Marble.H1() (short-video engine generation) 3 -> 4. The app runs the new MiLiveMaster module, but with 3
# it picks the old controller and never adds the paused-state "delete segment"/"finish" buttons, so clips can't be saved.
# 3 and 4 load the same native libraries (miffmpeg + MiShortVideoSDK).
# Front camera: Marble.g9() (front binning) true -> false, Marble.K4() (front picture halving) added -> false,
# Marble.m0() (picture size ratio tolerance) 0.005 -> 0.006 so the F4 front 4:3 sizes (0.0055 off) are not skipped.
# Video bitrate: Marble.C0() returns tools/re/VideoBitrates.java (30 and 60 fps, HEVC and H.264) instead of the Common table
# (30 fps HEVC only; 60 fps fell back to the vendor 30 fps values, 4K60 = 50 Mbit/s).
# Abandoned night shots keep a normal small preview instead of a 16 MiB zero-padded file (see block 4 below).
# Ultra-wide distortion correction defaults to off: its GPU engine crashes the app on this port (block 5 below).
# Zoom: Marble.u6() (super resolution) true -> false, so 2x+ photos are cropped normally instead of an unmerged SR frame.
# Each change is skipped when the APK already has it.
# usage: camera_watermark_patch.sh <MiuiCamera.apk> <out.apk>
# Needs: Java 21, Android build-tools, the jadx-headless-mcp 0.7.1 "-all" JAR (contains dexlib2/smali) in $JAR.
set -e
IN=${1:?MiuiCamera.apk}; OUT=${2:?out.apk}
JAR=${JAR:-$HOME/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar}
BT=${BT:-$HOME/Android/Sdk/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
D="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
javac -d "$W/cls" -cp "$JAR" "$D/Smali.java"
unzip -q -o "$IN" 'classes*.dex' -d "$W"
DEX=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Lcom/mi/device/Marble;'" && basename "$d" && break; done)
[ -n "$DEX" ] || { echo "Marble class not found"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX" "$W/smali"
# Own helper classes (tools/re/*.java besides Smali.java), compiled to smali and copied into the dex that calls them.
SDK=${SDK:-$HOME/Android/Sdk}; AJ=$(ls -d "$SDK"/platforms/android-3[0-9]*/android.jar | sort -V | tail -1)
javac --release 8 -nowarn -cp "$AJ" -d "$W/owncls" "$D/PlaceholderTrim.java" "$D/VideoBitrates.java" 2>/dev/null
mkdir -p "$W/owndex"; "$BT/d8" --min-api 30 --lib "$AJ" --output "$W/owndex" "$W"/owncls/com/munch/camera/*.class
java -cp "$JAR:$W/cls" Smali d "$W/owndex/classes.dex" "$W/ownsmali"
F="$W/smali/com/mi/device/Marble.smali"
python3 - "$F" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
start = s.index(".method public d()Landroid/util/SparseArray;"); end = s.index(".end method", start)
body = s[start:end]
if body.count('"POCO"') == 2 and body.count('"F4 5G"') == 2:
    print("watermark: already patched")
else:
    assert body.count('"XIAOMI"') == 2 and body.count('"17 PRO"') == 2, "unexpected Marble.d() body"
    body = body.replace('"XIAOMI"', '"POCO"').replace('"17 PRO"', '"F4 5G"')
s = s[:start] + body + s[end:]
m = re.search(r"(\.method public final E1\(\)\[I\s+\.registers 1\s+const/16 p0, )(0x[0-9a-f]+)(\s+filled-new-array \{p0\}, \[I)", s)
assert m, "unexpected Marble.E1() body"
if m.group(2) == "0x19":
    print("filter set: already 25")
else:
    assert m.group(2) == "0x11", "unexpected Marble.E1() value " + m.group(2)
    s = s[:m.start(2)] + "0x19" + s[m.end(2):]
m = re.search(r"(\.method public C\(\)I\s+\.registers 1\s+const p0, )(0x[0-9a-f]+)", s)
assert m, "unexpected Marble.C() body"
if m.group(2) == "0x1211":
    print("bokeh width: already 4625")
else:
    assert m.group(2) == "0xfa0", "unexpected Marble.C() value " + m.group(2)
    s = s[:m.start(2)] + "0x1211" + s[m.end(2):]
m = re.search(r"(\.method public H1\(\)I\s+\.registers 1\s+const p0, )(0x[0-9a-f]+)", s)
assert m, "unexpected Marble.H1() body"
if m.group(2) == "0x4":
    print("short video generation: already 4")
else:
    assert m.group(2) == "0x3", "unexpected Marble.H1() value " + m.group(2)
    s = s[:m.start(2)] + "0x4" + s[m.end(2):]
if "Lcom/munch/camera/VideoBitrates;" in s:
    print("video bitrates: already patched")
else:
    assert ".method public C0()Ljava/util/HashMap;" not in s, "Marble already overrides C0()"
    s += ("\n.method public C0()Ljava/util/HashMap;\n    .registers 1\n\n"
          "    invoke-static {}, Lcom/munch/camera/VideoBitrates;->table()Ljava/util/HashMap;\n\n"
          "    move-result-object p0\n\n    return-object p0\n.end method\n")
# Front camera: Marble (POCO F5) treats its front sensor as full-resolution quad-Bayer. g9() = true makes the app process
# front shots "binned" at half the picture size, and the inherited K4() halves the front picture size itself. Both off.
# The picture-size picker also requires |ratio - 4:3| < Marble.m0() = 0.005; the F4 front sizes 5184x3904 / 2592x1952
# are 0.0055 off, so it fell back to the first exact 4:3 size, 1600x1200 (processed at 800x600). 0.006 lets them through;
# the back camera's sizes are already within 0.005, so its choice does not change.
m = re.search(r"(\.method public m0\(\)F\s+\.registers 1\s+const p0, )(0x[0-9a-f]+)", s)
assert m, "unexpected Marble.m0() body"
if m.group(2) == "0x3bc49ba6":
    print("picture size ratio tolerance (m0): already 0.006")
else:
    assert m.group(2) == "0x3ba3d70a", "unexpected Marble.m0() value " + m.group(2)
    s = s[:m.start(2)] + "0x3bc49ba6" + s[m.end(2):]
m = re.search(r"(\.method public g9\(\)Z\s+\.registers 1\s+const/4 p0, )(0x[01])", s)
assert m, "unexpected Marble.g9() body"
if m.group(2) == "0x0":
    print("front binning (g9): already off")
else:
    s = s[:m.start(2)] + "0x0" + s[m.end(2):]
if ".method public K4()Z" in s:
    print("front picture halving (K4): already overridden")
else:
    s += "\n.method public K4()Z\n    .registers 1\n\n    const/4 p0, 0x0\n\n    return p0\n.end method\n"
# Zoom photos: with u6() (super resolution supported) the app shoots an 8-frame SR burst at 2x and above, but the munch MIA
# graph has no SR node and the HAL SR path is off, so one unmerged, uncropped full-frame image was saved (2x looked like 1x,
# noisy). u6() = false makes zoom use the normal 5-frame path with the HAL crop (only Camera2Module's SR check calls u6()).
m = re.search(r"(\.method public final u6\(\)Z\s+\.registers 1\s+const/4 p0, )(0x[01])", s)
assert m and s.count(" u6()Z") == 1, "unexpected Marble.u6()"
if m.group(2) == "0x0":
    print("super resolution (u6): already off")
else:
    s = s[:m.start(2)] + "0x0" + s[m.end(2):]
open(p, "w").write(s)
PY
mkdir -p "$W/smali/com/munch/camera"; cp "$W/ownsmali/com/munch/camera/VideoBitrates.smali" "$W/smali/com/munch/camera/"
mkdir -p "$W/stage"
java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23     # dex 035, like the original
# Two modes are both called "Short video": MiLiveMaster (segments, music, 720p) and the classic one (FunModule, 1080p).
# Label MiLiveMaster with the app's existing string "Xiaomi Short Video" (string/gvp) so they can be told apart.
DEX2=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Lcom/xiaomi/milive/mode/MiLiveMasterModuleEntry;'" && basename "$d" && break; done)
[ -n "$DEX2" ] && [ "$DEX2" != "$DEX" ] || { echo "MiLiveMasterModuleEntry not found in a separate dex"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX2" "$W/smali2"
python3 - "$W/smali2/com/xiaomi/milive/mode/MiLiveMasterModuleEntry.smali" <<'PY2'
import sys
p = sys.argv[1]; s = open(p).read()
if s.count("const v1, 0x7f140969") == 1:
    print("short video label: already Xiaomi Short Video")
else:
    assert s.count("const v1, 0x7f140b7e") == 1, "unexpected MiLiveMasterModuleEntry label"
    s = s.replace("const v1, 0x7f140b7e", "const v1, 0x7f140969")
open(p, "w").write(s)
PY2
java -cp "$JAR:$W/cls" Smali a "$W/smali2" "$W/stage/$DEX2" 23
# VLOG crash: VLOG asks the top-bar factory aa.j5.E() for item 172, which this build does not define; release builds throw
# "Illegal config item: 172", debug builds only log it and return a placeholder item. Take the debug path.
DEX3=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Laa/j5;'" && basename "$d" && break; done)
[ -n "$DEX3" ] && [ "$DEX3" != "$DEX" ] && [ "$DEX3" != "$DEX2" ] || { echo "aa.j5 not found in a separate dex"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX3" "$W/smali3"
python3 - "$W/smali3/aa/j5.smali" <<'PY3'
import sys
p = sys.argv[1]; s = open(p).read()
old = "    invoke-static {}, Lcom/android/camera/log/LogUtil;->isDebugOsBuild()Z\n\n    move-result v0\n\n    if-eqz v0, :cond_37\n\n    const-string v0, \"illegal config item: \""
new = "    const/4 v0, 0x1\n\n    if-eqz v0, :cond_37\n\n    const-string v0, \"illegal config item: \""
if s.count(new) == 1:
    print("VLOG top-bar fallback: already patched")
else:
    assert s.count(old) == 1, "unexpected aa.j5.E() fallback"
    s = s.replace(old, new)
open(p, "w").write(s)
PY3
java -cp "$JAR:$W/cls" Smali a "$W/smali3" "$W/stage/$DEX3" 23
# Abandoned night shots: a parallel shot whose capture start arrives after the mode was left (e.g. switching to video while
# night shots are still queued) is dropped, and its file stays a 1440x1080 preview padded with zeros to 16 MiB. Up.b/Up.f.A0
# (final image dropped) and Xp.m$b.a (onParallelDataAbandoned) now call PlaceholderTrim.trim(savePath), which cuts the zeros.
DEX4=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'LUp/b;'" && basename "$d" && break; done)
for x in "$DEX" "$DEX2" "$DEX3"; do [ -n "$DEX4" ] && [ "$DEX4" != "$x" ] || { echo "Up.b not found in a separate dex"; exit 1; }; done
java -cp "$JAR:$W/cls" Smali d "$W/$DEX4" "$W/smali4"
mkdir -p "$W/smali4/com/munch/camera"; cp "$W/ownsmali/com/munch/camera/PlaceholderTrim.smali" "$W/smali4/com/munch/camera/"
python3 - "$W/smali4" <<'PY4'
import sys
root = sys.argv[1]
call = "    invoke-static {%s}, Lcom/munch/camera/PlaceholderTrim;->trim(Ljava/lang/String;)V\n\n"
def hook(r):  # this.k (di.s) -> .k (di.C storage data) -> .g (savePath) -> trim; r is overwritten before its next use
    return ("    iget-object %s, p0, LUp/b;->k:Ldi/s;\n\n    iget-object %s, %s, Ldi/s;->k:Ldi/C;\n\n    if-eqz %s, :munch_trim_skip\n\n"
            "    iget-object %s, %s, Ldi/C;->g:Ljava/lang/String;\n\n" % (r, r, r, r, r, r)) + call % r + "    :munch_trim_skip\n\n"
for cls, a, b in (("Up/b", "v0", "v1"), ("Up/f", "v1", "v0")):
    p = "%s/%s.smali" % (root, cls); s = open(p).read()
    anchor = "    iget-boolean %s, %s, Ldi/A;->q:Z\n\n    if-ne %s, %s, :cond_22\n\n" % (a, a, a, b)
    if "PlaceholderTrim" in s:
        print(cls + ": placeholder trim already patched"); continue
    assert s.count(anchor) == 1 and "task is abandoned" in s[s.index(anchor):s.index(anchor) + 400], "unexpected %s.A0" % cls
    s = s.replace(anchor, anchor + hook(a)); open(p, "w").write(s)
p = root + "/Xp/m$b.smali"; s = open(p).read()
anchor = "    iget-object v0, v0, Ldi/C;->g:Ljava/lang/String;\n\n    const-string v2, \"onParallelDataAbandoned: should remove record \""
if "PlaceholderTrim" in s:
    print("Xp.m$b: placeholder trim already patched")
else:
    assert s.count(anchor) == 1, "unexpected Xp.m$b.a"
    head = "    iget-object v0, v0, Ldi/C;->g:Ljava/lang/String;\n\n"
    s = s.replace(anchor, head + call % "v0" + anchor[len(head):]); open(p, "w").write(s)
PY4
java -cp "$JAR:$W/cls" Smali a "$W/smali4" "$W/stage/$DEX4" 23
# Ultra-wide photos: "Ultra-wide distortion correction" (pref_camera_ultra_wide_ldc_key, default on) runs the capture LDC
# through libwa_widelens_undistort -> libanc_dc_base, the same GPU engine that crashes back Portrait on this port; the app
# dies (SIGSEGV) and the photo stays a 16 MiB preview placeholder. Default the setting to off (z.J0() and the settings
# checkbox); with it off ultra-wide photos save normally at 3264x2448. A user can still switch it on.
DEX5=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Lcom/android/camera/data/data/z;'" && basename "$d" && break; done)
for x in "$DEX" "$DEX2" "$DEX3" "$DEX4"; do [ -n "$DEX5" ] && [ "$DEX5" != "$x" ] || { echo "data.z not found in a separate dex"; exit 1; }; done
java -cp "$JAR:$W/cls" Smali d "$W/$DEX5" "$W/smali5"
python3 - "$W/smali5/com/android/camera" <<'PY5'
import sys
root = sys.argv[1]
for f, reg in (("data/data/z.smali", ("v1", "v2")), ("fragment/settings/CameraCapturePreferenceFragment.smali", ("v4", "v5"))):
    p = root + "/" + f; s = open(p).read()
    old = '    const-string %s, "pref_camera_ultra_wide_ldc_key"\n\n    const/4 %s, 0x1' % reg
    new = old[:-1] + "0"
    if s.count(new) == 1:
        print(f.split("/")[-1] + ": ultra-wide LDC default already off")
        continue
    assert s.count(old) == 1, "unexpected ultra-wide LDC default in " + f
    s = s.replace(old, new); open(p, "w").write(s)
PY5
java -cp "$JAR:$W/cls" Smali a "$W/smali5" "$W/stage/$DEX5" 23
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX" "$DEX2" "$DEX3" "$DEX4" "$DEX5")   # stored, like the original
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "patched $DEX $DEX2 $DEX3 $DEX4 $DEX5 -> $OUT"
