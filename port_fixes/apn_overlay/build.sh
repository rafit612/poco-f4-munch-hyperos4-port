#!/bin/bash
# Builds build/MunchApnOverlay.apk (static RRO for com.android.providers.telephony).
set -e
export PATH="/opt/android-studio/jbr/bin:$PATH"
D="$(cd "$(dirname "$0")" && pwd)"; BT=~/Android/Sdk/build-tools/37.0.0; JAR=~/Android/Sdk/platforms/android-37.0/android.jar
cd "$D/build"
"$BT/aapt2" compile --dir "$D/res" -o res.zip
"$BT/aapt2" link -o unsigned.apk -I "$JAR" --manifest "$D/AndroidManifest.xml" res.zip
"$BT/zipalign" -f -p 4 unsigned.apk aligned.apk
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out MunchApnOverlay.apk aligned.apk
"$BT/apksigner" verify MunchApnOverlay.apk && sha256sum MunchApnOverlay.apk
