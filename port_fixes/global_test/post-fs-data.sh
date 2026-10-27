#!/system/bin/sh
# TEST: Global cust region files (bd) over the port's China-only /system_ext/etc/cust
MODDIR=${0%/*}
chcon -R u:object_r:system_file:s0 "$MODDIR/cust" "$MODDIR/cust_prop_white_keys_list"
mount -o bind "$MODDIR/cust" /system_ext/etc/cust
mount -o bind "$MODDIR/cust_prop_white_keys_list" /system_ext/etc/cust_prop_white_keys_list
