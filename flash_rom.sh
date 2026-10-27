#!/bin/bash
# Flash the extracted MUNCH port ROM by fastboot, mirroring the zip's update-binary.
# Stops at the first failure.
F=/home/odoo-dbsl/android-tools/platform-tools/fastboot
I="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch/rom_extract/images"
LOG="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch/flash.log"
: > "$LOG"

flash() {
    echo "FLASHING $1 ..." | tee -a "$LOG"
    if out=$("$F" flash "$1" "$2" 2>&1); then
        echo "OK       $1" | tee -a "$LOG"
    else
        echo "FAILED   $1: $out" | tee -a "$LOG"
        echo "STOPPED at $1" | tee -a "$LOG"
        exit 1
    fi
}

for p in abl aop bluetooth boot cmnlib cmnlib64 devcfg dsp dtbo featenabler hyp imagefv keymaster modem qupfw tz uefisecapp vbmeta vbmeta_system vendor_boot xbl xbl_config; do
    flash "${p}_a" "$I/$p.img"
    flash "${p}_b" "$I/$p.img"
done

flash super "$I/super.img"
echo "ALL FLASHED" | tee -a "$LOG"
