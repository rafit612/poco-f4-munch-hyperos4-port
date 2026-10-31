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
* **OIS checked:** in `cam_sensor.h`, `struct cam_ois_opcode` has `ois_get_data` only on psyche and apollo in rohman, but always in liyafe. The porter's kernel checks `len < 0x49` (73 bytes) and copies 32 opcode bytes from offset 41 in `cam_ois_driver_cmd`, so it includes the field, the same as liyafe. rohman's munch build would be 4 bytes short.

### 5. Xiaomi extras
liyafe's MIUI config enables Xiaomi code the vendor stack may use: `MILLET`, `MIGT`, `BINDER_OPT`, `PERF_HELPER`, `mi_reclaim`, `rtmm`, `board_sensor_temp`. The porter's kernel has these names; neither Lineage nor rohman has `mi_reclaim` or `rtmm`.

### 6. Android 17 needs BPF and tracing
Our v1 reached Android, then rebooted with `bpfloader-failed`. Tracing and BPF events are the known gap.
* Lineage's `lineage-24.0` branch is the closest on BPF, and its manifest targets Android 17.
* liyafe's main branch is not. Its `android15-lineage22-mod-ebpf` branch adds 55 BPF backports but is 12 commits behind, last changed 2025-07.
* Config, read as text: liyafe's `munch_defconfig` doesn't set `FTRACE` or `DEBUG_KERNEL`, and `FTRACE` only defaults on with `DEBUG_KERNEL`. So tracing has to be switched on explicitly, as in v3: `FTRACE`, event tracing, a probe-events option, then `BPF_EVENTS` follows. rohman sets `# CONFIG_FTRACE is not set`, which matches v1's failure.
* So the published prebuilt MIUI kernel will likely stop at `bpfloader` too. It could still show display, touch and camera probing in RAM only.
* Not run: a generated `.config`. The session's permission check blocked running `make` from the downloaded source, so the final values aren't confirmed. It happens at build time, with the owner's permission.
* uclamp: rohman sets `UCLAMP_TASK=y` and has no WALT. liyafe has WALT and no uclamp. Enabling uclamp next to WALT is a separate test, since the vendor scripts tune WALT.

### 7. Device tree against the live phone
The liyafe eBPF branch and rohman were compiled with `cpp` + `dtc`, merged with `fdtoverlay` (`kona-v2.1` + munch overlay) and compared with `phone_snapshot/live_fdt.dtb`.

| | liyafe | rohman |
|---|---:|---:|
| Live nodes missing from source (of 4605) | **0** | 65 |
| Thermal zones (live 91) | 91, same names | 91, same names |
| Reserved memory values | **Same** | `linux,cma` 128 MB vs live 32 MB; `qseecom_region` 32 MB vs live 20 MB |
| Panel node `l11r_38_08_0a` | Only panel size differs, plus a renumbered reference | Timings, commands, brightness differ; live `timing@2` missing |
| `cpu-map` | Same | Different, clusters missing |

* The panel size in the source, 155 x 70, is what liyafe's MIUI `build.sh` changes to 1546 x 695, exactly the live values. So the porter very likely used this tree or a close relative, with that script.
* rohman's mismatches are a plausible reason its device tree dropped to fastboot, but that isn't proven.
* 21 nodes are only in liyafe (audio packet, `spf_core_platform`, `glink`, `ufsice`) and 129 properties only in source. `chosen` and `memory` values come from the bootloader. Read the rest before the test.

## What this doesn't explain
Why v2 and v3 hung before the console is still unknown. A new base removes several suspects but doesn't prove the cause, so the first test keeps the v4 crash logging.

## Next, in order
1. With the owner's OK and after the camera shots: allow `make` from this source, generate the `.config` with MIUI and tracing options, and compare it with the porter's feature list.
2. Enable `bcl-soc` for temperatures, as its own step (`POWER_THERMAL_PERF.md`).
3. Build, then the RAM-only test (`ROADMAP` A1). A failed RAM boot returns to the installed kernel. Needs about 1.3 GB for the tree plus build space.

## Reproduce
`tools/kernel_compare/`: `symbol_coverage.py` (table 1), `vendor_paths.sh` (run on the phone as root, writes `/data/local/tmp/paths2.txt`), `path_audit.py` (table 2), `dt_compare.py` (table in section 7).
