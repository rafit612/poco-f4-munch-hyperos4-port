#!/bin/bash
# Real bytecode verification of a patched framework.jar / services.jar with the phone's own dex2oat, without installing anything.
# Usage: dex2oat_verify_on_phone.sh <orig_fw.jar> <patched_fw.jar> <orig_services.jar> <patched_services.jar>
# Files go to /data/local/tmp and are removed again at the end. Needs adb and root (su). Prints, per jar, how many classes are
# Verified / VerifiedNeedsAccessChecks / Resolved / NotReady: the patched numbers must equal the original's, and the patched
# services.jar must give the same numbers only together with the patched framework.jar (ScanPackageUtils flips otherwise).
# Pitfalls found: a boot-classpath jar cannot be verified in place (every class stays NotReady): verify it as an ordinary app dex
# against the ART core jars; dex2oat has no --threads (use -j6) and no --vdex-file; its errors only go to logcat (read them with
# `logcat -d -s dex2oat64:E`, not with a grep that also matches your own command).
set -e
A=${ADB:-adb}
[ $# -eq 4 ] || { sed -n 2,9p "$0"; exit 1; }
$A push "$1" /data/local/tmp/orig_fw.jar >/dev/null; $A push "$2" /data/local/tmp/patched_fw.jar >/dev/null
$A push "$3" /data/local/tmp/orig_sv.jar >/dev/null; $A push "$4" /data/local/tmp/patched_sv.jar >/dev/null
cat > /tmp/dex2oat_verify.sh <<'S'
rm -rf /data/local/tmp/vf; mkdir -p /data/local/tmp/vf; cd /data/local/tmp/vf
D=/apex/com.android.art/bin/dex2oat64; O=/apex/com.android.art/bin/oatdump
ART=/apex/com.android.art/javalib/core-oj.jar:/apex/com.android.art/javalib/core-libart.jar:/apex/com.android.art/javalib/okhttp.jar:/apex/com.android.art/javalib/bouncycastle.jar:/apex/com.android.art/javalib/apache-xml.jar
NONART=$(echo "$BOOTCLASSPATH" | tr ':' '\n' | grep -v '^/apex/com.android.art' | paste -sd:)
run() { # name jar framework-jar-for-class-loader-context
  FW=$(echo "$NONART" | sed "s|/system/framework/framework.jar|$3|")
  $D --dex-file=$2 --dex-location=$2 --oat-file=/data/local/tmp/vf/$1.odex --compiler-filter=verify --instruction-set=arm64 -j6 \
     --runtime-arg -Xbootclasspath:$ART --runtime-arg -Xbootclasspath-locations:$ART --boot-image=/nonexistent/boot.art --class-loader-context="PCL[$FW]" > $1.log 2>&1
  echo "== $1 (dex2oat exit $?)"
  $O --oat-file=/data/local/tmp/vf/$1.odex --no-disassemble 2>/dev/null | grep type_idx | sed 's/^.*type_idx=[0-9]*) *//' | sort | uniq -c | sort -rn | head -5
}
run fw_original /data/local/tmp/orig_fw.jar /data/local/tmp/orig_fw.jar
run fw_patched /data/local/tmp/patched_fw.jar /data/local/tmp/patched_fw.jar
run sv_original /data/local/tmp/orig_sv.jar /data/local/tmp/orig_fw.jar
run sv_patched_with_patched_fw /data/local/tmp/patched_sv.jar /data/local/tmp/patched_fw.jar
run sv_patched_with_original_fw /data/local/tmp/patched_sv.jar /data/local/tmp/orig_fw.jar
S
$A push /tmp/dex2oat_verify.sh /data/local/tmp/dex2oat_verify.sh >/dev/null
$A shell "su -c 'sh /data/local/tmp/dex2oat_verify.sh'"
$A shell "su -c 'rm -rf /data/local/tmp/vf /data/local/tmp/*.jar /data/local/tmp/dex2oat_verify.sh'"; rm -f /tmp/dex2oat_verify.sh
