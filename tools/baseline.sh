#!/bin/bash
# Passive baseline for the POCO F4 port: only observes, no taps, app launches or setting changes, so it can run while the phone is in normal use.
# Compare runs taken in the same state (screen, charging, foreground app are recorded). tools/bench.sh is the active version with app launches.
# usage: baseline.sh <label> [seconds, default 120]   writes docs/rom_map/phone_audit/baseline_<label>.txt (git-ignored: it names installed apps)
set -u
ADB=${ANDROID_HOME:-$HOME/Android/Sdk}/platform-tools/adb
L=${1:?label}; S=${2:-120}
R="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}"; O="$R/docs/rom_map/phone_audit/baseline_$L.txt"; mkdir -p "$(dirname "$O")"
s() { timeout 40 "$ADB" shell "$@" 2>/dev/null | tr -d '\r'; }
su_() { timeout 60 "$ADB" shell "su -c '$1'" 2>/dev/null | tr -d '\r'; }
{
echo "date $(date '+%F %T') window ${S}s"; echo "build $(s getprop ro.build.fingerprint | cut -d/ -f5 | cut -d: -f1)"; echo "kernel $(s uname -r)"
echo "uptime_s $(s cut -d. -f1 /proc/uptime)"
echo "state $(s dumpsys power | grep -m1 mWakefulness | tr -d ' ') $(s dumpsys window | grep -m1 -o 'mCurrentFocus=[^ ]* [^ ]* [^ }]*' | cut -d' ' -f3)"
echo "battery $(s dumpsys battery | grep -E 'level|temperature|AC powered|USB powered' | tr -s ' ' | tr '\n' ';')"
a=$(s head -1 /proc/stat); w0=$(su_ "cat /proc/stat" | grep -E '^ctxt|^intr' | awk '{print $2}' | tr '\n' ' ')
su_ "dumpsys batterystats --reset" >/dev/null 2>&1 &
su_ "logcat -b all -c"
c0=$(su_ "cat /proc/[0-9]*/stat 2>/dev/null" | awk '{gsub(/[()]/,"",$2); t[$1" "$2]=$14+$15} END{for(k in t) print k,t[k]}')
sleep "$S"
b=$(s head -1 /proc/stat); w1=$(su_ "cat /proc/stat" | grep -E '^ctxt|^intr' | awk '{print $2}' | tr '\n' ' ')
c1=$(su_ "cat /proc/[0-9]*/stat 2>/dev/null" | awk '{gsub(/[()]/,"",$2); t[$1" "$2]=$14+$15} END{for(k in t) print k,t[k]}')
python3 - "$a" "$b" "$w0" "$w1" "$S" <<'PY'
import sys
a,b,w0,w1,S=sys.argv[1:]; S=float(S)
a=list(map(int,a.split()[1:]));b=list(map(int,b.split()[1:]));d=[y-x for x,y in zip(a,b)];t=sum(d)
print('cpu_busy_pct %.1f  iowait_pct %.1f'%(100*(t-d[3]-d[4])/t,100*d[4]/t))
x=w0.split();y=w1.split()
if len(x)==2 and len(y)==2: print('ctxt_per_s %d  irq_per_s %d'%((int(y[1])-int(x[1]))/S,(int(y[0])-int(x[0]))/S))
PY
echo "--- top processes by CPU in the window (percent of one core)"
python3 - "$S" "$c0" "$c1" <<'PY'
import sys
S=float(sys.argv[1]);p=lambda s:{' '.join(l.split()[:2]):int(l.split()[-1]) for l in s.splitlines() if len(l.split())>=3}
a=p(sys.argv[2]);b=p(sys.argv[3])
r=sorted(((b[k]-a.get(k,b[k]))/100/S*100,k.split(' ',1)[1]) for k in b)[::-1][:14]
for v,n in r:
    if v>=0.1: print('%5.1f %s'%(v,n))
PY
echo "--- memory"; su_ "cat /proc/meminfo" | grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree|^Cached' | tr -s ' ' | tr '\n' ';'; echo; s cat /proc/vmstat | grep -E '^(pswpin|pswpout|pgmajfault|allocstall_normal|workingset_refault_file) ' | tr '\n' ';'; echo
echo "--- thermal"; su_ "for z in /sys/class/thermal/thermal_zone*; do echo \$(cat \$z/type) \$(cat \$z/temp); done" | awk '$2>1000{printf "%s=%.0f ",$1,$2/1000}' | tr ' ' '\n' | sort -t '=' -k2 -rn | head -6 | tr '\n' ' '; echo
echo "--- log volume in the window"; su_ "logcat -b all -d" > /tmp/bl_$$.log; echo "lines $(wc -l < /tmp/bl_$$.log)"
echo "--- top repeating log messages"; sed -E 's/^.{31}//; s/[0-9]+/N/g' /tmp/bl_$$.log | cut -c1-90 | sort | uniq -c | sort -rn | head -14
echo "--- SELinux denials"; grep -a 'avc: *denied' /tmp/bl_$$.log | sed -E 's/.*denied +\{ ([^}]*)\}.*scontext=u:r:([a-z0-9_]+):.*tcontext=u:[a-z_]+:([a-z0-9_]+):.*tclass=([a-z_]+).*/\2 -> \3 \4 {\1}/' | sort | uniq -c | sort -rn | head -8
rm -f /tmp/bl_$$.log
} > "$O" 2>&1
echo "$O"
