#!/system/bin/sh
# Battery fixes for this port (custom kernel without Xiaomi's "millet" netlink driver).
MODDIR=${0%/*}; LOG=$MODDIR/last_run.log
until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 2; done
sleep 20
# The Kaorios hook in framework.jar recreates this flag at boot (hides developer/USB-debugging state from apps).
settings put global kaorios_hide_dev_work 0
# millet_monitor fails with errno 93 (no millet netlink in the kernel) and init restarts it every ~9 s.
setprop ctl.stop millet_monitor
# HyperOS keeps Android's own cached-apps freezer off while Millet is enabled; Millet cannot work
# here, so switch it off and let the AOSP cgroup-v2 freezer (supported by this kernel) work.
[ "$(getprop persist.sys.powmillet.enable)" = "false" ] || setprop persist.sys.powmillet.enable false
[ "$(device_config get activity_manager_native_boot use_freezer)" = "true" ] || device_config put activity_manager_native_boot use_freezer true
echo "$(date) kaorios=$(settings get global kaorios_hide_dev_work) millet=$(getprop init.svc.millet_monitor) powmillet=$(getprop persist.sys.powmillet.enable)" > "$LOG"
