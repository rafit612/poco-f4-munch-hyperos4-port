#!/bin/bash
# Update core Xiaomi system apps one at a time, least critical first.
# After each: check the crash log; roll back that app on any crash.
# At the end: reboot and confirm the phone boots and none of them crash.
DL=/home/odoo-dbsl/Downloads
ADB=/home/odoo-dbsl/android-tools/platform-tools/adb
LOG="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch/global_install.log"
W="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch/apk_analysis_work"
say() { echo "$*" | tee -a "$LOG"; }
sh() { "$ADB" shell "$@" 2>&1 | tr -d '\r'; }

LIST=(
"com.miui.guardprovider|com.miui.guardprovider_3.1.4-20260902.0-330_minAPI33(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.securitycore|com.miui.securitycore_4.4.4.1-4-260902-40004441_minAPI30(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.xiaomi.xmsf|com.xiaomi.xmsf_7.5.69-C-70005069_1arch_1dpi_13feat_b2347864e4ae005c94785e753c34f9e3_apkmirror.com.apkm"
"com.xiaomi.misettings|com.xiaomi.misettings_16.4.260908.00-260908400_minAPI24(arm64-v8a)(nodpi)_apkmirror.com.apk"
"com.miui.securitycenter|com.miui.securitycenter_13.6.6-260928.0.1-40001366_minAPI26(arm64-v8a)(nodpi)_apkmirror.com.apk"
)
DONE_PKGS=()

for e in "${LIST[@]}"; do
    pkg=${e%%|*}; file="$DL/${e#*|}"
    [ -f "$file" ] || { say "MISSING  $pkg"; continue; }
    sh logcat -b crash -c >/dev/null
    case "$file" in
        *.apkm) rm -rf "$W"; mkdir -p "$W"; unzip -qo "$file" '*.apk' -d "$W"
                out=$("$ADB" install-multiple -r "$W"/*.apk 2>&1 | tr -d '\r'); rm -rf "$W" ;;
        *)      out=$("$ADB" install -r "$file" 2>&1 | tr -d '\r') ;;
    esac
    if ! grep -q Success <<<"$out"; then say "FAILED   $pkg: $(tail -1 <<<"$out")"; continue; fi
    ver=$(sh dumpsys package "$pkg" | grep -m1 -oE "versionName=[^ ]+" | cut -d= -f2)
    sleep 10   # these are services; give them time to restart
    crash=$(sh logcat -b crash -d | grep -c "Process: $pkg")
    if [ "$crash" -gt 0 ]; then
        say "CRASHED  $pkg $ver: rolling back"
        sh logcat -b crash -d | grep -A3 "Process: $pkg" | head -4 | sed 's/^/           /' | tee -a "$LOG"
        sh pm uninstall-system-updates "$pkg" | sed 's/^/           /' | tee -a "$LOG"
    else
        say "OK       $pkg $ver (no crash)"; DONE_PKGS+=("$pkg")
    fi
done

[ ${#DONE_PKGS[@]} -eq 0 ] && { say "DONE (nothing updated, no reboot needed)"; exit 0; }

say "REBOOT   testing that the phone boots with the updates"
sh logcat -b crash -c >/dev/null
"$ADB" reboot
sleep 20
for i in $(seq 1 60); do
    [ "$(sh getprop sys.boot_completed 2>/dev/null)" = "1" ] && break; sleep 5
done
if [ "$(sh getprop sys.boot_completed)" != "1" ]; then
    say "BOOT     NOT COMPLETED after 5 min: check the phone screen"; exit 1
fi
sleep 30   # let services settle after boot
say "BOOT     completed"
for pkg in "${DONE_PKGS[@]}"; do
    c=$(sh logcat -b crash -d | grep -c "Process: $pkg")
    if [ "$c" -gt 0 ]; then say "CRASHED  $pkg after reboot ($c crash(es))"; else say "OK       $pkg after reboot"; fi
done
say "DONE"
