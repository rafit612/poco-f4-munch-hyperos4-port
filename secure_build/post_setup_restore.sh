#!/bin/bash
# After the fresh setup (Settings > Developer options > USB debugging ON), restore what lives in
# user data and is not part of the images: GCam (LMC 8.4) with the POCO F4 config, display settings.
set -u
B="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch"
ADB=/home/odoo-dbsl/Android/Sdk/platform-tools/adb
"$ADB" wait-for-device
echo "GCam LMC 8.4: install"
"$ADB" install -r "$B/gcam_download/LMC8.4_R16_Snapcam.apk"
echo "GCam config: copy POCO-F4-FINAL.xml (load it in GCam: double-tap the black area next to the shutter)"
"$ADB" shell mkdir -p /sdcard/LMC8.4
"$ADB" push "$B/gcam_download/POCO-F4-FINAL.xml" /sdcard/LMC8.4/
echo "Display: 60 Hz (clone panel), colour mode as before, auto-brightness on"
"$ADB" shell settings put system peak_refresh_rate 60.0
"$ADB" shell settings put system min_refresh_rate 60.0
"$ADB" shell settings put secure user_refresh_rate 60
"$ADB" shell settings put system display_color_mode 258
"$ADB" shell settings put system screen_brightness_mode 1
echo "Done. Play Store apps come back from your Google account; Google Photos backs up your photos."
