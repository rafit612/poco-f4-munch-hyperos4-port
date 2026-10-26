#!/bin/bash
# Repeatable device benchmark for the POCO F4 port: run once before a change and once after,
# then compare with tools/bench_compare.py. Read-only apart from launching/closing apps.
# Usage: bench.sh <label>   (phone unlocked, screen on, on the home screen, not in use)
set -u
ADB=${ANDROID_HOME:-$HOME/Android/Sdk}/platform-tools/adb
LABEL=${1:?label}
OUT="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}/audit/benchmarks/$LABEL"
mkdir -p "$OUT"
J="$OUT/results.tsv"; : > "$J"
put() { printf '%s\t%s\n' "$1" "$2" >> "$J"; echo "$1 = $2"; }
sh() { $ADB shell "$@" 2>/dev/null | tr -d '\r'; }

[ "$($ADB get-state 2>/dev/null)" = device ] || { echo "no device"; exit 1; }
[ "$(sh dumpsys window | grep -m1 -o 'isKeyguardShowing=[a-z]*')" = "isKeyguardShowing=false" ] || { echo "unlock the phone first"; exit 1; }
sh svc power stayon true
put date "$(date '+%F %T')"
put build "$(sh getprop ro.build.version.incremental)"
put kernel "$(sh uname -r)"
put uptime_s "$(sh cut -d. -f1 /proc/uptime)"

# --- boot (from this boot's event log if still buffered)
bc=$(sh logcat -d -b events | grep -m1 boot_progress_enable_screen | grep -oE '\[[0-9]+\]|: [0-9]+$' | grep -oE '[0-9]+' | tail -1)
put boot_enable_screen_ms "${bc:-na}"

# --- idle CPU (screen on, home screen): 5 samples of /proc/stat over 2 s
$ADB shell input keyevent KEYCODE_HOME; sleep 3
tot=0
for i in 1 2 3 4 5; do
  a=$(sh head -1 /proc/stat); sleep 2; b=$(sh head -1 /proc/stat)
  u=$(python3 -c "
a=list(map(int,'''$a'''.split()[1:])); b=list(map(int,'''$b'''.split()[1:]))
d=[y-x for x,y in zip(a,b)]; idle=d[3]+d[4]; t=sum(d)
print(round(100*(t-idle)/t,1))")
  tot=$(python3 -c "print($tot+$u)")
done
put idle_cpu_pct "$(python3 -c "print(round($tot/5,1))")"
put top_idle_procs "$(sh top -b -n1 -s 9 | sed -n '6,9p' | awk '{print $NF":"$9}' | tr '\n' ' ')"

# --- memory
put mem_available_mb "$(sh grep MemAvailable /proc/meminfo | awk '{print int($2/1024)}')"
put swap_used_mb "$(sh grep -E 'SwapTotal|SwapFree' /proc/meminfo | awk '{v[$1]=$2} END{print int((v["SwapTotal:"]-v["SwapFree:"])/1024)}')"
put cached_apps "$(sh dumpsys activity lru | grep -cE ' cch[ +]')"

# --- thermal
put battery_temp_c "$(sh dumpsys battery | grep temperature | awk '{print $2/10}')"
put thermal_status "$(sh dumpsys thermalservice | grep -m1 'Thermal Status' | awk '{print $NF}')"

# --- app cold launch (median of 3, force-stopped before each run)
launch() {  # launch <name> <package>  (launcher activity resolved on the phone)
  local n=$1 c v=() t
  c=$(sh cmd package resolve-activity --brief -c android.intent.category.LAUNCHER -a android.intent.action.MAIN "$2" | tail -1)
  case "$c" in */*) ;; *) put "launch_${n}_ms" na; return ;; esac
  for i in 1 2 3; do
    $ADB shell am force-stop "${c%%/*}"; sleep 1
    t=$(sh am start -W -n "$c" | grep -m1 -E 'TotalTime|WaitTime' | awk '{print $2}')
    [ -n "$t" ] && v+=("$t"); sleep 2
    $ADB shell input keyevent KEYCODE_HOME; sleep 1
  done
  put "launch_${n}_ms" "$(printf '%s\n' "${v[@]:-}" | sort -n | sed -n 2p)"
}
launch settings com.android.settings
launch camera com.android.camera
launch gallery com.miui.gallery
launch contacts com.android.contacts
launch messages com.android.mms
launch clock com.android.deskclock
launch calculator com.miui.calculator
launch files com.mi.android.globalFileexplorer
launch chrome com.android.chrome
$ADB shell am force-stop com.android.camera

# --- UI smoothness: notification shade 10x and app drawer scroll 10x
$ADB shell dumpsys gfxinfo com.android.systemui reset >/dev/null
for i in $(seq 1 10); do $ADB shell input swipe 540 30 540 1400 250; sleep 0.6; $ADB shell input swipe 540 1400 540 30 250; sleep 0.6; done
put jank_systemui_pct "$(sh dumpsys gfxinfo com.android.systemui | grep -m1 'Janky frames' | grep -oE '\([0-9.]+%\)' | tr -d '()%')"
$ADB shell input keyevent KEYCODE_HOME; sleep 1
# (the HyperOS 4 launcher renders with Flutter, so HWUI gfxinfo is empty for it; scroll Settings instead)
$ADB shell am start -n com.android.settings/.MainSettings >/dev/null 2>&1; sleep 2
$ADB shell dumpsys gfxinfo com.android.settings reset >/dev/null
for i in $(seq 1 10); do $ADB shell input swipe 540 1900 540 500 200; sleep 0.5; $ADB shell input swipe 540 500 540 1900 200; sleep 0.5; done
put jank_settings_pct "$(sh dumpsys gfxinfo com.android.settings | grep -m1 'Janky frames' | grep -oE '\([0-9.]+%\)' | tr -d '()%')"
put frame_p90_settings_ms "$(sh dumpsys gfxinfo com.android.settings | grep -m1 '90th percentile' | grep -oE '[0-9]+ms' | tr -d ms)"
$ADB shell input keyevent KEYCODE_HOME

# --- network latency (Wi-Fi or mobile, whatever is active)
put ping_ms "$(sh ping -c 10 -i 0.3 8.8.8.8 | tail -1 | awk -F/ '{print $5}')"

# --- battery drain at idle, screen on, home screen: charge-counter drop over 120 s (current_now is not readable)
c1=$(sh dumpsys battery | grep -m1 'Charge counter' | awk '{print $3}'); sleep 120
c2=$(sh dumpsys battery | grep -m1 'Charge counter' | awk '{print $3}')
put battery_drain_ma "$(python3 -c "print(round(($c1-$c2)/1000*30,1))" 2>/dev/null || echo na)"
put charging "$(sh dumpsys battery | grep -m1 -E 'AC powered|USB powered' | grep -c true)"

sh svc power stayon false
echo "saved: $J"
