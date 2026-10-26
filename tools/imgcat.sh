#!/bin/bash
# imgcat.sh <image> <path-inside> : print one file from an EROFS or ext4 partition image (read-only)
D="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/tools/erofs/root/usr/bin/dump.erofs"
if [ "$(od -An -tx1 -j1024 -N4 "$1" | tr -d ' \n')" = "e2e1f5e0" ]; then "$D" --cat --path="/$2" "$1"
else debugfs -R "cat /$2" "$1" 2>/dev/null; fi
