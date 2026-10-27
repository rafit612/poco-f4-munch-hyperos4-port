#!/bin/bash
# Patch the camera app's watermark device name: the port's MiuiCamera 6.7 loads a fixed "Marble" device profile whose
# watermark table (com.mi.device.Marble.d()) is {"XIAOMI", "17 PRO"}; this sets it to {"POCO", "F4 5G"}.
# It also sets the profile's filter set (Marble.E1(), {17} = no Leica looks) to {25} = LC_CUSTOM_BACK: Leica Vivid,
# Natural, Chrome, Classic, Contemporary, Eternal, Brass, Teal, IModelA. Photo filters are LUTs inside the app.
# Portrait: Marble.C() (largest bokeh picture width) 4000 -> 4625 like the official app's Munch_pro profile, so the
# depth stream uses the OV64B40's native 4624x3472 instead of a forced 4000x3000.
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
open(p, "w").write(s)
PY
mkdir -p "$W/stage"
java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23     # dex 035, like the original
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX")   # stored, like the original
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "patched $DEX -> $OUT"
