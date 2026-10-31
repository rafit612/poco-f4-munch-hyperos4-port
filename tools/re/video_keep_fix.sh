#!/bin/bash
# Long native recordings were sometimes deleted: the save step (n7.Q.a) reads duration 0 and the app calls the file invalid (docs/camera/OWNER_TESTS_2026-10-30.md).
# Adds com.munch.camera.VideoDur in a new dex and calls it after both duration reads, so a file with data keeps its real length (from the MP4 mvhd box).
# usage: video_keep_fix.sh <in.apk> <out.apk>
set -e
IN=${1:?in.apk}; OUT=${2:?out.apk}
JAR=${JAR:-$HOME/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar}
SDK=${SDK:-$HOME/Android/Sdk}; BT=${BT:-$SDK/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
AJ=$(ls -d "$SDK"/platform-tools/../platforms/android-3[0-9]*/android.jar | sort -V | tail -1)
D="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
javac -d "$W/cls" -cp "$JAR" "$D/Smali.java"
unzip -q -o "$IN" 'classes*.dex' -d "$W"
DEX=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'Ln7/Q;'" && basename "$d" && break; done)
[ -n "$DEX" ] || { echo "n7/Q not found"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX" "$W/smali"
python3 - "$W/smali/n7/Q.smali" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = '''    :cond_22c
    new-instance v0, Ljava/lang/StringBuilder;

    const-string/jumbo v8, "save video: mVideoSaveCallback -> "
'''
new = '''    :cond_22c
    invoke-static {v9, v10, v11}, Lcom/munch/camera/VideoDur;->fix(Ljava/lang/String;J)J

    move-result-wide v10

    new-instance v0, Ljava/lang/StringBuilder;

    const-string/jumbo v8, "save video: mVideoSaveCallback -> "
'''
assert s.count(old) == 1, "hook point not unique"
open(p, "w").write(s.replace(old, new)); print("save step: duration fix hooked")
PY
mkdir -p "$W/stage" "$W/new/cls" "$W/new/dex"; java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23
javac --release 8 -nowarn -cp "$AJ" -d "$W/new/cls" "$D/VideoDur.java" 2>&1 | grep -v '^Note:\|^warning' || true
"$BT/d8" --min-api 29 --lib "$AJ" --output "$W/new/dex" $(find "$W/new/cls" -name '*.class')
N=$(ls "$W"/classes*.dex | sed -E 's/.*classes([0-9]*)\.dex/\1/' | sort -n | tail -1); NEXT="classes$((N + 1)).dex"
cp "$W/new/dex/classes.dex" "$W/stage/$NEXT"
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX" "$NEXT")
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "video keep fix ($DEX + $NEXT) -> $OUT"
rm -rf "$W"
