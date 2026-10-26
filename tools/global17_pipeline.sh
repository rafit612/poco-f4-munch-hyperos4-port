#!/bin/bash
# Reference ROM: Xiaomi 17 (pudding) official HyperOS 4 GLOBAL OS4.0.0.9.XPCMIXM (Android 17).
# Used to see how Xiaomi Global integrates Google services, Gemini and AI, for the munch port.
R="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/stock_rom_global17"
ZIP="pudding_global-ota_full-OS4.0.0.9.XPCMIXM-user-17.0-4fe981b89f.zip"
URL="https://bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com/OS4.0.0.9.XPCMIXM/$ZIP"
EXTRACT="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/tools/payload_extract.py"
LOG="$R/progress.log"; log() { echo "$(date +%T) $*" >> "$LOG"; }
mkdir -p "$R/images" && cd "$R" || exit 1
log "STEP 1/4: downloading Xiaomi 17 Global HyperOS 4 OS4.0.0.9 (8.46 GB)"
curl -sL --retry 5 --retry-delay 5 -C - --max-time 10800 -o "$ZIP" "$URL" || { log "FAILED: download error"; exit 1; }
log "STEP 1/4 done: $(du -h "$ZIP" | cut -f1) downloaded"
log "STEP 2/4: verifying MD5 prefix (4fe981b89f)"
got=$(md5sum "$ZIP" | cut -d' ' -f1)
case "$got" in 4fe981b89f*) log "STEP 2/4 done: MD5 $got matches - genuine official file" ;; *) log "FAILED: MD5 $got"; exit 1 ;; esac
log "STEP 3/4: reading partition list"
python3 -I "$EXTRACT" "$ZIP" --list > partitions.txt 2>&1 || { log "FAILED: payload parse"; exit 1; }
log "STEP 3/4 done: $(grep -c . partitions.txt) partitions"
for p in system_ext system product mi_ext; do
    grep -q "^$p " partitions.txt || { log "  skip $p (not in payload)"; continue; }
    log "STEP 4/4: extracting $p"
    python3 -I "$EXTRACT" "$ZIP" "$p" images 2>&1 | while read -r line; do log "  $p: $line"; done
done
rm -f "$ZIP"; log "zip deleted after extraction"; log "ALL DONE"
