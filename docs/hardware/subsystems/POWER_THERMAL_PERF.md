# Power, thermal and performance (Phase 1, first pass, 2026-10-31)

Read-only analysis. [Observed] = read from the phone or binary. [Source] = open-source code. [Inferred] = reasoning, not proven.

## Stack
```
Apps / games          PowerManager hints, Thermal API, ADPF
Framework             thermalservice, performance_hint, Joyose, Xiaomi computility level 4
HALs (vendor SDK 30)  thermal@2.0-service.qti, android.hardware.power-service, perf@2.2, miperf@1.0
Daemons               thermal-engine, mi_thermald, perfservice
Kernel 4.19.325       schedtune (no uclamp), cgroup freezer (no binder freeze), 93 thermal zones
Hardware              SM8250 (soc_id 356), Adreno 650 at 670 MHz
```

## Baseline (screen on, home screen, on charger, 120 s)
CPU busy 4.6 %. Top: `system_server` 5.1 % of a core, display thread `crtc_event` 3.2 %, launcher 3.0 %, SurfaceFlinger 2.1 %. No runaway process, and `hwservicemanager` isn't listed. Screen-off drain not measured (needs the phone off USB).

## Findings

### 1. Thermal HAL returns no temperatures [Observed + Source]
Symptom: `dumpsys thermalservice` lists cooling devices but no temperatures, so Android's Thermal API has no data.
Binary `android.hardware.thermal@2.0-service.qti` is built from `vendor/qcom/opensource/thermal-hal` ([LineageOS copy](https://github.com/LineageOS/android_hardware_qcom_thermal)). In the `lineage-20.0` revision of that code, `ThermalCommon::initThermalZones` returns -1 if **any** configured sensor has no thermal zone; `ThermalUtils` then leaves `is_sensor_init=false` and `readTemperatures` returns nothing. Cooling devices are set up separately, which matches the symptom.
The HAL binary is byte-identical to official HyperOS 1 (sha 05031fcf), so the HAL isn't at fault: the mismatch is on the porter's kernel side. Zone names the binary knows but this kernel lacks include `xo-therm-usr` and `quiet-therm-usr`; the kernel has `xo-therm-adc` and `quiet_therm`. The binary's sensor list isn't the same as that source revision, so this is a strong lead, not proof.
**Still to confirm:** the exact missing zone, from the boot-time line `No thermal zone for sensor:`. The archived bugreport doesn't contain it. Capture `logcat` from the next boot.
**Fix options:** patch the expected name in the HAL binary, or provide the name from our kernel. Temperature reporting could activate thresholds that were silent, so test with care.

### 2. ADPF unavailable: the power HAL is too old [Observed]
`Hint Session Support: false`, CPU and GPU headroom unsupported. `android.hardware.power-service` links `android.hardware.power-V1-ndk_platform`, and hint sessions only exist from `IPower` version 2. It's byte-identical to official HyperOS 1 (sha d6fba612), so this isn't a porter mistake. The kernel also has no uclamp.
**Two things are needed:** a newer power HAL and a way to act on hints. LineageOS on this same chip uses `android.hardware.power-service.lineage-libperfmgr` with a `powerhint.json`, and the Qualcomm power source implements `createHintSession` (`PowerHintSession.cpp`). Open question: whether the vendor's SDK 30 VINTF, SELinux and perf stack accept it.

### 3. Kernel features [Observed, `/proc/kallsyms` by symbol name]
| Feature | State |
|---|---|
| uclamp | Not found (schedtune present) |
| Binder freezer | Not found (`cgroup_freezer` present) |
| BBR | Not found, TCP is cubic |
| MGLRU | Not found |
| PSI | System-wide `/proc/pressure/memory` works; `cgroup_disable=pressure` is on the command line. lmkd uses minfree levels, same as official |
| THP | Absent |

### 4. Wasted work: the OS asks for services the old vendor lacks [Observed]
| Loop | Rate | Cause | Candidate fix |
|---|---|---|---|
| `/system_ext/bin/loc_sys_service` waits for `vendor.qti.gnss.ILocAidlGnss` | About 1/s, plus a failed `ctl.interface_start` each time | Links AIDL `vendor.qti.gnss-V8`; vendor only has HIDL `gnss@4.0` | Test stopping the service, then check GPS still works (vendor `loc_launcher` and `gnss_service` keep running) |
| `TcmReceiver` thread writes to `/dev/socket/tcm` | About 1.5/s denied, only for `joyose_app` | Thread comes from Qualcomm `tcmclient.jar` (DPM), loaded in the Java runtime: seen in 7 processes, including ordinary apps. `dpmd` is running. Joyose's own domain has no rule for `vendor_dpmtcm_socket` | Narrow SELinux rule for that one socket (needs the offline policy check), then compare |
Their battery effect isn't measured yet. Measure screen-off wakeups before and after.

### 5. Other candidates, all unmeasured
* I/O scheduler `cfq`; `noop` and `deadline` available.
* `dalvik.vm.isa.arm64.variant=kryo300` comes from the official vendor `default.prop`. Low priority: same as official, gain uncertain.
* zram 8 GiB lz4 with writeback; zstd available.
* Cooling device `battery` was at level 2 while on the charger at 100 %. Check whether it affects charge speed.

### 6. Who controls what [Observed]
* **Thermal:** `mi_thermald` runs; `thermal-engine` exists but isn't running. Xiaomi's profiles (`thermal-normal`, `-mgame`, `-camera`, `-video`...) are encrypted on the phone; decrypted copies are in `audit/agents/perf/thermal_decrypted`. Current profile: `local_danger` in `thermal.current.ini`, not yet understood.
* **Performance:** `perfservice` + perf HAL 2.2 with 40 boost entries, `miperf`, `miui.powerkeeper.PerfEngService`, plus Android `performance_hint`, which is inactive.
* **Memory:** lmkd in minfree mode, swappiness 60, 8 GiB zram. Same design as official.
* The heap values match official HyperOS 1's product overrides.

## A better kernel base: LineageOS [Source]
[`LineageOS/android_kernel_xiaomi_sm8250`](https://github.com/LineageOS/android_kernel_xiaomi_sm8250) is what LineageOS builds for munch (device config `vendor/xiaomi/munch.config`).
* Also 4.19.325, branches up to `lineage-24.0`; the `lineage-24.0` manifest is on `android-17.0.0_r1`. Device tree `android_device_xiaomi_munch` stops at `lineage-23.2`.
* Latest commits include `v4.19.325-cip136` (September 2026), so it still gets 4.19 security backports through CIP.
* Source has `UCLAMP_TASK` and `BINDER_FREEZE`, plus CFI and shadow call stack in its defconfig. UCLAMP wasn't set in the config files checked, so it would need enabling and testing.
* **Main risk:** it's built for AOSP-style ROMs. Notes from another munch kernel project say the AOSP display driver doesn't display properly on MIUI/HyperOS, and the vendor stack here expects Xiaomi's. Untested. Audio and camera may also differ.

## Next
1. Compare the Lineage kernel with `rohmanurip/kernel_munch` and the porter's symbols: display, camera, audio, Xiaomi-specific drivers.
2. Read `thermal_decrypted` and what `local_danger` means.
3. Framework side: how Joyose and computility levels drive performance.
4. Capture a boot log for the thermal zone name.
