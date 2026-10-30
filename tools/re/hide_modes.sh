#!/bin/bash
# Hides camera modes that crash on this phone: sets ModuleEntry.support() to false (the opposite of hidden_modes_test.sh).
# Mimoji (Sticker avatars, Mimoji video): NPE in the mode screen because the prop camera.support.mimoji.version is unset on munch.
# Clone, Movie effects: SNPE/Hexagon SIGSEGV in libfenshen_snpe (movielens module). Found in the 2026-10-30 owner test (docs/camera/OWNER_TESTS_2026-10-30.md).
# usage: hide_modes.sh <in.apk> <out.apk> [full/class/path/Entry ...]   (default: the four entries above)
set -e
IN=${1:?in.apk}; OUT=${2:?out.apk}; shift 2
[ $# -gt 0 ] || set -- com/xiaomi/mimoji/common/module/MimojiModuleEntry com/xiaomi/mimoji/common/module/MimojiVideoModuleEntry \
  com/android/camera/features/mode/more/clone/MoreCloneModuleEntry com/android/camera/features/mode/more/film/MoreFilmModuleEntry
JAR=${JAR:-$HOME/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar}
BT=${BT:-$HOME/Android/Sdk/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
D="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
javac -d "$W/cls" -cp "$JAR" "$D/Smali.java"
unzip -q -o "$IN" 'classes*.dex' -d "$W"
cp "$IN" "$W/work.apk"; mkdir -p "$W/stage"
for e in "$@"; do
  DEX=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'L$e;'" && basename "$d" && break; done)
  [ -n "$DEX" ] || { echo "entry $e not found"; exit 1; }
  if [ ! -d "$W/smali_$DEX" ]; then java -cp "$JAR:$W/cls" Smali d "$W/$DEX" "$W/smali_$DEX"; fi
  python3 - "$W/smali_$DEX/$e.smali" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
m = re.search(r"(\.method public support\(\)Z\s+\.registers \d+\s+const/4 v0, )(0x[01])(\s+return v0)", s)
assert m, "unexpected support() body in " + p
if m.group(2) == "0x0":
    print(p.split("/")[-1], "already off")
else:
    open(p, "w").write(s[:m.start(2)] + "0x0" + s[m.end(2):]); print(p.split("/")[-1], "support() -> false")
PY
done
for sd in "$W"/smali_*; do DEX=${sd##*smali_}; java -cp "$JAR:$W/cls" Smali a "$sd" "$W/stage/$DEX" 23; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX"); done
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "modes hidden -> $OUT"
rm -rf "$W"
