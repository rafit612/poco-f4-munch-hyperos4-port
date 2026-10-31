# POCO F4 full-ROM optimisation plan (hardware, firmware, kernel, OS)

Written 2026-10-31. Goal: get the best real performance, battery and feature set this phone can give on HyperOS 4 / Android 17,
backed by reverse engineering and measurements. This extends `ROADMAP.md` (kernel + 64-bit), which stays valid.
Nothing here has been changed on the phone yet.

## 1. What limits the work

| Fact | Consequence |
|---|---|
| Android 17 (SDK 37) runs on an Android 11-frozen vendor (SDK 30, `ro.board.first_api_level=30`) | New HyperOS 4 hardware interfaces have no vendor service behind them. Each one needs a shim, a fallback or a clean disable |
| Firmware is the final official set (modem, ADSP, Wi-Fi, BT, TrustZone); no newer version exists | Firmware work means reading and understanding, plus config files. **Never write modem, EFS or persist** |
| Kernel 4.19.325 is the final 4.19 release; the kona drivers exist only for 4.19 | "New kernel" means a better 4.19 build, not 5.x |
| This phone has a replacement 60 Hz panel and a dead fingerprint flex (both hardware) | Do not "unlock" 120 Hz. In-display fingerprint can't work without a repair |
| The USB link on this laptop drops during long sessions (again on 2026-10-31) | Run long phone jobs on the phone itself. Check cable and port before any flash |
| Laptop free space is low; a product build needs about 14 GB, and `~/kernel_build` (8.6 GB) must stay | Free space before building anything |

**Not reachable on this hardware:** on-device Gemini Nano (AICore needs SM8850), pKVM/virtualisation, eSIM, UWB, StrongBox, LE Audio on this Bluetooth chip.

## 2. Existing knowledge

* Hardware docs on the pendrive `hardware_docs/`: 1152 devices mapped device -> driver -> source -> Kconfig -> device tree, 57 sensors, SoC and OS architecture, 25 driver source archives. **Not in the repo.**
* Audits in `audit/`: hardware health, security, firmware and drivers, ROM architecture, HyperOS 4 features and tuning, performance.
* Camera stack: fully mapped, `docs/camera/`.
* Whole-ROM graph, new: `docs/rom_map/graphify-out/graph.html` (local only, 71 files).

### What was never reverse engineered
| Area | State | Why it matters |
|---|---|---|
| Framework (`services.jar`, `framework.jar`, `miui-services`) | Only read to fix single bugs | Signature bypass, performance scheduling, what HyperOS 4 expects from the vendor |
| Xiaomi performance stack (perf HAL, `mi_thermald`, Joyose, computility levels) | Props only | Biggest direct effect on smoothness and heat |
| Kernel: porter's binary vs our source | Symbol names only | Why our v2 and v3 hung; what the porter changed |
| HALs per subsystem except camera | Lists only | Sensors, GNSS, touch, thermal, power |
| Sensor DSP (SLPI/SEE) | Inventory only | Closed firmware: config level only |
| 64-bit: all 32-bit programs and libraries | The 9 vendor programs are known; libraries are not | `ROADMAP` step B1 was never done |

## 3. Measured on the phone today

| Item | Result | Note |
|---|---|---|
| `hwservicemanager` CPU drain (58 % of a core on 26 Oct) | Not in today's top list | Looks gone; confirm in the baseline |
| `vendor.qti.gnss.ILocAidlGnss` | Waited for 897 times in the log | Client looks for a service that never comes: wasted wakeups |
| SettingsProvider `Permission denial` | 526 repeats | Some app or service retries a forbidden write |
| Bluetooth wake lock errors | 331 repeats | Vendor file permission or path |
| Wi-Fi `Fail to get mlo info` | 295 repeats | New framework call on an old vendor |
| Thermal HAL | Connected; earlier audit: no temperatures | Blocks Android's thermal API |
| ADPF | Hint sessions unsupported; CPU/GPU headroom unsupported | Needs kernel uclamp + a power HAL; games and apps get no performance hints |
| I/O scheduler `cfq`, TCP `cubic` (no BBR) | | Candidates, measure first |
| `dalvik.vm.isa.arm64.variant=kryo300` | SD870 has Cortex-A77/A55-class cores | Check against official HyperOS 1, test |
| zram 8 GiB lz4 with writeback | zstd also available | Candidate, measure |
| 32-bit | 9 vendor programs; 0 apps reported a 32-bit ABI of 99 user apps + system | 64-bit-only costs less than feared; recheck in B1 |
| Max charging current | HAL reports 1.1 A on this USB port | Inconclusive here: retest on the real charger |
| Root | Works over `su` today, though `FIX_PLAN` says removed | Decide at the end whether it stays |

