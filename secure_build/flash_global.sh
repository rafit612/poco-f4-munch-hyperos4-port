#!/bin/bash
# Flash the munch secure build (vendor, system, system_ext, product) and wipe data so /data is
# created encrypted. ERASES ALL USER DATA. Run only after backing up the phone.
#   bash flash_secure.sh            flash the new images
#   bash flash_secure.sh rollback   flash the original port images back (also wipes data)
set -u
B="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch"
ADB=/home/odoo-dbsl/Android/Sdk/platform-tools/adb
FB=/home/odoo-dbsl/android-tools/platform-tools/fastboot
LOG="$B/secure_build/flash_global.log"
log() { echo "$(date +%T) $*" | tee -a "$LOG"; }

if [ "${1:-}" = "rollback" ]; then IMG="$B/secure_build/rollback_secure"; log "ROLLBACK to the working secure build (China base)"
else IMG="$B/secure_build/out_global"; log "Flashing FULL GLOBAL build"
    (cd "$IMG" && sha256sum -c SHA256SUMS) || { log "FAILED: image checksum mismatch, nothing flashed"; exit 1; }
fi
for p in vendor system system_ext product mi_ext odm; do [ -s "$IMG/$p.img" ] || { log "FAILED: missing $IMG/$p.img"; exit 1; }; done

# 1. fastbootd (userspace fastboot) is needed to write logical partitions inside super
if "$ADB" get-state >/dev/null 2>&1; then log "adb: rebooting to fastbootd"; "$ADB" reboot fastboot
else log "no adb device: assuming the phone is already in fastboot"; "$FB" reboot fastboot >/dev/null 2>&1; fi
for i in $(seq 1 60); do [ "$("$FB" getvar is-userspace 2>&1 | grep -o 'yes')" = "yes" ] && break; sleep 2; done
[ "$("$FB" getvar is-userspace 2>&1 | grep -o 'yes')" = "yes" ] || { log "FAILED: phone did not reach fastbootd"; exit 1; }
log "in fastbootd, current slot: $("$FB" getvar current-slot 2>&1 | grep -o 'current-slot: .*')"

# 2. flash the four logical partitions (fastbootd resizes them inside super)
for p in vendor system system_ext product mi_ext odm; do
    log "flashing $p ($(du -h "$IMG/$p.img" | cut -f1))"
    "$FB" flash "$p" "$IMG/$p.img" 2>&1 | tee -a "$LOG" | grep -qiE "error|fail" && { log "FAILED on $p - run: bash flash_secure.sh rollback"; exit 1; }
done

# 3. wipe /data and /metadata so the first boot creates them encrypted (FBE + metadata encryption)
log "rebooting to bootloader to wipe userdata + metadata"
"$FB" reboot bootloader; sleep 8
"$FB" erase metadata 2>&1 | tee -a "$LOG"
"$FB" erase userdata 2>&1 | tee -a "$LOG"
log "rebooting to Android (first boot takes a few minutes)"
"$FB" reboot 2>&1 | tee -a "$LOG"
log "DONE"
