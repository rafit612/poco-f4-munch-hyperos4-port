#!/bin/bash
# POCO F4 5G (munch) — HyperOS 4 / Android 17 unofficial port: install script (Linux / macOS).
#   bash flash_linux.sh          clean install: firmware + kernel + system, ERASES ALL DATA (first install)
#   bash flash_linux.sh update   update an existing install of this ROM: system images only, keeps data
# Needs: unlocked bootloader, phone in fastboot mode (Power + Volume down), Android platform-tools in PATH.
# ONLY for POCO F4 5G (munch). At your own risk.
set -u
cd "$(dirname "$0")"
FB=${FASTBOOT:-fastboot}
FW="abl aop bluetooth cmnlib cmnlib64 devcfg dsp featenabler hyp imagefv keymaster modem qupfw tz uefisecapp xbl xbl_config"
KERNEL="boot dtbo vendor_boot"
LOGICAL="system system_ext product vendor odm mi_ext"
die() { echo "ERROR: $*"; exit 1; }
run() { echo "> $FB $*"; "$FB" "$@" || die "fastboot $* failed"; }

command -v "$FB" >/dev/null || die "fastboot not found (install Android platform-tools)"
echo "Checking image files (SHA256SUMS) ..."
if command -v sha256sum >/dev/null; then SUM="sha256sum"; else SUM="shasum -a 256"; fi   # macOS has shasum
(cd images && $SUM -c --quiet ../SHA256SUMS) || die "checksum mismatch: download again"
echo "Waiting for the phone in fastboot mode ..."
"$FB" wait-for-device 2>/dev/null || true
product=$("$FB" getvar product 2>&1 | awk '/^product:/{print $2}')
[ "$product" = "munch" ] || die "this is not a POCO F4 5G (product='$product'). Nothing was flashed."
unlocked=$("$FB" getvar unlocked 2>&1 | awk '/^unlocked:/{print $2}')
[ "$unlocked" = "yes" ] || die "bootloader is locked. Unlock it first (see INSTALL.md)."

if [ "${1:-}" != "update" ]; then
    echo; echo "CLEAN INSTALL: this ERASES ALL DATA on the phone. Type YES to continue:"; read -r ok
    [ "$ok" = "YES" ] || die "cancelled"
    for p in $FW; do run flash "${p}_a" "images/$p.img"; run flash "${p}_b" "images/$p.img"; done
    for p in $KERNEL; do run flash "${p}_a" "images/$p.img"; run flash "${p}_b" "images/$p.img"; done
    run --disable-verity --disable-verification flash vbmeta_a images/vbmeta.img
    run --disable-verity --disable-verification flash vbmeta_b images/vbmeta.img
    run flash vbmeta_system_a images/vbmeta_system.img
    run flash vbmeta_system_b images/vbmeta_system.img
    run --set-active=a
fi

run reboot fastboot
sleep 5; "$FB" wait-for-device 2>/dev/null || true
[ "$("$FB" getvar is-userspace 2>&1 | awk '/^is-userspace:/{print $2}')" = "yes" ] || die "phone did not reach fastbootd"
slot=$("$FB" getvar current-slot 2>&1 | awk '/^current-slot:/{print $2}')
other=$([ "$slot" = "a" ] && echo b || echo a)
# free space in super: old snapshots and the unused slot's copies
for p in $LOGICAL; do
    "$FB" delete-logical-partition "${p}_${slot}-cow" >/dev/null 2>&1
    "$FB" delete-logical-partition "${p}_${other}" >/dev/null 2>&1
done
for p in $LOGICAL; do run flash "$p" "images/$p.img"; done

if [ "${1:-}" != "update" ]; then
    run reboot bootloader
    sleep 5; "$FB" wait-for-device 2>/dev/null || true
    run erase metadata
    run erase userdata
fi
run reboot
echo; echo "Done. First boot takes 3-5 minutes (it builds the boot image once). Then see INSTALL.md: 'After the first boot'."
