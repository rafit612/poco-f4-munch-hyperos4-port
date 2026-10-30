#!/bin/bash
# Long videos were lost: the camera caps one recording file at 3,670,016,000 bytes (VideoUtil.getRecorderMaxFileSize, device flag J3() is true on the Marble
# profile). On this port a recording that passes the cap is not split: the app calls it invalid and DELETES it (seen 2026-10-31: 6 min of 4K60 at 100 Mbit/s,
# file 4.79 GB, "delete invalid video ... .pending-..."; the v9 bitrate doubling made it happen after ~4.7 min instead of ~9 min).
# Fix: raise the cap constant to 64 GB, so the recorder limit becomes the free storage (minus 200 MB), as on devices without the flag. MPEG4Writer wrote the
# 4.79 GB file correctly, so there is no 4 GB container problem.
# usage: video_maxsize.sh <in.apk> <out.apk>
set -e
IN=${1:?in.apk}; OUT=${2:?out.apk}
JAR=${JAR:-$HOME/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar}
BT=${BT:-$HOME/Android/Sdk/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
D="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
javac -d "$W/cls" -cp "$JAR" "$D/Smali.java"
unzip -q -o "$IN" 'classes*.dex' -d "$W"
DEX=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Lcom/android/camera/module/video/H;'" && basename "$d" && break; done)
[ -n "$DEX" ] || { echo "video/H not found"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX" "$W/smali"
python3 - "$W/smali/com/android/camera/module/video/H.smali" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
a = s.index(".method public static j(J)J"); b = s.index(".end method", a)
body = s[a:b]
if "0x1000000000L" in body:
    print("cap already raised"); sys.exit(0)
assert body.count("const-wide v6, 0xdac00000L") == 1, "cap constant not unique"
body = body.replace("const-wide v6, 0xdac00000L", "const-wide v6, 0x1000000000L")
open(p, "w").write(s[:a] + body + s[b:]); print("max single file size: 3.5 GB -> 64 GB")
PY
mkdir -p "$W/stage"; java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX")
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "video cap patch -> $OUT"
rm -rf "$W"
