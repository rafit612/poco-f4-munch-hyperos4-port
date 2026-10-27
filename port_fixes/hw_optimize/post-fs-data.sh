#!/system/bin/sh
# Runs before vendor services and system_server start.
MODDIR=${0%/*}
RP=/data/adb/ksu/bin/resetprop
chcon u:object_r:vendor_configs_file:s0 "$MODDIR/fingerprint_hidden.xml" "$MODDIR"/thermal/*.conf

# Fix 0: hide the fingerprint feature so system_server stops retrying the dead sensor
# (flex cable cut). Delete this module's fingerprint_hidden.xml after the repair.
FP=/vendor/etc/permissions/android.hardware.fingerprint.xml
[ -f "$MODDIR/fingerprint_hidden.xml" ] && [ -f "$FP" ] && mount -o bind "$MODDIR/fingerprint_hidden.xml" "$FP"

# Fix 1: official POCO F4 (HyperOS 1.0.9) thermal profiles over the port's empty ones.
for f in "$MODDIR"/thermal/*.conf; do
    d=/vendor/etc/$(basename "$f")
    [ -f "$d" ] && mount -o bind "$f" "$d"
done

# Fix 3: munch.xml with real hardware values (battery 4520, CPU 3.2 GHz, 60 Hz default)
# and official munch features (AOD, True Tone, gesture shortcuts, game/cloud dim).
# Fix 4: hide the virtualization feature (no hypervisor on this kernel).
chcon u:object_r:system_file:s0 "$MODDIR/munch.xml" "$MODDIR/virt_hidden.xml"
MX=/product/etc/device_features/munch.xml
[ -f "$MODDIR/munch.xml" ] && [ -f "$MX" ] && mount -o bind "$MODDIR/munch.xml" "$MX"
VX=/product/etc/permissions/features_com.android.virt.xml
[ -f "$MODDIR/virt_hidden.xml" ] && [ -f "$VX" ] && mount -o bind "$MODDIR/virt_hidden.xml" "$VX"

# Fix 5a: official munch Wi-Fi config (port added aggressive EDCA values from another device).
chcon u:object_r:vendor_configs_file:s0 "$MODDIR/WCNSS_qcom_cfg.ini"
WI=/vendor/etc/wifi/qca6390/WCNSS_qcom_cfg.ini
[ -f "$MODDIR/WCNSS_qcom_cfg.ini" ] && [ -f "$WI" ] && mount -o bind "$MODDIR/WCNSS_qcom_cfg.ini" "$WI"
# Fix 5b: RAM partial-array self-refresh power saving (official munch vendor value).
$RP vendor.pasr.activemode.enabled true

# Fix 7a: traced (perfetto) crash loop - the K90 donor's product sets a vsock relay port,
# but kernel 4.19 has no AF_VSOCK, so traced exits on every start.
$RP --delete traced.relay_producer_port
# Fix 7b: ATFWD-daemon crash loop - old vendor seccomp policy lacks syscalls the new libc uses.
chcon u:object_r:vendor_configs_file:s0 "$MODDIR/atfwd@2.0.policy"
AP=/vendor/etc/seccomp_policy/atfwd@2.0.policy
[ -f "$MODDIR/atfwd@2.0.policy" ] && [ -f "$AP" ] && mount -o bind "$MODDIR/atfwd@2.0.policy" "$AP"

# Fix 8: audio - official munch values. The port set surround.headphone.only=false, so MiSound
# asks the DSP for speaker surround (NDSURROUND), which the munch DSP does not support.
$RP ro.vendor.audio.surround.headphone.only true
$RP audio.offload.gapless.enabled true

# Security step 1: privileged-permission allowlist "disable" -> "enforce" (official HyperOS 4 value).
# Every priv-app permission must be allowlisted first, or system_server fails at boot: if a new
# priv-app is added, switch this to "log", reboot, add the logged permissions, then enforce again.
$RP ro.control_privapp_permissions enforce
# Allowlist for the product priv-apps found in log mode, bind-mounted over an existing product
# permission file (keeps that file's original eu.xiaomi.ext entries).
chcon u:object_r:system_file:s0 "$MODDIR/privapp_whitelist_combined.xml"
PW=/product/etc/permissions/privapp_whitelist_eu.xiaomi.ext.xml
[ -f "$MODDIR/privapp_whitelist_combined.xml" ] && [ -f "$PW" ] && mount -o bind "$MODDIR/privapp_whitelist_combined.xml" "$PW"

# Fix 2: official values (vendor sets 1000 ms; the port's product overrides them to "never").
$RP ro.surface_flinger.set_idle_timer_ms 1000
$RP ro.surface_flinger.set_touch_timer_ms 1000
$RP --delete ro.surface_flinger.set_display_power_timer_ms
$RP persist.sys.deviceidle.disable false
$RP persist.sys.enable_templimit true
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do $RP --delete sys.keep_app_$i; done
