#!/bin/bash
# Patch the camera app's watermark device name: the port's MiuiCamera 6.7 loads a fixed "Marble" device profile whose
# watermark table (com.mi.device.Marble.d()) is {"XIAOMI", "17 PRO"}; this sets it to {"POCO", "F4 5G"}.
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
assert body.count('"XIAOMI"') == 2 and body.count('"17 PRO"') == 2, "unexpected Marble.d() body"
body = body.replace('"XIAOMI"', '"POCO"').replace('"17 PRO"', '"F4 5G"')
open(p, "w").write(s[:start] + body + s[end:])
PY
mkdir -p "$W/stage"
java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23     # dex 035, like the original
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX")   # stored, like the original
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "patched $DEX -> $OUT"
