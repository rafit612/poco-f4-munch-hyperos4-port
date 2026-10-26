#!/bin/bash
# mkboot_v3.sh <kernel> <ramdisk> <out> : boot header v3 like the port's, keeping its os_version field (porter used patch month 00)
set -e
T=$HOME/kernel_build/tools; ORIG="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/rom_extract/images/boot.img"
python3 -E -s $T/mkbootimg.py --header_version 3 --os_version 13.0.0 --os_patch_level 2025-01 --cmdline '' --kernel "$1" --ramdisk "$2" --output "$3"
dd if="$ORIG" of="$3" bs=1 skip=16 seek=16 count=4 conv=notrunc status=none   # os_version/patch field
