#!/bin/bash
# Live dashboard for all reference-ROM jobs (HyperOS 1.0.9, MIUI 14, annibale HyperOS 4, ...).
# Run: bash dashboard.sh     Ctrl+C closes only the dashboard; the work continues.
B="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
declare -A TOTAL=(  # expected download sizes in bytes, by job folder
    [stock_rom_1.0.9]=4722005552
    [stock_rom_miui14]=3875164928
    [stock_rom_annibale]=9356751434
)
declare -A NAME=(
    [stock_rom_1.0.9]="POCO F4 HyperOS 1.0.9 Global (official reference)"
    [stock_rom_miui14]="POCO F4 MIUI 14 V14.0.4.0 Global (official reference)"
    [stock_rom_annibale]="Redmi K90 / POCO F8 Pro HyperOS 4 OS4.0.0.34 (port's source)"
)
declare -A PREV_SIZE PREV_T

bar() {  # bar <percent>
    local p=${1%.*} w=40 f
    f=$(( p * w / 100 )); [ $f -gt $w ] && f=$w; [ $f -lt 0 ] && f=0
    printf "[%s%s] %5.1f%%" "$(printf '#%.0s' $(seq 1 $f) 2>/dev/null)" "$(printf '.%.0s' $(seq 1 $((w-f))) 2>/dev/null)" "$1"
}

while true; do
    clear
    echo "========== POCO F4 REFERENCE ROM JOBS   $(date +%T)   disk free: $(df -h "$B" | awk 'NR==2{print $4}') =========="
    for dir in "$B"/stock_rom_*; do
        [ -d "$dir" ] || continue
        job=$(basename "$dir"); log="$dir/progress.log"
        last=$(grep -E "STEP|ALL DONE|FAILED" "$log" 2>/dev/null | tail -1 | cut -d' ' -f2-)
        echo
        echo "### ${NAME[$job]:-$job}"
        echo "    current step: ${last:-not started}"
        zip=$(ls "$dir"/*.zip 2>/dev/null | head -1)
        if [ -n "$zip" ] && echo "$last" | grep -q "STEP 1/4: downloading"; then
            tot=${TOTAL[$job]:-0}; size=$(stat -c %s "$zip" 2>/dev/null || echo 0); now=$(date +%s)
            ps=${PREV_SIZE[$job]:-$size}; pt=${PREV_T[$job]:-$now}; dt=$(( now - pt )); [ $dt -lt 1 ] && dt=1
            speed=$(( (size - ps) / dt )); [ $speed -lt 0 ] && speed=0
            PREV_SIZE[$job]=$size; PREV_T[$job]=$now
            [ "$tot" -gt 0 ] && printf "    %s\n" "$(bar "$(echo "100*$size/$tot" | bc -l)")"
            printf "    done: %d MB   left: %d MB   total: %d MB" $((size/1000000)) $(((tot-size)/1000000)) $((tot/1000000))
            if [ $speed -gt 0 ]; then left=$(( (tot-size) / speed )); printf "   speed: %.1f MB/s   time left: %d min %02d s" "$(echo "$speed/1000000" | bc -l)" $((left/60)) $((left%60)); fi
            echo
        fi
        prog=$(grep -E "operations$" "$log" 2>/dev/null | tail -1 | cut -d' ' -f2-)
        echo "$last" | grep -q "STEP 4/4" && [ -n "$prog" ] && echo "    extracting: $prog"
        echo "    results:"
        grep -E "done:|OK|FAILED|wrote|ALL DONE" "$log" 2>/dev/null | tail -8 | sed 's/^/      /'
        imgs=$(ls "$dir/images" 2>/dev/null | tr '\n' ' ')
        [ -n "$imgs" ] && echo "    extracted images: $imgs"
    done
    echo
    echo "### RUNNING COMMANDS"
    ps -eo pid,etime,pcpu,args --sort=start_time | grep -E "curl .*(bigota|aliyuncs|miui)|md5sum|payload_extract|_pipeline\.sh" | grep -v grep | \
        sed -E 's#${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/##g' | cut -c1-130 | sed 's/^/    /'
    [ -z "$(pgrep -f 'payload_extract|md5sum|_pipeline\.sh')" ] && echo "    (no ROM job running)"
    echo
    echo "    (Ctrl+C closes this dashboard only; the work continues in the background)"
    sleep 2
done
