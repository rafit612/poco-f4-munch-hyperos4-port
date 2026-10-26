#!/bin/bash
# Read-only hardware/OS tuning probe for the POCO F4 port. Prints one section per subsystem.
# Usage: hw_probe.sh > audit/hw_probe_<date>.txt
ADB=${ANDROID_HOME:-$HOME/Android/Sdk}/platform-tools/adb
sh() { $ADB shell "$@" 2>/dev/null | tr -d '\r'; }
sec() { echo; echo "### $1"; }
rd() { for f in "$@"; do v=$(sh "cat $f" | head -c 300 | tr '\n' ' '); echo "$f = ${v:-<unreadable>}"; done; }

sec "CPU clusters / governor (schedutil)"
for p in 0 4 7; do
  rd /sys/devices/system/cpu/cpufreq/policy$p/scaling_governor /sys/devices/system/cpu/cpufreq/policy$p/scaling_min_freq \
     /sys/devices/system/cpu/cpufreq/policy$p/scaling_max_freq /sys/devices/system/cpu/cpufreq/policy$p/cpuinfo_max_freq
  sh "ls /sys/devices/system/cpu/cpufreq/policy$p/schedutil/ 2>/dev/null" | tr '\n' ' '; echo
  for k in up_rate_limit_us down_rate_limit_us hispeed_freq hispeed_load rate_limit_us; do
    v=$(sh "cat /sys/devices/system/cpu/cpufreq/policy$p/schedutil/$k"); [ -n "$v" ] && echo "policy$p schedutil/$k = $v"; done
done
sec "EAS / capacity / sched knobs"
rd /sys/devices/system/cpu/cpu0/cpu_capacity /sys/devices/system/cpu/cpu4/cpu_capacity /sys/devices/system/cpu/cpu7/cpu_capacity
sh "ls /proc/sys/kernel/ | grep -E '^sched_'" | tr '\n' ' '; echo
rd /proc/sys/kernel/sched_boost /proc/sys/kernel/sched_energy_aware /proc/sys/kernel/sched_util_clamp_min /proc/sys/kernel/sched_util_clamp_max
sec "cgroups / stune / uclamp"
sh "cat /proc/cgroups"; sh "ls -d /dev/stune /dev/cpuctl/top-app 2>&1; ls /dev/cpuctl/top-app 2>/dev/null | grep -E 'uclamp|shares'" | tr '\n' ' '; echo
sec "GPU (Adreno 650, kgsl devfreq)"
rd /sys/class/kgsl/kgsl-3d0/devfreq/governor /sys/class/kgsl/kgsl-3d0/max_gpuclk /sys/class/kgsl/kgsl-3d0/devfreq/min_freq \
   /sys/class/kgsl/kgsl-3d0/devfreq/max_freq /sys/class/kgsl/kgsl-3d0/devfreq/available_frequencies /sys/class/kgsl/kgsl-3d0/gpu_model
sec "devfreq (bus/DDR/LLCC)"
for d in $(sh "ls /sys/class/devfreq/" ); do echo "$d gov=$(sh "cat /sys/class/devfreq/$d/governor")"; done | head -20
sec "Hexagon DSP / NPU (NNAPI)"
sh "getprop | grep -iE 'init.svc.*(neural|nnapi|cdsp|adsp|fastrpc|qti.*dsp)'"
sh "ls /dev/ | grep -iE 'fastrpc|adsprpc|cdsp'" | tr '\n' ' '; echo
sec "Charging / PMIC / battery"
sh "dumpsys battery" | grep -E 'AC|USB|Wireless|status|health|level|voltage|temperature|technology|Max charging'
rd /sys/class/power_supply/usb/real_type /sys/class/power_supply/usb/pd_active /sys/class/power_supply/battery/charge_type \
   /sys/class/power_supply/battery/cycle_count /sys/class/power_supply/bms/charge_full_design
