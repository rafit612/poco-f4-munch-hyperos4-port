#!/bin/bash
# Reference ROM: Redmi K90 / POCO F8 Pro ("annibale") official HyperOS 4 China OS4.0.0.34.XPKCNXM.
# The port's product/mi_ext came from annibale; this lets us diff the port against its official source.
R="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/stock_rom_annibale"
ZIP="annibale-ota_full-OS4.0.0.34.XPKCNXM-user-17.0-8982747db5.zip"
URL="https://bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com/OS4.0.0.34.XPKCNXM/$ZIP"
MD5_PREFIX="8982747db5"
EXTRACT="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/tools/payload_extract.py"
LOG="$R/progress.log"
log() { echo "$(date +%T) $*" >> "$LOG"; }

mkdir -p "$R/images" && cd "$R" || exit 1
log "STEP 1/4: downloading annibale HyperOS 4 OS4.0.0.34 (9.36 GB) from Xiaomi Singapore mirror"
curl -sL --retry 5 --retry-delay 5 -C - --max-time 10800 -o "$ZIP" "$URL" || { log "FAILED: download error"; exit 1; }
log "STEP 1/4 done: $(du -h "$ZIP" | cut -f1) downloaded"

log "STEP 2/4: verifying MD5 prefix from Xiaomi's file name ($MD5_PREFIX)"
got=$(md5sum "$ZIP" | cut -d' ' -f1)
case "$got" in "$MD5_PREFIX"*) log "STEP 2/4 done: MD5 $got matches prefix - genuine official file" ;;
    *) log "FAILED: MD5 $got does not match $MD5_PREFIX"; exit 1 ;; esac

log "STEP 3/4: reading partition list"
python3 -I "$EXTRACT" "$ZIP" --list > partitions.txt 2>&1 || { log "FAILED: payload parse"; exit 1; }
log "STEP 3/4 done: $(grep -c . partitions.txt) partitions found"

for p in system_ext system product mi_ext odm; do
    grep -q "^$p " partitions.txt || { log "  skip $p (not in payload)"; continue; }
    log "STEP 4/4: extracting $p"
    python3 -I "$EXTRACT" "$ZIP" "$p" images 2>&1 | while read -r line; do log "  $p: $line"; done
done
log "ALL DONE"
