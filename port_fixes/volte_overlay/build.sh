#!/bin/bash
# Builds build/MunchVolteOverlay.apk (static RRO for com.android.carrierconfig) from global_inputs/.
set -e
export PATH="/opt/android-studio/jbr/bin:$PATH"
D="$(cd "$(dirname "$0")" && pwd)"; BT=~/Android/Sdk/build-tools/37.0.0; JAR=~/Android/Sdk/platforms/android-37.0/android.jar
python3 -I "$D/make_vendor_xml.py" "$D/global_inputs/CarrierConfigResCommon_Sys_global_vendor.xml" \
    "$D/global_inputs/globalization.xml" "$D/global_inputs/pudding_vendor_device.xml" "$D/res/xml/vendor.xml"
python3 -I -c "import sys,xml.dom.minidom; xml.dom.minidom.parse(sys.argv[1])" "$D/res/xml/vendor.xml"
cd "$D/build"
"$BT/aapt2" compile --dir "$D/res" -o res.zip
"$BT/aapt2" link -o unsigned.apk --keep-raw-values -I "$JAR" --manifest "$D/AndroidManifest.xml" res.zip
"$BT/zipalign" -f -p 4 unsigned.apk aligned.apk
"$BT/apksigner" sign --ks ~/.android/debug.keystore --ks-pass pass:android --out MunchVolteOverlay.apk aligned.apk
"$BT/apksigner" verify MunchVolteOverlay.apk && sha256sum MunchVolteOverlay.apk
