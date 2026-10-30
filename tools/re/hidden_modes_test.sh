#!/bin/bash
# C5 test builds: switch on hidden camera modes (their ModuleEntry.support() returns a hard-coded false) on top of a
# patched MiuiCamera build. Test only - one APK, installed through the munch_cam_watermark module like other builds.
# usage: hidden_modes_test.sh <in.apk (e.g. MiuiCamera_v11.apk)> <out.apk> <entry> [entry ...]
#   entries are paths below com/android/camera/features/mode/, e.g. night/video/NightVideoModuleEntry moon/MoonModuleEntry
set -e
IN=${1:?in.apk}; OUT=${2:?out.apk}; shift 2; [ $# -gt 0 ] || { echo "no entries given"; exit 1; }
JAR=${JAR:-$HOME/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar}
BT=${BT:-$HOME/Android/Sdk/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
D="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
javac -d "$W/cls" -cp "$JAR" "$D/Smali.java"
unzip -q -o "$IN" 'classes*.dex' -d "$W"
DEX=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Lcom/android/camera/features/mode/$1;'" && basename "$d" && break; done)
[ -n "$DEX" ] || { echo "entry $1 not found"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX" "$W/smali"
for e in "$@"; do
  python3 - "$W/smali/com/android/camera/features/mode/$e.smali" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
m = re.search(r"(\.method public support\(\)Z\s+\.registers \d+\s+const/4 v0, )(0x[01])(\s+return v0)", s)
assert m, "unexpected support() body in " + p
if m.group(2) == "0x1":
    print(p.split("/")[-1], "already on")
else:
    s = s[:m.start(2)] + "0x1" + s[m.end(2):]
    open(p, "w").write(s)
    print(p.split("/")[-1], "support() -> true")
PY
done
mkdir -p "$W/stage"; java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX")
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "patched $DEX -> $OUT"
rm -rf "$W"
