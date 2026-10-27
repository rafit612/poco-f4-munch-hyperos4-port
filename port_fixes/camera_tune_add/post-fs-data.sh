#!/system/bin/sh
# Bind-mount official POCO F4 (HyperOS 1.0.9) camera files over the port's vendor copies
# before the camera HAL starts.
MODDIR=${0%/*}
bind() { [ -f "$1" ] && [ -f "$2" ] && chcon "$3" "$1" && mount -o bind "$1" "$2"; }
# CamX settings: official enableSensorHWSync=1, numConsecutiveRecovery=10
bind "$MODDIR/camxoverridesettings.txt" /vendor/etc/camera/camxoverridesettings.txt u:object_r:vendor_configs_file:s0
# Front OFilm IMX596 tuning (port's copy has weaker temporal noise reduction, changed AWB)
bind "$MODDIR/lib64/com.qti.tuned.munch_ofilm_imx596_front.bin" /vendor/lib64/camera/com.qti.tuned.munch_ofilm_imx596_front.bin u:object_r:vendor_file:s0
bind "$MODDIR/lib/com.qti.tuned.munch_ofilm_imx596_front.bin" /vendor/lib/camera/com.qti.tuned.munch_ofilm_imx596_front.bin u:object_r:vendor_file:s0
# Wide/ultrawide dual-camera calibration (official golden files)
bind "$MODDIR/etc/com.xiaomi.dcal.wu.golden" /vendor/etc/camera/com.xiaomi.dcal.wu.golden u:object_r:vendor_configs_file:s0
bind "$MODDIR/etc/com.xiaomi.dcal.wu.golden2" /vendor/etc/camera/com.xiaomi.dcal.wu.golden2 u:object_r:vendor_configs_file:s0
