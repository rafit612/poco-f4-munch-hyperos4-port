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
**Cause (corrected 2026-10-31; the earlier "missing zone name" theory was wrong):** the HAL logs `Temperature read error:1 for sensor soc` then `Sensor Temperature read failure` about once a second, so it starts and then fails at one read.
* `/sys/class/thermal/thermal_zone74` (`soc`) exists, but reading `temp` returns `Invalid argument`: no sensor is attached.
* The sensor is the `bcl-soc` node under `pm8150b`, and it has `status = "disabled"`. Driver `bcl_soc_peripheral` is built in but has no device.
* In the HAL source, a failed read ends the whole list and returns an error, so no temperature gets through.
* **Not a porter mistake:** the official HyperOS 1.0.9 device tree also has `bcl-soc` disabled, and the HAL binary is byte-identical to official (sha 05031fcf). So official most likely has the same failure, though that wasn't run. The names `xo-therm-usr` and `quiet-therm-usr` belong to the binary's lists for other chips.

**Fix candidate:** enable `bcl-soc` in the device tree, with the next kernel or a `dtbo` change.
* It reads battery percent from the `battery` supply, which works.
* The `soc` zone has a trip at 10 % that limits `cpu4`-`cpu7` one step (`low_limits_cap`). Keep that deliberately, or remove those four cooling maps so behaviour doesn't change.
* Temperatures reaching Android could wake framework thresholds that were silent. Test under load.
* Other sensors after `soc` in the HAL's list are unverified, because the read stops at the first failure. Five other zones also return `Invalid argument` (`modem-mmw3-usr`, `modem-mmw*-mod-usr`), so if any is in the kona list it would fail next.

### 2. ADPF unavailable: the power HAL is too old [Observed]
`Hint Session Support: false`, CPU and GPU headroom unsupported. `android.hardware.power-service` links `android.hardware.power-V1-ndk_platform`, and hint sessions only exist from `IPower` version 2. It's byte-identical to official HyperOS 1 (sha d6fba612), so this isn't a porter mistake. The kernel also has no uclamp.
**New (2026-10-31):** the framework also asks for `vendor.xiaomi.aidl.mipowerhal.IMiPowerHalAIDLService/default`, denied every 10 minutes, so HyperOS 4 expects a Xiaomi AIDL power HAL that this vendor lacks.
**Two things are needed:** a newer power HAL and a way to act on hints. LineageOS on this same chip uses `android.hardware.power-service.lineage-libperfmgr` with a `powerhint.json`, and the Qualcomm power source implements `createHintSession` (`PowerHintSession.cpp`). Open question: whether the vendor's SDK 30 VINTF, SELinux and perf stack accept it.

### 3. Kernel features [Observed, `/proc/kallsyms` by symbol name]
| Feature | State |
|---|---|
| uclamp | Off: only the 3 helper functions that always compile (`uclamp_task`, `uclamp_boosted`, `uclamp_latency_sensitive`), no `uclamp_rq` or `uclamp_se`. schedtune is used instead |
| App freezer | **Works** (corrected 2026-10-31): `binder_add_freeze_work` and `binder_ioctl_get_freezer_info` exist, `use_freezer=true`, `freeze_binder_enabled=true`, `dumpsys activity` reports `Apps frozen: 50` |
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
* **Thermal:** `mi_thermald` runs; `thermal-engine` exists but isn't running. Xiaomi's profiles (`thermal-normal`, `-mgame`, `-camera`, `-video`...) are encrypted on the phone; decrypted copies are in `audit/agents/perf/thermal_decrypted`. Only the `official` folder is usable: most files in `port` are empty, so that decrypt failed and says nothing about the phone.
  * **`mi_thermald` does limit the CPU** even though the Thermal API has no temperatures. `/data/vendor/thermal/thermal.dump` showed, on 2026-10-31: virtual sensor 36.3 C, `cpu4` capped at 1862400 kHz, `cpu7` at 1977600 kHz. That matches `official/thermal-normal.conf`, where 35 C is the first real cap (`cpu7` 2745600 down to 1977600). In a warm room this first step could come early, so measure it under load before any change.
  * `thermal.current.ini` = `local_danger` in `/vendor/etc`: no vendor program, library or init file checked refers to `thermal.current` or `local_danger`. It looks unused by the vendor. The framework and apps weren't checked. Low priority.
