#!/bin/bash
# Builds the PhotoStage speed-test APK with plain SDK tools + OpenCV Android (Apache 2.0; fetched by the caller into $OCV, not stored in the repo).
# usage: OCV=~/camera_builds/ocv build.sh <out.apk>
set -e
D="$(cd "$(dirname "$0")" && pwd)"; OUT=${1:?out.apk}; OCV=${OCV:-$HOME/camera_builds/ocv}
SDK=${SDK:-$HOME/Android/Sdk}; BT=${BT:-$SDK/build-tools/37.0.0}; export PATH=/opt/android-studio/jbr/bin:$PATH
AJ=$(ls -d "$SDK"/platforms/android-3[0-9]*/android.jar | sort -V | tail -1)
W=$(mktemp -d)
cat > "$W/AndroidManifest.xml" <<'XML'
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.munch.photostage">
  <application android:label="PhotoStage" android:debuggable="true" android:largeHeap="true" android:extractNativeLibs="true">
    <activity android:name=".StageTest" android:exported="true">
      <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
    </activity>
  </application>
</manifest>
XML
mkdir -p "$W/cls" "$W/dex" "$W/lib/arm64-v8a"
javac --release 8 -nowarn -cp "$AJ:$OCV/classes.jar" -d "$W/cls" "$D"/*.java 2>&1 | grep -v "^Note:" || true
"$BT/d8" --min-api 29 --lib "$AJ" --output "$W/dex" $(find "$W/cls" -name '*.class') "$OCV/classes.jar"
"$BT/aapt2" link -o "$W/base.apk" -I "$AJ" --manifest "$W/AndroidManifest.xml" --min-sdk-version 29 --target-sdk-version 34
cp "$OCV/jni/arm64-v8a/libopencv_java4.so" "$OCV/jni/arm64-v8a/libc++_shared.so" "$W/lib/arm64-v8a/"
(cd "$W/dex" && zip -q "$W/base.apk" classes*.dex); (cd "$W" && zip -q -0 -r base.apk lib)
"$BT/zipalign" -f -p 4 "$W/base.apk" "$W/aligned.apk"
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out "$OUT" "$W/aligned.apk"
rm -rf "$W"; ls -l "$OUT" | awk '{print $5, $9}'
