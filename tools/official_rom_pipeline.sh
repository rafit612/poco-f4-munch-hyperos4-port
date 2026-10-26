#!/bin/bash
# Download the official POCO F4 1.0.9 Global recovery ROM, verify it, and extract
# the partitions needed for the official-vs-port comparison. Progress -> progress.log
R="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/stock_rom_1.0.9"
ZIP="miui_MUNCHGlobal_OS1.0.9.0.ULMMIXM_7b798621ce_14.0.zip"
URL="https://bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com/OS1.0.9.0.ULMMIXM/$ZIP"
MD5="7b798621ce6a111c53f4253200b781ab"
EXTRACT="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/tools/payload_extract.py"
LOG="$R/progress.log"
log() { echo "$(date +%T) $*" >> "$LOG"; }

cd "$R" || exit 1
log "STEP 1/4: downloading official ROM from Xiaomi Singapore mirror (4.72 GB)"
curl -sL --retry 5 --retry-delay 5 -C - --max-time 7200 -o "$ZIP" "$URL" || { log "FAILED: download error"; exit 1; }
log "STEP 1/4 done: $(du -h "$ZIP" | cut -f1) downloaded"

log "STEP 2/4: verifying MD5 against Xiaomi's published value"
got=$(md5sum "$ZIP" | cut -d' ' -f1)
if [ "$got" != "$MD5" ]; then log "FAILED: MD5 mismatch (got $got)"; exit 1; fi
log "STEP 2/4 done: MD5 OK ($got) - genuine official file"

log "STEP 3/4: reading partition list from payload.bin"
python3 -I "$EXTRACT" "$ZIP" --list > partitions.txt 2>&1 || { log "FAILED: payload parse"; exit 1; }
log "STEP 3/4 done: $(wc -l < partitions.txt) partitions found"

mkdir -p images
for p in vendor product system_ext system odm mi_ext; do
    grep -q "^$p " partitions.txt || { log "  skip $p (not in payload)"; continue; }
    log "STEP 4/4: extracting $p"
    python3 -I "$EXTRACT" "$ZIP" "$p" images 2>&1 | while read -r line; do log "  $p: $line"; done
done
log "ALL DONE"
