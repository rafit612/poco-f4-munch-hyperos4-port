# Roadmap — next kernel and 64-bit-only system

Written 2026-10-26, after release T20261026. Baseline = that release (`secure_build/out_tele` + `rom_extract/images`).

## Rules for this work
1. **One change per test build.** The first 64-bit attempt failed because five changes went in at once (below).
2. Every step: build → `errors 0` + `crossing block boundary 0` → flash (`flash_linux.sh update`, or `fastboot boot`
   for kernels) → the test list (end of this file) → benchmark (`tools/bench.sh`) → keep or roll back.
3. Rollback is always ready: the T20261026 images (`out_tele`, `rom_extract/images/boot.img`, `vendor_boot.img`).
4. Kernel tests start **RAM-only** (`fastboot boot`, nothing written to the phone).
5. A step goes into a public release only after a full test pass and a few days of daily use.

---

## Track A — Kernel

### Facts
- The phone runs the port's `4.19.325-zyndong-perf`. **4.19.325 is the final Linux 4.19 LTS release** (4.19 reached end
  of life in December 2024), so "newer kernel" means **our own build of 4.19.325** with better features and settings,
  not a 5.x kernel. munch's Qualcomm (kona) drivers, vendor HALs and DSP firmware exist only for 4.19; moving to 5.x
  would need a different vendor and is out of scope.
- Source: `rohmanurip/kernel_munch` (base) + KernelSU, clang r547379, full LTO; build tree `~/kernel_build/src`;
  packing `~/kernel_build/pack_kernel.sh`. History of v1–v4: [`secure_build/KERNEL.md`](../secure_build/KERNEL.md).
- v1 reached Android (failed on missing tracing for bpfloader); v2/v3 hung before any log; v4 = v3 + crash safety
  (panic on oops, soft-lockup panic, 1 MB pstore records), **built, never tested**.

### Goals (why a new kernel)
| Feature | Benefit | Status in port kernel |
|---|---|---|
| Audio as the vendor's own modules (official 4.19.157 layout) | "Hey Google" voice wake can come back without crashing the DSP | built in, DSP crash |
| uclamp | Android 17 task profiles can boost the foreground app properly (smoother, less power) | missing (schedtune only) |
| Binder freezer (cgroup freezer + binder freeze) | Cached apps really frozen → less background CPU/battery | missing (check if the source has the ACK backport) |
| FTRACE / tracepoints / BPF events | Required by Android 17 bpfloader, network stats, Perfetto | present in port kernel, needed in ours |
| zram writeback, MGLRU (if backported), BBR | Memory pressure and network quality | partly missing (no BBR) |
| Security: CFI/SCS where the toolchain allows, hardened usercopy, stack protector | Hardening | port kernel has most |
| KernelSU kept inactive (no manager shipped) | Root stays opt-in | same |

### Steps
| # | Step | Risk | Done when |
|---|---|---|---|
| A1 | `fastboot boot secure_build/kernel_v4/boot_v4.img` (RAM only) | none (a reboot returns to the installed kernel) | boots to Android, or leaves a pstore record |
| A2 | If A1 fails: boot the installed kernel, read `/sys/fs/pstore/` (needs temporary root), fix the crash, rebuild, repeat A1 | none | a v4.x boots to the home screen |
| A3 | Feature passes, one per build: tracing/BPF check → uclamp + task profiles → binder freezer → zram writeback → BBR | low (RAM-only each time) | each feature verified on the phone (`/proc/kallsyms`, `/sys`, `dumpsys activity` freezer state) |
| A4 | Audio modules: build the kernel without built-in audio, load the vendor's audio `.ko` set; compare with official HyperOS 1 (`stock_rom_1.0.9`) | medium (audio/DSP) | sound, calls, BT, wired, mic all OK; then retry Google's hotword engine in `sound_trigger_platform_info.xml` |
| A5 | Flash to slot A (`fastboot flash boot_a …`), daily use 3–7 days, full test list | medium | no reboots, battery and heat ≤ baseline |
| A6 | Release: new `boot.img` in the package; changelog; old kernel kept in the release notes as rollback | — | — |

---

## Track B — 64-bit-only system

### Why the first attempt failed (2026-10-24, `secure_build/payload_g64`, local only)
It changed five things at once and never got past boot. Three of them were later found to break the phone on their own:

