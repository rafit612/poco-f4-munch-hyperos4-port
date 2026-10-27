#!/bin/bash
# Build the pure 64-bit Global image set for POCO F4 (munch) into secure_build/out_g64/.
# Base: Xiaomi 17 Global (stock_rom_global17) for system/system_ext/product/mi_ext,
#       the current port vendor + odm (out_sunday_plus). Changes: payload_g64/ (+ *.remove lists).
set -e
B="/home/odoo-dbsl/poco f4 5g 8gb 256gb munch"
T="$B/tools"
E="$T/erofs/root/usr/bin"
W=${W:?mount work dir}            # holds g17/<part> and port/vendor erofsfuse mounts
Y="$B/secure_build/payload_g64"
O="$B/secure_build/out_g64"
TMP="$W/g64tmp"
mkdir -p "$O" "$TMP"

build() {  # part orig_mount [extra mkfs args]
    local part=$1 orig=$2; shift 2
    echo "== $part: rebuild from $orig"
    python3 -I "$T/erofs_tar_rebuild.py" "$orig" "$Y/$part" "$Y/$part.remove" "$TMP/$part.tar"
    rm -f "$O/$part.img"
    "$E/mkfs.erofs" -zlz4hc,12 -b4096 -T"$(date +%s)" --all-time -E^xattr-name-filter "$@" --tar=f "$O/$part.img" "$TMP/$part.tar" > "$TMP/$part.mkfs.log" 2>&1
    rm -f "$TMP/$part.tar"
    mkdir -p "$TMP/new_$part"
    "$E/erofsfuse" "$O/$part.img" "$TMP/new_$part" > /dev/null 2>&1
    python3 -I "$T/verify_img.py" "$orig" "$TMP/new_$part" "$Y/$part" "$Y/$part.remove" | tail -3
    fusermount -u "$TMP/new_$part"
    echo "   $(stat -c %s "$O/$part.img" | awk '{printf "%.0f MB", $1/1048576}')"
}

PARTS=${PARTS:-system system_ext product mi_ext vendor}    # e.g. PARTS="product mi_ext" to rebuild only those
for p in $PARTS; do
    if [ "$p" = vendor ]; then
        build vendor "$W/port/vendor" -Ue0addc37-d7ae-453a-aa9d-c65f5856dc4d
    else
        build $p "$W/g17/$p"
    fi
done
cp "$B/secure_build/out_sunday_plus/odm.img" "$O/odm.img"
(cd "$O" && sha256sum *.img > SHA256SUMS)
ls -l "$O" | awk 'NR>1{s+=$5; printf "%8.0f MB  %s\n", $5/1048576, $9} END{printf "total %.0f MB (super group max 8702 MB)\n", s/1048576}'
