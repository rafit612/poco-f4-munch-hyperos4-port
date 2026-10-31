#!/bin/bash
# NO-WIPE update of the system partition only (user data is never touched: no erase, no -w).
#   bash flash_system_nowipe.sh <dir with system.img + SHA256SUMS> "<log note>"
# Rollback = run it again with the previous image dir, e.g. secure_build/out_tele_T20261030_v13.
set -u
B="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch"
ADB=/home/odoo-dbsl/Android/Sdk/platform-tools/adb
FB=/home/odoo-dbsl/android-tools/platform-tools/fastboot
IMG=${1:?image dir}; NOTE=${2:-system update}
LOG="$B/secure_build/flash_global.log"
log() { echo "$(date +%T) $*" | tee -a "$LOG"; }

[ -s "$IMG/system.img" ] || { log "FAILED: $IMG/system.img missing"; exit 1; }
(cd "$IMG" && sha256sum -c SHA256SUMS 2>&1 | grep -E "system.img") | grep -q ": OK" || { log "FAILED: system.img checksum mismatch, nothing flashed"; exit 1; }
log "NO-WIPE update: system ($NOTE) from $IMG"

if "$ADB" get-state >/dev/null 2>&1; then log "adb: rebooting to fastbootd"; "$ADB" reboot fastboot
else log "no adb device: assuming the phone is already in fastboot"; "$FB" reboot fastboot >/dev/null 2>&1; fi
for i in $(seq 1 60); do [ "$("$FB" getvar is-userspace 2>&1 | grep -o 'yes')" = "yes" ] && break; sleep 2; done
[ "$("$FB" getvar is-userspace 2>&1 | grep -o 'yes')" = "yes" ] || { log "FAILED: phone did not reach fastbootd (nothing flashed)"; exit 1; }
log "in fastbootd, slot $("$FB" getvar current-slot 2>&1 | grep -o 'current-slot: .*')"

log "flashing system ($(du -h "$IMG/system.img" | cut -f1))"
if "$FB" flash system "$IMG/system.img" 2>&1 | tee -a "$LOG" | grep -qiE "^FAILED|error"; then
    log "FAILED while flashing system - run again with the previous image dir"; exit 1
fi
log "rebooting (no wipe)"; "$FB" reboot 2>&1 | tee -a "$LOG"
log "DONE"
