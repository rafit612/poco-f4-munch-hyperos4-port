#!/bin/bash
# Builds the NrProbe test APK with plain SDK tools (no Gradle): javac -> d8 -> aapt2 -> zipalign -> apksigner (debug key).
# usage: build.sh <out.apk>
set -e
D="$(cd "$(dirname "$0")" && pwd)"; OUT=${1:?out.apk}
SDK=${SDK:-$HOME/Android/Sdk}; BT=${BT:-$SDK/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
AJ=$(ls -d "$SDK"/platforms/android-3[0-9]*/android.jar | sort -V | tail -1)
W=$(mktemp -d)
cat > "$W/AndroidManifest.xml" <<'XML'
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.munch.nrprobe">
  <uses-permission android:name="android.permission.CAMERA"/>
  <application android:label="NrProbe" android:debuggable="true">
    <activity android:name=".NrProbe" android:exported="true">
      <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
    </activity>
  </application>
</manifest>
XML
mkdir -p "$W/cls" "$W/dex"
javac --release 8 -nowarn -cp "$AJ" -d "$W/cls" "$D/NrProbe.java" 2>&1 | grep -v "^Note:" || true
"$BT/d8" --min-api 29 --lib "$AJ" --output "$W/dex" $(find "$W/cls" -name '*.class')
"$BT/aapt2" link -o "$W/base.apk" -I "$AJ" --manifest "$W/AndroidManifest.xml" --min-sdk-version 29 --target-sdk-version 34
(cd "$W/dex" && zip -q "$W/base.apk" classes.dex)
"$BT/zipalign" -f -p 4 "$W/base.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
rm -rf "$W"; ls -l "$OUT" | awk '{print $5, $9}'
