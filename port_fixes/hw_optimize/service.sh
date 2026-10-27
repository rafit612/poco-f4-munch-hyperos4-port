#!/system/bin/sh
# Fix 5c: official munch power-key wake boost (all clusters). init.qcom.post_boot.sh in the
# port boosts only the mid cluster; it runs at boot_completed, so re-apply after it.
until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 2; done
sleep 30
echo "0:1804800 1:0 2:0 3:0 4:2419200 5:0 6:0 7:3187200" > /sys/devices/system/cpu/cpu_boost/powerkey_input_boost_freq
