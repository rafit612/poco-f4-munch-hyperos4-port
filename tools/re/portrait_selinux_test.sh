#!/bin/bash
# Portrait crash: test whether the camera's SELinux domain is the cause, then try the fix. Run on the PC with the
# phone connected, unlocked and rooted (KernelSU/ReSukiSU, Shell granted). Every step is reversible.
#
# Why: official camera 5.1 (HyperOS 1) is platform-signed and runs as platform_app; munch's vendor policy (v30) gives
# its camera/GPU/DSP/property rules to platform_app. The re-signed camera 6.7 runs as priv_app_36, which those vendor
# rules do not cover, and the dual-bokeh depth engine aborts with zero-sized tensors.
#
#   portrait_selinux_test.sh diag     SELinux permissive for one Portrait try, then enforcing again (nothing is written)
#   portrait_selinux_test.sh install  KSU module "munch_cam_domain": product_seapp_contexts + one line that runs
#                                     com.android.camera as platform_app (like HyperOS 1); needs a reboot
#   portrait_selinux_test.sh golden D  official dual-camera golden files from folder D (RAM only, until reboot)
#   portrait_selinux_test.sh opencl D  KSU module adding HyperOS 1's libopencl-camera.so (missing in the port) from the
#                                     mounted official system_ext root D, plus its public.libraries-qti.txt entries; reboot
#   portrait_selinux_test.sh check    show the camera's domain and the newest camera crash
#   portrait_selinux_test.sh remove   delete the module; reboot to go back
set -e
A=${ADB:-adb}
M=/data/adb/modules/munch_cam_domain
SEAPP=/product/etc/selinux/product_seapp_contexts
LINE='user=_app isPrivApp=true name=com.android.camera domain=platform_app type=app_data_file levelFrom=all'
su() { $A shell su -c "\"$1\""; }

crash() { $A logcat -d -b crash | grep -E "Abort message|Fatal signal" | grep -iE "camera|DNNError" | tail -3; }

case "$1" in
diag)
  $A logcat -b crash -c
  echo "enforce before: $(su getenforce)"
  su "setenforce 0"; echo "now: $(su getenforce)"
  $A shell am start -n com.android.camera/.Camera >/dev/null
  read -rp "Open Portrait on the phone, wait 10 s, take one photo, then press Enter here… "
  su "setenforce 1"; echo "restored: $(su getenforce)"
  if crash | grep -q .; then crash; echo "RESULT: still crashes with SELinux off -> domain is NOT the cause";
  else echo "RESULT: no crash with SELinux off -> domain IS the cause; next: $0 install"; fi ;;
install)
  su "test -f $SEAPP && echo exists || echo none" | tee /dev/stderr | grep -q exists && base=1 || base=0
  su "mkdir -p $M && rm -f $M/seapp"
  [ "$base" = 1 ] && su "cat $SEAPP > $M/seapp"
  su "grep -v 'name=com.android.camera ' $M/seapp 2>/dev/null > $M/seapp.t; echo '$LINE' >> $M/seapp.t; mv $M/seapp.t $M/seapp"
  su "chown root:root $M/seapp; chmod 644 $M/seapp; chcon u:object_r:seapp_contexts_file:s0 $M/seapp"
  su "printf 'id=munch_cam_domain\nname=Camera as platform_app (Portrait test)\nversion=1\nversionCode=1\nauthor=munch\ndescription=Runs com.android.camera in platform_app like HyperOS 1\n' > $M/module.prop"
  su "printf '#!/system/bin/sh\nmount --bind $M/seapp $SEAPP\n' > $M/post-fs-data.sh; chmod 755 $M/post-fs-data.sh"
  [ "$base" = 1 ] || echo "note: no product_seapp_contexts on this build; the bind needs an existing file -> stop and report"
  su "cat $M/seapp | tail -3"; echo "installed; reboot, unlock, then: $0 check" ;;
