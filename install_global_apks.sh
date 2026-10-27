#!/bin/bash
# Verify and install Global Xiaomi APKs dropped into ./global_apks
# Rules:
#  - Core system apps on the blocklist are never replaced.
#  - Updating an installed app: Android itself rejects a different signing key.
#    We also refuse downgrades.
#  - Installing a new package: its v1 cert must match Xiaomi's official key.
# Accepts .apk, or .apkm / .xapk / .apks bundles (installed as split APKs).

ROOT="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch"
IN="$ROOT/global_apks"
WORK="$ROOT/global_apks_work"
LOG="$ROOT/global_install.log"
ADB=/home/odoo-dbsl/android-tools/platform-tools/adb
AAPT=/home/odoo-dbsl/Android/Sdk/build-tools/37.0.0/aapt2

# Xiaomi MIUI platform key, verified against independent public reports
XIAOMI_KEYS="C9:00:9D:01:EB:F9:F5:D0:30:2B:C7:1B:2F:E9:AA:9A:47:A4:32:BB:A1:73:08:A3:11:1B:75:D7:B2:14:90:25"

BLOCK="com.miui.securitycenter com.miui.home com.android.camera com.xiaomi.misettings com.miui.packageinstaller com.xiaomi.phone com.android.phone com.miui.system com.miui.core com.miui.rom com.lbe.security.miui com.miui.guardprovider com.miui.securitycore com.miui.powerkeeper com.android.systemui com.android.settings"

mkdir -p "$IN" "$WORK"
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

cert_of() {  # v1 signing cert SHA-256 of an APK, or "none"
    local r
    r=$(unzip -l "$1" 2>/dev/null | grep -oE "META-INF/[^ ]+\.(RSA|DSA|EC)$" | head -1)
    [ -z "$r" ] && { echo none; return; }
    unzip -p "$1" "$r" | openssl pkcs7 -inform DER -print_certs 2>/dev/null \
        | openssl x509 -noout -fingerprint -sha256 2>/dev/null | sed 's/.*=//'
}

shopt -s nullglob nocaseglob
files=("$IN"/*.apk "$IN"/*.apkm "$IN"/*.xapk "$IN"/*.apks)
[ ${#files[@]} -eq 0 ] && { say "No APKs in $IN"; exit 0; }

for f in "${files[@]}"; do
    name=$(basename "$f")
    rm -rf "$WORK"/*
    case "${name,,}" in
        *.apk) splits=("$f"); base="$f" ;;
        *)     unzip -qo "$f" '*.apk' -d "$WORK" 2>/dev/null
               splits=("$WORK"/*.apk)
               base="$WORK/base.apk"; [ -f "$base" ] || base=$(ls -S "$WORK"/*.apk 2>/dev/null | head -1) ;;
    esac
    if [ -z "$base" ] || [ ! -f "$base" ]; then say "SKIP     $name: no APK inside"; continue; fi

    badge=$("$AAPT" dump badging "$base" 2>/dev/null | head -1)
    pkg=$(sed -n "s/.*name='\([^']*\)'.*/\1/p" <<<"$badge")
    vcode=$(sed -n "s/.*versionCode='\([0-9]*\)'.*/\1/p" <<<"$badge")
    vname=$(sed -n "s/.*versionName='\([^']*\)'.*/\1/p" <<<"$badge")
    [ -z "$pkg" ] && { say "SKIP     $name: unreadable APK"; continue; }
    cert=$(cert_of "$base")

    if [[ " $BLOCK " == *" $pkg "* ]]; then say "BLOCKED  $pkg $vname: core system app, not replaced"; continue; fi

    cur=$("$ADB" shell dumpsys package "$pkg" 2>/dev/null | tr -d '\r' | grep -m1 -oE "versionCode=[0-9]+" | cut -d= -f2)
    if [ -n "$cur" ]; then
        if [ -n "$vcode" ] && [ "$vcode" -le "$cur" ]; then
            say "SKIP     $pkg $vname: not newer than installed (have $cur, file $vcode)"; continue
        fi
        mode="update"
    else
        if [[ " $XIAOMI_KEYS " != *" $cert "* ]]; then
            say "REJECT   $pkg $vname: new app, signing key not Xiaomi's (cert: $cert)"; continue
        fi
        mode="new"
    fi

    say "INSTALL  $pkg $vname ($mode, ${#splits[@]} apk file(s), cert ${cert:0:11}...)"
    if [ ${#splits[@]} -gt 1 ]; then out=$("$ADB" install-multiple -r "${splits[@]}" 2>&1)
    else out=$("$ADB" install -r "${splits[0]}" 2>&1); fi
    if grep -q Success <<<"$out"; then say "OK       $pkg"
    else say "FAILED   $pkg: $(tail -1 <<<"$out")"; fi
done
rm -rf "$WORK"
say "DONE"