* **Performance:** `perfservice` + perf HAL 2.2 with 40 boost entries, `miperf`, `miui.powerkeeper.PerfEngService`, plus Android `performance_hint`, which is inactive.
* **Memory:** lmkd in minfree mode, swappiness 60, 8 GiB zram. Same design as official.
* The heap values match official HyperOS 1's product overrides.

## Joyose and computility levels [Observed, strings only; jadx isn't installed]
**Two level systems, both read from `MiuiBooster.jar` (decompiled 2026-10-31, `com.miui.performance`):**
* **Old device level** (`DeviceLevelUtils`): the platform name (`ro.board.platform` = `kona`) is looked up in lists inside the framework resources (high, middle and low CPU and GPU lists, plus a per-device whitelist by `ro.product.device` = `munch`), RAM gives 1 up to 4 GB, 2 up to 6 GB, 3 above. The result is stored in `Settings.System deviceLevelList`: on this phone **`v:1,c:3,g:3`, high for both CPU and GPU**, and RAM 8 GB is high too. So HyperOS 4 treats the phone as a high-end device and leaves its effects on.
* **Computility levels** (`ComputilityLevelUtils`): version 1 reads `persist.sys.computility.cpulevel` and `gpulevel`, valid 1 to 6, device level = the lower of the two; version 2 reads `persist.sys.computilityV2.*`, valid 1 to 4 with its own device level. Out-of-range values are rejected and logged. Read by SurfaceFlinger, SystemUI, AOD, Gallery, Theme Manager and AiAsstVision, mostly to pick visual effects.
* **Our values:** version 1 is 4 of 6 and version 2 is 4 of 4. The porter's `build.prop` first sets version 1 to 6, then later under the comment `#Blur Optimize` to 4, and the later line wins. So 4 is deliberate (a cheaper blur), and removing the first block (change A1 in `ROM_PHASE2_CHANGES.md`) only tidies a dead duplicate.
* **Still unknown:** the exact threshold at which each consumer switches an effect off. That is in each app, not in the booster library.

**Joyose doesn't read computility levels.** `com.xiaomi.joyose` (`SmartOpService`, about 67 MB) is a game and scene tuner, and much of what it names is missing on this phone:
| Names in Joyose | On this phone |
|---|---|
| `/proc/sys/walt/*`, `policy0/walt/target_loads` | Absent. This kernel uses `/proc/sys/kernel/sched_*` and `schedutil` |
| `/dev/migt_reset`, `/sys/module/mi_game`, `metis`, `turbo_sched` | Absent |
| `/proc/trace_package/*` | Absent |
| `/dev/cpuset/game`, `gamelite` | Absent |
| `bus_dcvs` | Absent |
Its assets have folders for newer chips (8635, 8735, 8750, 8850, 8950, 8975), and none for SM8250 or model `22021211RG`; `profiles/` and `default_cloud.json` aren't read yet.
So it may do little here. **Phase 2 test:** disable Joyose, then compare a game's frame rate, heat and idle wakeups. That would also stop its `TcmReceiver` denials. If it does nothing useful, that's about 67 MB back, with no SELinux change needed.

## Kernel base
Compared in [`KERNEL_BASE_COMPARISON.md`](KERNEL_BASE_COMPARISON.md). Decision: start from `liyafe1997/kernel_xiaomi_sm8250_mod` with its MIUI build and eBPF branch, and bring in LineageOS's CIP patches after it boots. `UCLAMP_TASK` exists in the sources compared but isn't enabled in the configs read.

## Next
1. Find where each computility consumer switches an effect (SystemUI, SurfaceFlinger, AOD). Tools work: JDK 17 at `~/.local/opt/jdk-17.0.20+8`, JADX library in `~/re_tools/jadx`, helper `tools/re/Decomp.java` (compile with javac 17).
2. Measure where thermal caps start under load, in a normal warm room.
3. Read the kona sensor list in the HAL binary, to see what follows `soc`.
