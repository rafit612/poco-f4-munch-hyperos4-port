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
Zone names the binary knows but this kernel lacks include `xo-therm-usr` and `quiet-therm-usr`; the kernel has `xo-therm-adc` and `quiet_therm`. The binary's sensor list isn't the same as that source revision, so this is a strong lead, not proof.
**Still to confirm:** the exact missing zone, from the boot-time line `No thermal zone for sensor:`. The archived bugreport doesn't contain it. Capture `logcat` from the next boot.
**Fix options:** patch the expected name in the HAL binary, or provide the name from our kernel. Temperature reporting could activate thresholds that were silent, so test with care.

### 2. ADPF unavailable [Observed]
`Hint Session Support: false`, CPU and GPU headroom unsupported. The kernel has no uclamp symbols, and `android.hardware.power-service` exists. [Inferred] A kernel with uclamp is needed before hint sessions can work; still to check what the power HAL implements.

### 3. Kernel features [Observed, `/proc/kallsyms` by symbol name]
| Feature | State |
|---|---|
| uclamp | Not found (schedtune present) |
| Binder freezer | Not found (`cgroup_freezer` present) |
| BBR | Not found, TCP is cubic |
| MGLRU | Not found |
| PSI | Built, but `cgroup_disable=pressure` on the command line |
| THP | Absent |

### 4. Wasted work: the OS asks for services the old vendor lacks [Observed]
| Loop | Rate | Cause | Candidate fix |
|---|---|---|---|
| `/system_ext/bin/loc_sys_service` waits for `vendor.qti.gnss.ILocAidlGnss` | About 1/s, plus a failed `ctl.interface_start` each time | Links AIDL `vendor.qti.gnss-V8`; vendor only has HIDL `gnss@4.0` | Test stopping the service, then check GPS still works (vendor `loc_launcher` and `gnss_service` keep running) |
| Joyose `TcmReceiver` writes to `/dev/socket/tcm` | About 1.5/s, SELinux denied | `joyose_app` has no rule for `vendor_dpmtcm_socket` | Find out what Joyose wants; narrow rule or quiet the retry |
Their battery effect isn't measured yet. Measure screen-off wakeups before and after.

### 5. Other candidates, all unmeasured
* I/O scheduler `cfq`; `noop` and `deadline` available.
* `dalvik.vm.isa.arm64.variant=kryo300` on a Kryo 585 chip. Compare with official HyperOS 1 and Xiaomi 17.
* zram 8 GiB lz4 with writeback; zstd available.
* Cooling device `battery` was at level 2 while on the charger at 100 %. Check whether it affects charge speed.

## Next
1. Read `thermal-engine` and `mi_thermald` configs and the perf HAL boost tables.
2. Reverse `android.hardware.power-service` (which version, what it implements).
3. Framework side: how Joyose and computility levels drive performance.
4. Capture a boot log for the thermal zone name.
