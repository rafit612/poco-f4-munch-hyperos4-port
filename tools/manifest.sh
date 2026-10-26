#!/bin/bash
# manifest.sh <image> <out.tsv>
# Temporarily unpacks an EROFS or ext4 partition image, writes "path<TAB>size<TAB>sha1"
# for every file (plus symlink targets), then deletes the unpacked copy.
IMG="$1"; OUT="$2"
FSCK="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/tools/erofs/root/usr/bin/fsck.erofs"
TMP=$(mktemp -d -p "${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/audit")
magic=$(od -An -tx1 -j1024 -N4 "$IMG" | tr -d ' \n')
if [ "$magic" = "e2e1f5e0" ]; then
    "$FSCK" --extract="$TMP/root" --no-preserve "$IMG" >/dev/null 2>&1
else
    7z x -y -o"$TMP/root" "$IMG" >/dev/null 2>&1
fi
cd "$TMP/root" || exit 1
{
    find . -type f -print0 | xargs -0 -P 8 -n 200 sha1sum | awk '{h=$1; $1=""; sub(/^ +\.\//,""); print $0"\tFILE\t"h}'
    find . -type l -printf '%P\tLINK\t%l\n'
} | sort > "$OUT"
cd / && rm -rf "$TMP"
echo "$(basename "$IMG"): $(grep -c $'\tFILE\t' "$OUT") files, $(grep -c $'\tLINK\t' "$OUT") symlinks -> $(basename "$OUT")"