| Change in that build | Later finding |
|---|---|
| Images built with stock mkfs.erofs 1.9.1 | Unreadable symlinks; one build lost `getprop`/`rm` and did not boot (fixed: patched mkfs + check) |
| Full Xiaomi 17 Global app swap (TeleService, SystemUI, Settings …) | Xiaomi 17 TeleService needs a framework class this port lacks → every call crashed |
| Stale `/system` ART boot image | Rebuilt in RAM each boot (fixed: removed) |
| 64-bit audio + codec2 launchers (`tools/hal64`), `ro.zygote=zygote64` | **Tested alone: worked** (audio, all hardware codecs) |
| 7 other 32-bit vendor programs removed (Miracast, virtual SIM, antenna DTX, OMX, CAS, 2 test tools) | Not tested alone |

So the plan is to change **only the architecture**, on top of the working T20261026 build, in small steps.

### Facts
- `ro.zygote=zygote64_32`; abilist `arm64-v8a,armeabi-v7a,armeabi`.
- The official kona vendor runs 9 programs as 32-bit. Two matter: `android.hardware.audio.service` and
  `vendor.qti.media.c2@1.0-service` → 64-bit replacements exist in `tools/hal64` (tested via a tmpfs module).
- Benefits of 64-bit only: no 32-bit zygote (estimated 100–150 MB RAM saved and a faster boot — to be measured), smaller images, newer apps only
  ship 64-bit anyway. Cost: 32-bit-only apps (old games, some banking/Indian/Chinese apps) stop working; Miracast and
  Xiaomi virtual SIM may be lost.

### Steps
| # | Step | Partition | Test focus |
|---|---|---|---|
| B1 | Inventory: every 32-bit program/library in vendor/odm/system/system_ext/product; preinstalled apps with only `lib/arm` | — | list in `audit/research/64bit_inventory.md` |
| B2 | 64-bit audio + codec2 launchers in **vendor** (32-bit zygote still on) | vendor | calls (earpiece/speaker/BT/wired), recording, 4K60 video, YouTube, offload playback |
| B3 | Replace or drop the other 7 32-bit vendor programs, one at a time (test Miracast/casting, virtual SIM, antenna, DRM/Widevine L1) | vendor | the feature each one serves |
| B4 | `ro.zygote=zygote64`, 64-bit-only abilist (no 32-bit app support); everything else unchanged | system/vendor props | boot, every preinstalled app, Play Store installs, banking apps |
| B5 | Remove 32-bit libraries and the 32-bit linker/runtime pieces that nothing uses | system, system_ext, vendor | boot + full test list; image sizes |
| B6 | Release as a separate "64-bit" build first (32-bit build stays available), then make it the default if no complaints | — | — |

Keep: `secure_build/payload_g64/` (transplant lists, prop list, privapp XML) and `tools/hal64/` as references.

---

## Order
1. **A1** (zero risk, one command) — tells us at once whether our kernel can be the base for the rest.
2. **B1 → B2** (vendor only, easy rollback).
3. A2–A4 and B3–B4 alternately, never two untested changes in one build.
4. Release when either track reaches its last step.

## Test list (every build)
- Boot time, no boot loop, `logcat -b crash` empty apart from known items, SELinux denials not higher than baseline.
- Calls on both SIMs (VoLTE where available), SMS, mobile data, Wi-Fi, hotspot, Wi-Fi calling.
- Speaker, earpiece, wired headset, Bluetooth audio (A2DP, LDAC/aptX) and Bluetooth call microphone.
- Camera photo/video (all lenses, 4K60), LMC, gallery playback; GPS; NFC; IR; vibration; sensors (`dumpsys sensorservice`).
- Charging, screen-off drain over 1 h, temperature under load (`tools/bench.sh`).
- Google sign-in, Play Store, a banking app.

## Kept on disk for this work (local, not in git)
`stock_rom_1.0.9/` (official kernel, vendor modules), `stock_rom_global17/` (64-bit reference),
`~/kernel_build/` (sources, toolchain), `secure_build/kernel_v1..v4/`, `secure_build/payload_g64/`, `tools/hal64/`,
`secure_build/out_sunday_plus/`, `secure_build/out_tele/`, `rom_extract/images/`, and the original port zip.