## 4. Phases

Each change: one per build, measured, with a rollback. Flashes only with the owner's OK.

### Phase 0: Foundation (no phone changes)
1. Free laptop space; test cable and port.
2. Move own hardware docs into the repo under `docs/hardware/`, without binaries, datasheets or vendor files.
3. Baseline script extending `tools/bench.sh`: idle CPU, screen-off drain per hour, boot time, app launch, jank (`gfxinfo`), memory, thermal under load, top log spam. Every later step is judged by it.
4. Refresh the old audits' status: mark each finding fixed, open or wrong. Security items C1-C3 and H1-H4 first; several may be out of date.

### Phase 1: Reverse engineering and architecture (read-only)
One document per subsystem, same template: **hardware -> kernel driver -> HAL -> framework -> app -> feature status -> what can be improved.** Tools: JADX, dexlib2, Ghidra headless, `llvm-objdump`, `dtc`, `kallsyms_dump.py`, live `lshal`/`dumpsys`, plus LineageOS munch sources as an open reference. Graph updated after each.

Order, by gain: power/thermal/perf -> memory and scheduling -> display and touch -> Wi-Fi and modem -> audio -> GNSS -> sensors -> charging -> storage -> security.

Also: framework map of each HyperOS 4 service with no vendor counterpart (this produces the feature matrix in Phase 5), and porter's kernel vs our source.

### Phase 2: Cleanup and tuning (low risk, app/prop/rc level)
Stop the log spam found above, fix what the framework waits for, then test tuning candidates one by one: scheduler, dalvik variant, zram, heap, background limits. Keep only what the baseline shows as better.

### Phase 3: Kernel (`ROADMAP` track A)
A1 RAM-only test of v4 -> read pstore -> fix. Before more guessing, compare with a maintained base: [`liyafe1997/kernel_xiaomi_sm8250_mod`](https://newreleases.io/project/github/liyafe1997/kernel_xiaomi_sm8250_mod/release/20250403) has MIUI/HyperOS builds and munch fixes, but its notes cover Android 11-14, so Android 17 is unproven.
Then one feature at a time: uclamp -> binder freezer -> zram -> BBR -> audio modules ("Hey Google"). uclamp is what opens the door to ADPF. Everything RAM-only first, and flashing needs a few days of daily use.

### Phase 4: 64-bit only (`ROADMAP` track B)
B1 inventory -> audio + codec2 launchers in vendor -> the other 7 programs one at a time -> `zygote64` -> remove libraries. Expected gain is an estimated 100-150 MB of RAM and a faster boot, to be measured. It loses Miracast and Xiaomi virtual SIM unless replaced.

### Phase 5: Full HyperOS 4 / Android 17 features
Feature matrix, one row per feature: works / works with a shim / needs a kernel change / impossible on this hardware, with evidence. Fill it from the Phase 1 map and Xiaomi 17 Global (pendrive), and add features in order of daily use. Known candidates: Soft Light Glass effects, stacked widgets, grouped notifications, lock-screen island, ECH and local-network protection (software), rich haptics, Google mainline modules (all 29 as one swap only).

### Phase 6: Firmware (understanding first)
Read firmware versions, carrier MBN selection and DSP configs. Change config only where a clear benefit shows, such as the Banglalink VoLTE registration. No modem, EFS or persist writes, and no flashing of firmware from other devices.

### Phase 7: Security and release
Decide on the signature bypass, root and verified boot with evidence from Phase 0-1; new public package with a privacy scan; docs and graph finished.

## 5. Order and timing with the camera week
Phases 0-1 are laptop and read-only work, so they can run during the owner's week of shooting. Phase 2 onward changes the phone and starts **after** the camera shots are analysed, so results stay clean. Exception: the RAM-only kernel test is safe earlier if wanted.

## 6. Research limits
* Session transcripts could not be read (blocked by the session's permission check). Written history was used instead.
* Web sources on HyperOS 4 are mostly news and leaks, and disagree on rollout. Local comparison with Xiaomi 17 Global is more reliable.
* Sources: [Android 17 features](https://developer.android.com/about/versions/17/features), [Android 17 behaviour changes](https://developer.android.com/about/versions/17/behavior-changes-17?hl=en), [HyperOS 4 features](https://propakistani.pk/2026/09/26/5-biggest-features-of-hyperos-4-xiaomi-users-should-know-about/amp/), [HyperOS 4 overview](https://droid.tools/xiaomi-hyperos-4-update-devices-release), [LineageOS munch](https://wiki.lineageos.org/devices/munch/variant1/), [KernelSU device list](https://kernelsu.org/guide/unofficially-support-devices.html).