golden)
  # Second suspect: the porter's vendor has its own wide+ultra dual-camera golden files; MIUI 14 and HyperOS 1 share
  # c0e7e796… (audit/agents/camera/inventory.tsv). $2 = folder with the official com.xiaomi.dcal.wu.golden{,2}
  # (e.g. from the mounted stock_rom_1.0.9 vendor.img, etc/camera/). RAM-only bind mount; a reboot undoes it.
  D=${2:?usage: $0 golden <folder with official com.xiaomi.dcal.wu.golden and .golden2>}
  su "sha1sum /vendor/etc/camera/com.xiaomi.dcal.wu.golden*"
  for f in golden golden2; do
    [ "$(sha1sum < "$D/com.xiaomi.dcal.wu.$f" | cut -c1-40)" = c0e7e7969cb1a0465ccbca8e9f7a7cfd33c5612c ] \
      || { echo "$D/com.xiaomi.dcal.wu.$f is not the official file"; exit 1; }
    $A push "$D/com.xiaomi.dcal.wu.$f" /data/local/tmp/dcal_$f >/dev/null
    su "chown root:root /data/local/tmp/dcal_$f; chmod 644 /data/local/tmp/dcal_$f; chcon u:object_r:vendor_configs_file:s0 /data/local/tmp/dcal_$f; mount --bind /data/local/tmp/dcal_$f /vendor/etc/camera/com.xiaomi.dcal.wu.$f"
  done
  su "sha1sum /vendor/etc/camera/com.xiaomi.dcal.wu.golden*"
  $A shell am force-stop com.android.camera; su "pkill -f camera.provider"; sleep 3
  $A logcat -b crash -c; echo "official golden files active until reboot; open Portrait, then: $0 check" ;;
opencl)
  # Third suspect: official HyperOS 1 system_ext has lib{,64}/libopencl-camera.so; the port has none, and the depth
  # engine runs inside the camera app right where it loads OpenCL. Adds the official files systemlessly.
  D=${2:?usage: $0 opencl <mounted official HyperOS 1 system_ext root>}; O=/data/adb/modules/munch_cam_opencl
  [ -f "$D/lib64/libopencl-camera.so" ] || { echo "no $D/lib64/libopencl-camera.so"; exit 1; }
  for l in lib lib64; do $A push "$D/$l/libopencl-camera.so" /data/local/tmp/oc_$l.so >/dev/null; done
  $A shell cat /system_ext/etc/public.libraries-qti.txt > /tmp/port_pub.txt
  missing=$(grep -vxFf /tmp/port_pub.txt "$D/etc/public.libraries-qti.txt" | grep -v '^#' || true)
  echo "official public.libraries-qti.txt entries missing on the phone: ${missing:-none}"
  su "mkdir -p $O/system/system_ext/lib $O/system/system_ext/lib64 $O/system/system_ext/etc"
  for l in lib lib64; do su "mv /data/local/tmp/oc_$l.so $O/system/system_ext/$l/libopencl-camera.so; chown root:root $O/system/system_ext/$l/libopencl-camera.so; chmod 644 $O/system/system_ext/$l/libopencl-camera.so; chcon u:object_r:system_lib_file:s0 $O/system/system_ext/$l/libopencl-camera.so"; done
  if [ -n "$missing" ]; then
    { cat /tmp/port_pub.txt; echo "$missing"; } > /tmp/new_pub.txt; $A push /tmp/new_pub.txt /data/local/tmp/pub.txt >/dev/null
    su "mv /data/local/tmp/pub.txt $O/system/system_ext/etc/public.libraries-qti.txt; chown root:root $O/system/system_ext/etc/public.libraries-qti.txt; chmod 644 $O/system/system_ext/etc/public.libraries-qti.txt; chcon u:object_r:system_file:s0 $O/system/system_ext/etc/public.libraries-qti.txt"
  fi
  su "printf 'id=munch_cam_opencl\nname=HyperOS 1 libopencl-camera (Portrait test)\nversion=1\nversionCode=1\nauthor=munch\ndescription=test\n' > $O/module.prop"
  echo "installed; reboot, open Portrait, then: $0 check   (undo: su -c rm -rf $O; reboot)" ;;
check)
  $A shell am start -n com.android.camera/.Camera >/dev/null; sleep 3
  $A shell ps -AZ | grep -E "com\.android\.camera" || true
  $A logcat -d | grep -E "seapp|SELinux: .*seapp|selinux_android_setcontext" | tail -5 || true
  echo "--- newest camera crash (empty = none since boot):"; crash ;;
remove)
  su "rm -rf $M"; echo "removed; reboot to restore the original domain" ;;
*) sed -n 2,14p "$0"; exit 1 ;;
esac
