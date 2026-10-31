#!/bin/bash
# Port image set (out_sunday_plus) + Global telephony data (payload_tele) -> out_tele/
# mi_ext: /mi_ext/product/etc/vendor_device.xml (Xiaomi VoLTE globalization for all operators)
# product: Global APN database (228 countries) + IMS APNs for 470-03 / 470-04
set -e
# noinline_data: the 4.19 kernel EROFS driver rejects inline symlink data that crosses a 4 KB block
# ("erofs_fill_symlink: inline data cross block boundary", e.g. /system/bin/getprop unreadable). Stock
# mkfs.erofs 1.9.1 applies noinline_data to regular files only, so MK is patched to include symlinks.
B="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}"; T="$B/tools"; E="$T/erofs/root/usr/bin"; MK="$T/erofs/munch/mkfs.erofs"
W=${W:?mount work dir}; Y="${PAYLOAD:-$B/secure_build/payload_tele}"; O="${OUT:-$B/secure_build/out_tele}"; TMP="$W/teletmp"
# PAYLOAD / OUT (optional) build a separate change set, e.g. secure_build/payload_sigfix -> secure_build/out_sigfix, without touching payload_tele
mkdir -p "$O" "$TMP"
for part in ${PARTS:-mi_ext product}; do
    orig="$W/port/$part"
    python3 -I "$T/erofs_tar_rebuild.py" "$orig" "$Y/$part" "$Y/$part.remove" "$TMP/$part.tar"
    rm -f "$O/$part.img"
    "$MK" -zlz4hc,12 -b4096 -T"$(date +%s)" --all-time -E^xattr-name-filter,noinline_data --tar=f "$O/$part.img" "$TMP/$part.tar" > "$TMP/$part.mkfs.log" 2>&1
    rm -f "$TMP/$part.tar"
    mkdir -p "$TMP/new_$part"; "$E/erofsfuse" "$O/$part.img" "$TMP/new_$part" > /dev/null 2>&1
    python3 -I "$T/verify_img.py" "$orig" "$TMP/new_$part" "$Y/$part" "$Y/$part.remove" | tail -1
    python3 -I "$T/erofs_symlink_check.py" "$O/$part.img" | tail -1
    fusermount -u "$TMP/new_$part"
done
(cd "$O" && sha256sum *.img > SHA256SUMS)
