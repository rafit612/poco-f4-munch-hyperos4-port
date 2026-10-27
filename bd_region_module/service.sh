#!/system/bin/sh
# 1) Mark this boot successful: the port never does it, so A/B retries run out
#    after 7 reboots and the phone falls into fastboot.
# 2) Re-apply the Bangladesh region after Xiaomi's late-boot scripts reset it to CN.
BIN=/data/adb/ksu/bin
until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 2; done
$BIN/bootctl mark-boot-successful
for i in 1 2 3 4 5 6; do
    [ "$(getprop ro.miui.region)" != "BD" ] && $BIN/resetprop -n ro.miui.region BD
    sleep 5
done