sec "Audio: ALSA SoC, Smart PA (TFA98xx), Dolby, Hi-Res"
sh "cat /proc/asound/cards"; sh "getprop | grep -iE 'dolby|dax|hifi|hires|audio.offload|misound|ro.vendor.audio.(spk|sfx|soundfx)'" | head -20
sh "getprop | grep -iE 'init.svc.*(audio|dolby|dax|dms)'"
sec "IR blaster"
sh "service check consumer_ir; dumpsys consumer_ir 2>/dev/null | head -3"; sh "pm has-feature android.hardware.consumerir"
sec "Display: panel, DFPS, HDR, 10-bit, DC dimming, kcal"
sh "dumpsys display" | grep -m3 -oE 'supportedModes \[[^]]*\]|supportedColorModes \[[^]]*\]|hdrCapabilities HdrCapabilities\{[^}]*\}' | cut -c1-400
sh "getprop | grep -iE 'dc_backlight|dcdimming|dc_dimming|dfps|refresh|vendor.display|ro.surface_flinger|debug.sf|persist.sys.sf'" | head -30
rd /sys/devices/platform/kcal_ctrl.0/kcal /sys/class/drm/card0-DSI-1/panel_info
sec "SurfaceFlinger / HWC / Gralloc"
sh "dumpsys SurfaceFlinger" | grep -m6 -iE 'Display [0-9]+ HWC|refresh-rate|composition|GLES:|vsync|max frame buffer'
sh "lshal list 2>/dev/null" | grep -iE 'composer|allocator|mapper|power|perf|radio|thermal|neuralnetworks|vibrator|ir@' | awk '{print $2}' | sort -u
sec "Vulkan / OpenGL"
sh "pm list features" | grep -iE 'vulkan|opengles'
sh "getprop ro.hardware.vulkan; getprop ro.opengles.version"
sec "Storage: UFS, I/O scheduler, filesystems"
rd /sys/block/sda/queue/scheduler /sys/block/sda/queue/read_ahead_kb /sys/block/sda/queue/nr_requests /sys/block/sda/device/model
sh "mount" | grep -E ' / | /system | /vendor | /product | /data ' | awk '{print $3, $5}'
sec "Memory: zram, swap, swappiness, dirty ratios, LMK, memory engine"
rd /sys/block/zram0/comp_algorithm /sys/block/zram0/disksize /proc/sys/vm/swappiness /proc/sys/vm/dirty_ratio \
   /proc/sys/vm/dirty_background_ratio /proc/sys/vm/vfs_cache_pressure /proc/sys/vm/watermark_scale_factor /proc/swaps
sh "getprop | grep -iE 'ro.lmk|lmkd|persist.sys.memory|mi_mem|extm|memory_ext|miui.extm'" | head -20
sh "ls /proc/mi_mem_engine 2>&1 | head -2"
sec "Power HAL / perf / Doze"
sh "dumpsys deviceidle | grep -m3 -E 'mDeepEnabled|mLightEnabled|mState'"
sh "getprop | grep -iE 'vendor.perf|perf.hal|power.hal|init.svc.*(perf|power)'" | head -12
sec "Thermal"
sh "getprop | grep -iE 'init.svc.*thermal|thermal'" | head -10; sh "dumpsys thermalservice | head -12"
sec "Telephony / RIL / 5G NSA-SA / VoNR"
sh "getprop | grep -iE 'gsm.version|ril|radio.*(nr|sa|nsa|5g|vonr)|persist.vendor.radio.(enable|nr)'" | head -25
sh "dumpsys telephony.registry" | grep -m4 -oE 'mNrState=[^,]*|mNrFrequencyRange=[^,]*|getRilDataRadioTechnology=[^,]*|mIsUsingCarrierAggregation=[^,]*'
sec "Security: AVB, SELinux, integrity props"
sh "getenforce; getprop ro.boot.verifiedbootstate; getprop ro.boot.vbmeta.device_state; getprop ro.boot.flash.locked; getprop ro.boot.veritymode; getprop ro.build.tags; getprop ro.build.type"
sec "Binder / IPC"
sh "ls /dev/binderfs 2>&1 | head; getprop ro.binder.default_max_threads"
