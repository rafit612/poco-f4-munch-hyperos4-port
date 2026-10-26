#!/bin/bash
# Read-only FUSE mounts of every image used by the build and audits.
# R = reference/original images, N = images currently flashed on the phone (out_global).
# Mount points live in /tmp and disappear on reboot/session cleanup; just run this again.
B="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
E="$B/tools/erofs/root/usr/bin/erofsfuse"
F2="$B/tools/e2fs/root/usr/bin/fuse2fs"
R=/tmp/claude-1000/155acf9c-1946-41a4-8e72-96ea9676041c/scratchpad
N=/tmp/claude-1000/-home-odoo-dbsl-poco-f4-5g-8gb-256gb-munch/155acf9c-1946-41a4-8e72-96ea9676041c/scratchpad
mnt() {  # mnt <dir> <image>
    mkdir -p "$1"; mountpoint -q "$1" && return
    "$E" "$2" "$1" >/dev/null 2>&1 || "$F2" -o ro,fakeroot "$2" "$1" >/dev/null 2>&1
    mountpoint -q "$1" && echo "ok   $1" || echo "FAIL $1"
}
# original port (the build source)
mnt $R/mnt_prod "$B/audit/port/product.img"
mnt $R/o_se     "$B/audit/port/system_ext.img"
mnt $R/o_sys    "$B/audit/port/system.img"
mnt $R/opv      "$B/audit/port/vendor.img"
# official HyperOS 1 (munch)
mnt $R/h1v           "$B/stock_rom_1.0.9/images/vendor.img"
mnt $R/h1_product    "$B/stock_rom_1.0.9/images/product.img"
mnt $R/h1_system     "$B/stock_rom_1.0.9/images/system.img"
mnt $R/h1_system_ext "$B/stock_rom_1.0.9/images/system_ext.img"
# Xiaomi 17 Global HyperOS 4
mnt $R/g17_product    "$B/stock_rom_global17/images/product.img"
mnt $R/g17_system     "$B/stock_rom_global17/images/system.img"
mnt $R/g17_system_ext "$B/stock_rom_global17/images/system_ext.img"
mnt $R/glob/m/mi_ext  "$B/stock_rom_global17/images/mi_ext.img"
# currently flashed build
O="$B/secure_build/out_global"
mnt $N/n_ven "$O/vendor.img"
mnt $N/n_sys "$O/system.img"
mnt $N/n_se  "$O/system_ext.img"
mnt $N/n_pr  "$O/product.img"
mnt $N/n_mx2 "$O/mi_ext.img"
