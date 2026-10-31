# Kernel base comparison (Phase 1, 2026-10-31)

Question: which source should the next custom kernel start from? Read-only work; nothing was built or changed on the phone.

Reference: the porter's running kernel (`4.19.325-zyndong-perf-g7e817c4ca270`), the only kernel known to work with this ROM. Its source was not found.

| Tree | Source | State |
|---|---|---|
| Lineage | `LineageOS/android_kernel_xiaomi_sm8250`, branch `lineage-24.0`, commit `6b34d24` | 4.19.325 `-cip136`, `-st20` |
| liyafe | `liyafe1997/kernel_xiaomi_sm8250_mod`, branch `android15-lineage22-mod`, commit `3ebb633` | 4.19.325, no CIP tag. Fork of Lineage 22.1 with a MIUI build. Prebuilt MIUI munch kernels up to 2026-07-15 |
| rohman | `rohmanurip/kernel_munch`, our v1-v4 base, `~/kernel_build/src` | 4.19.325, no CIP tag |

## Decision
**Stop using rohman as the base. Start from liyafe's MIUI build, the branch with the eBPF backports, and bring in Lineage's CIP security patches after it boots.**
This is a source-level decision. No candidate has been booted yet.

## Evidence

### 1. Functions in the porter's kernel that each tree lacks
Lower is better. Function names come from `kallsyms`. Camera and audio were checked against the tree's own driver folder, the others against the whole tree.

| Subsystem | Porter's functions | Lineage | liyafe | rohman |
|---|---|---:|---:|---:|
| Camera (`cam_`) | 1278 | 78 | 3 | 4 |
| Display (`dsi_`, `sde_`, `mi_dsi`, `dp_`) | 2478 | 30 | 7 | 11 |
| Audio | 1298 | 37 | 34 | 34 |
| BPF | 1097 | **224** | 761 | 762 |
| GPU (`kgsl_`, `adreno_`) | 637 | 3 | 3 | 21 |
| Scheduler (WALT, `sched_`, `sugov_`) | 155 | 0 | 0 | **53** |
| Memory (`mi_reclaim`, `rtmm`, zram) | 82 | 14 | 3 | 22 |
| Binder | 108 | 24 | 19 | 17 |
| Wi-Fi | 3739 | 0 | 0 | 0 |
| Charging | 420 | 6 | 6 | 6 |
| Touch, haptics | 472 | 0 | 0 | 0 |
| Thermal | 70 | 9 | 0 | 7 |

Limits of this test: a name found in a tree may be disabled by config, or only referenced, and the behaviour may differ. A few misses are false, such as `cam_cc_kona_*`, which is a clock driver outside the camera folder, and most of the 34 audio misses, which are USB gadget functions (`audio_pcm_*`, `audio_source_*`). It ranks the trees; it doesn't prove that one boots.

### 2. Paths the vendor uses that exist on this phone
All `/sys` and `/proc` paths in vendor binaries, HAL libraries and init files were read on the phone, and those that exist were kept: 268 different leaf names. Then each tree was searched for the name.

| | Lineage | liyafe | rohman |
|---|---:|---:|---:|
| Names not found | 30 | 19 | 45 |

* **rohman** lacks scheduler and governor tunables that the vendor boot scripts write, such as `sched_walt_rotate_big_tasks`, `sched_window_stats_policy`, `hispeed_freq`, `up_rate_limit_us`. It has no WALT, while the vendor stack expects it.
* **Lineage** lacks `disp_param`, `disp_pcc`, `wp_info`, `oled_pmic_id` and `/sys/class/thermal/thermal_message/` entries that `mi_thermald` uses.
* **All three** miss some names that are probably built by macros (`kernel_max`, `rps_cpus`, `usbpd0`) or that the porter or vendor added (`protect_memcg_*`, `verify_digest`). Each needs checking before a test.

### 3. Display: the risk with Lineage is real and has a known fix
`vendor.qti.hardware.display.composer-service` itself uses `disp_param`, `disp_pcc` and `wp_info`. `displayfeature` and `lights.kona` use `brightness_clone`, `disp_param`, `panel_info` and more. Plain Lineage has none of the `drm_sysfs` part.
liyafe solves this with one switch: `CONFIG_XIAOMI_MIUI` builds `techpack/display/msm-miui` and Xiaomi's `drm_sysfs` nodes. Its `build.sh` also adjusts panel files, and its README warns that the AOSP variant doesn't display on MIUI/HyperOS.
This phone's panel, `l11r_38_08_0a_dsc_cmd`, is in all three trees. `build.sh` changes that file's panel dimensions (`<155>` to `<1546>`, `<70>` to `<695>`). The replacement panel still reports this name, but its timing is unverified: **do not change refresh rates**.

### 4. Camera interface
The vendor camera HAL talks to the kernel through `cam_*.h`.
* liyafe's headers match rohman's in every file but `cam_sensor.h`.
* Lineage's `camera-xiaomi` is older: it lacks `CAM_REQ_MGR_REQUEST_DUMP` and `cam_req_mgr_custom_msg`, and it has 78 missing functions.
* **Check before testing:** in `cam_sensor.h`, `struct cam_ois_opcode` has `ois_get_data` only on psyche and apollo in rohman, but always in liyafe. The struct is packed, so a size mismatch with the vendor HAL could break OIS firmware loading on munch. Read which size the HAL uses.

### 5. Xiaomi extras
liyafe's MIUI config enables Xiaomi code the vendor stack may use: `MILLET`, `MIGT`, `BINDER_OPT`, `PERF_HELPER`, `mi_reclaim`, `rtmm`, `board_sensor_temp`. The porter's kernel has these names; neither Lineage nor rohman has `mi_reclaim` or `rtmm`.

### 6. Android 17 needs BPF and tracing
Our v1 reached Android, then rebooted with `bpfloader-failed`. Tracing and BPF events are the known gap.
* Lineage's `lineage-24.0` branch is the closest on BPF, and its manifest targets Android 17.
* liyafe's main branch is not. Its `android15-lineage22-mod-ebpf` branch adds 55 BPF backports but is 12 commits behind, last changed 2025-07.
* None of the configs read so far sets `FTRACE`, `TRACEPOINTS` or `BPF_EVENTS` by name. Their real values need a generated `.config`.
* So the published prebuilt MIUI kernel will likely stop at `bpfloader` too. It could still show display, touch and camera probing in RAM only.

## What this doesn't explain
Why v2 and v3 hung before the console is still unknown. "Porter's kernel + rohman's device tree" also dropped to fastboot. A new base doesn't fix this by itself, so the first test keeps the v4 crash logging.

## Next, in order (no phone change)
1. Compare liyafe's munch device tree with `phone_snapshot/live_fdt.dtb`.
2. Read which `cam_ois_opcode` size the vendor HAL uses.
3. Generate a `.config` for the eBPF branch with MIUI options and compare it with the porter's feature list. Needs a disk location for the tree, about 1.3 GB.
4. Then, with the owner's OK and after the camera shots: build, then the RAM-only test (`ROADMAP` A1). A failed RAM boot returns to the installed kernel.

## Reproduce
`tools/kernel_compare/`: `symbol_coverage.py` (table 1), `vendor_paths.sh` (run on the phone as root, writes `/data/local/tmp/paths2.txt`), `path_audit.py` (table 2).
