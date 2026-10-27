#!/bin/bash
# Install the vetted Global/newer Xiaomi APKs one by one, launch each,
# check the crash log, and roll back any app that crashes.
DL=/home/odoo-dbsl/Downloads
ADB=/home/odoo-dbsl/android-tools/platform-tools/adb
LOG="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch/global_install.log"
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

# pkg|file   (low risk first; contacts and messages last)
LIST=(
"com.miui.notes|com.miui.notes_3.2.7.9-3279_minAPI29(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.compass|com.miui.compass_17.1.4.1-1701041_minAPI26(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.weather2|com.miui.weather2_17.1.0.26-R-17010026_minAPI24(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.android.soundrecorder|com.android.soundrecorder_8.1.6-056aff0d5-801060_minAPI33(arm64-v8a,armeabi-v7a)(nodpi)_apkmirror.com.apk"
"com.miui.screenrecorder|com.miui.screenrecorder_4.16.2.9.1-41602091_minAPI29(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.screenshot|com.miui.screenshot_RELEASE-1.6.3.40-09141112-10603040_minAPI34(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.personalassistant|com.miui.personalassistant_25.41.82.00-09162057-2541820_minAPI29(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.hyper.gallery.plugin|com.hyper.gallery.plugin_5.4.2.8-5040208_minAPI34(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.cloudbackup|com.miui.cloudbackup_1.12.1.6.52.2-2120106522_minAPI24(nodpi)_apkmirror.com.apk"
"com.miui.hybrid|com.miui.hybrid_1.31.9.0-13190002_minAPI28(arm64-v8a,armeabi-v7a)(nodpi)_apkmirror.com.apk"
"com.xiaomi.account|com.xiaomi.account_R-26.09.14.00-326091400_minAPI28(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.xiaomi.mi_connect_service|com.xiaomi.mi_connect_service_6.0.456.10-60004561_minAPI28(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.misound|com.miui.misound_16-4.0-4-20260903-260903_minAPI33(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.xiaomi.joyose|com.xiaomi.joyose_2.5.22-522_minAPI24(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.xiaomi.mipicks|com.xiaomi.mipicks_602-16.6.1.0-6021661_minAPI24(arm64-v8a,armeabi-v7a)(nodpi)_apkmirror.com.apk"
"com.xiaomi.calendar|com.xiaomi.calendar_G-18.0.7-180007000_minAPI26(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.mishare.connectivity|com.miui.mishare.connectivity_5.4.1.global_20260914_1648-50401_minAPI26(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.android.contacts|com.android.contacts_18.31.00.55-310055_minAPI23(nodpi)_apkmirror.com.apk"
"com.android.mms|com.android.mms_18.0.0.42-gl-180000042_minAPI29(arm64-v8a)(nodpi)_apkmirror.com.apk"
)

sh() { "$ADB" shell "$@" 2>&1 | tr -d '\r'; }

for e in "${LIST[@]}"; do
    pkg=${e%%|*}; file="$DL/${e#*|}"
    [ -f "$file" ] || { say "MISSING  $pkg"; continue; }
    was_installed=$(sh pm path "$pkg" | grep -c package:)
    out=$("$ADB" install -r "$file" 2>&1 | tr -d '\r')
    if ! grep -q Success <<<"$out"; then say "FAILED   $pkg: $(tail -1 <<<"$out")"; continue; fi
    ver=$(sh dumpsys package "$pkg" | grep -m1 -oE "versionName=[^ ]+" | cut -d= -f2)

    # Launch it (if it has a launcher icon) and watch the crash log for 6 seconds.
    sh logcat -b crash -c >/dev/null
    act=$(sh cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER "$pkg" | tail -1)
    if [[ "$act" == */* ]]; then sh am start -W -n "$act" >/dev/null; launched="launched"; else launched="no icon (service)"; fi
    sleep 6
    crash=$(sh logcat -b crash -d | grep -E "FATAL EXCEPTION|Process: $pkg" | grep -c "$pkg")
    sh am force-stop "$pkg" >/dev/null 2>&1
    if [ "$crash" -gt 0 ]; then
        say "CRASHED  $pkg $ver ($launched): rolling back"
        sh logcat -b crash -d | grep -A3 "Process: $pkg" | head -4 | sed 's/^/           /' | tee -a "$LOG"
        if [ "$was_installed" -gt 0 ]; then sh pm uninstall-system-updates "$pkg" | sed 's/^/           /' | tee -a "$LOG"
        else sh pm uninstall "$pkg" | sed 's/^/           /' | tee -a "$LOG"; fi
    else
        say "OK       $pkg $ver ($launched, no crash)"
    fi
done
say "DONE"
