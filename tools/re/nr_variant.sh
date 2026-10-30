#!/bin/bash
# Experiment build: the native camera asks the HAL for lighter noise reduction / edge mode on STILL_CAPTURE requests.
# The app never sets android.noiseReduction.mode / android.edge.mode itself, so the HAL default (high quality NR, which smears detail at
# ISO > 400) applies. Eh.c.a() is the app's single request factory (session ordinal 1 = TEMPLATE_STILL_CAPTURE); the new helper
# com.munch.camera.NrPatch.apply() sets the two modes after the app's stored settings, so they win.
# usage: nr_variant.sh <in.apk (v13)> <out.apk> <nr mode> <edge mode>      modes: NR 0 off 1 fast 2 high quality 3 minimal 4 zsl; edge 0 off 1 fast 2 hq 3 zsl
set -e
IN=${1:?in.apk}; OUT=${2:?out.apk}; NR=${3:?nr mode}; EDGE=${4:?edge mode}; ONLY=${5:-1}   # ONLY = camera2 template to change (1 = ordinal 1 = STILL_CAPTURE; "all" = every request, for probing)
COND="    const/4 v0, 0x$ONLY\n\n    if-ne p1, v0, :cond_end\n"; [ "$ONLY" = all ] && COND=""
JAR=${JAR:-$HOME/re_tools/jadx/jadx-headless-mcp-0.7.1-all.jar}
BT=${BT:-$HOME/Android/Sdk/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
D="$(cd "$(dirname "$0")" && pwd)"; W=$(mktemp -d)
javac -d "$W/cls" -cp "$JAR" "$D/Smali.java"
unzip -q -o "$IN" 'classes*.dex' -d "$W"
DEX=$(for d in "$W"/classes*.dex; do "$BT/dexdump" -f "$d" 2>/dev/null | grep -q "Class descriptor  : 'LEh/c;'" && basename "$d" && break; done)
[ -n "$DEX" ] || { echo "Eh/c not found"; exit 1; }
java -cp "$JAR:$W/cls" Smali d "$W/$DEX" "$W/smali"
mkdir -p "$W/smali/com/munch/camera"
cat > "$W/smali/com/munch/camera/NrPatch.smali" <<EOF
.class public Lcom/munch/camera/NrPatch;
.super Ljava/lang/Object;

.method public static apply(Landroid/hardware/camera2/CaptureRequest\$Builder;I)V
    .registers 5

$(printf "$COND")
    sget-object v0, Landroid/hardware/camera2/CaptureRequest;->NOISE_REDUCTION_MODE:Landroid/hardware/camera2/CaptureRequest\$Key;

    const/4 v1, 0x$NR

    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v1

    invoke-virtual {p0, v0, v1}, Landroid/hardware/camera2/CaptureRequest\$Builder;->set(Landroid/hardware/camera2/CaptureRequest\$Key;Ljava/lang/Object;)V

    sget-object v0, Landroid/hardware/camera2/CaptureRequest;->EDGE_MODE:Landroid/hardware/camera2/CaptureRequest\$Key;

    const/4 v1, 0x$EDGE

    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v1

    invoke-virtual {p0, v0, v1}, Landroid/hardware/camera2/CaptureRequest\$Builder;->set(Landroid/hardware/camera2/CaptureRequest\$Key;Ljava/lang/Object;)V

    :cond_end
    return-void
.end method
EOF
python3 - "$W/smali/Eh/c.smali" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
start = s.index(".method public final a(LEh/d;Ln9/O1;)Landroid/hardware/camera2/CaptureRequest$Builder;")
end = s.index(".end method", start)
b = s[start:end]
if "NrPatch" in b:
    print("NR hook: already present"); sys.exit(0)
assert b.count("    .registers 5\n") == 1, "unexpected register count"
b = b.replace("    .registers 5\n", "    .registers 6\n")
old = "    move-result p1\n"
assert b.count(old) == 1, "ordinal move-result not unique"
b = b.replace(old, old + "\n    move v2, p1\n")
ret = "    monitor-exit p2\n"
i = b.index(ret) + len(ret)
j = b.index("    return-object p0\n", i)
b = b[:j] + "    invoke-static {p0, v2}, Lcom/munch/camera/NrPatch;->apply(Landroid/hardware/camera2/CaptureRequest$Builder;I)V\n\n" + b[j:]
open(p, "w").write(s[:start] + b + s[end:])
print("NR hook added to Eh.c.a()")
PY
mkdir -p "$W/stage"; java -cp "$JAR:$W/cls" Smali a "$W/smali" "$W/stage/$DEX" 23
cp "$IN" "$W/work.apk"; (cd "$W/stage" && zip -q -0 "$W/work.apk" "$DEX")
"$BT/zipalign" -f -p 4 "$W/work.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
"$BT/apksigner" verify "$OUT" && echo "NR variant nr=$NR edge=$EDGE ($DEX) -> $OUT"
rm -rf "$W"
