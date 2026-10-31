# What HyperOS 4 expects from the kernel (2026-10-31)

Owner's goal: kernel and firmware work should serve HyperOS 4, so the ROM gets better optimised, not only boots.

## Method
Every `/sys`, `/proc` and `/dev` path was read from the phone's `system`, `system_ext` and `product` (frameworks, libraries, programs, app code, init files), and each was checked for existence: 16746 path-and-file rows, 3659 missing, 1114 different missing paths. Most are debug, tracing, other-chip or unrelated strings, so the list below is the part that matters. A name in a file doesn't prove it's used on this phone, or how much it helps.

Then each interface was searched for in the porter's kernel (`kallsyms`), `liyafe`, `rohman` and Xiaomi's published Xiaomi 17 source (`xiaomi17_family_kernel_source` on the pendrive, branch `popsicle-w-oss`). That release has no source for the Xiaomi performance features, only `mi_stack`, `mi_kernel_monitor`, `mi_trace` and similar debug drivers. The full Xiaomi 17 ROM images are on the pendrive too (`stock_rom_global17`, no kernel modules among them).

## Result
| Group | Interfaces | Used by | Source | Plan |
|---|---|---|---|---|
| **A. Available now in `liyafe`** | `migt` (frame boost), `millet` (freezer helper), `perf_helper`, `mi_reclaim`, `BINDER_OPT` | `libmigl`, `miui-services`, `perfservice` | Yes | Enable with MIUI config, one at a time. liyafe's MIGT is older: HyperOS 4 writes `/sys/module/migt/parameters/flt_*` and `frame_boost_enable`, so check that the names match |
| **B. Standard kernel features to add** | uclamp (`cpu.uclamp.*`), tracefs at `/sys/kernel/tracing`, cgroup `memory.reclaim`, binderfs `features/*` (`freeze_notification`, `extended_error`, `oneway_spam_detection`) | `init.rc`, `libbinder`, `atrace`, `libandroid_servers` | Upstream or Android common, needs backport | Start with tracing (needed anyway) and uclamp |
| **C. Already in `rohman`, reusable** | `kcompressd` (separate compression thread, in `mm/`) | `init.mtmr.rc` names a `kcompressd` switch | Yes | Candidate to port if swap traffic matters; test |
| **D. Xiaomi closed, no source found** | `mi_mtmr`, `mi_mem_engine`, `mi_memory_monitor`, `mi_mempool`, `metis`, `mist`, `speed_touch`, `xswapd`, `mfz`, `qpace`, `/dev/mi_display/disp_feature`, `/dev/mi_sw_sync`, `/dev/launch_boost`, `mi_dma_dio` | `init.rc`, `init.mtmr.rc`, `libmiperfturbo`, SurfaceFlinger | None | Can't port. Rewriting them is research work with uncertain gain. Userland already runs without them, apparently falling back. Confirm no retry loops or log spam |
| **E. Needs a much newer kernel or other hardware** | `/sys/fs/bpf/miui/*`, hypervisor tracing, MTK and Xiaomi 17 hardware paths | `libmmperf`, `atrace` | Depends on 6.x kernel features or hardware | Skip |
| **F. Device tree fix** | `bcl-soc` for temperatures | Thermal HAL | Yes | See `POWER_THERMAL_PERF.md` |

Group D isn't a promise of what's lost, and its effect hasn't been measured. These features are Xiaomi's newest memory and frame tuning, written for its 6.x kernels.

## Firmware
Firmware can't be rebuilt for HyperOS 4. It's closed and signed: modem, ADSP, Wi-Fi, Bluetooth and TrustZone images only load if signed for this chip, and POCO F4's final official set is already on the phone. Xiaomi 17's firmware is for SM8850 and can't run on SM8250. What's possible is what the vendor stack around it does:
* configuration files (carrier MBN selection, audio and sensor configs), read only until a clear benefit shows;
* shims between the HyperOS 4 framework and the Android 11 vendor services;
* newer open-source HALs where the old vendor ones limit features, such as the power HAL.
**Never write modem, EFS or persist.**

## Order for the HyperOS 4 kernel
1. Base: `liyafe` MIUI + eBPF branch + tracing. It must boot and equal today's kernel first.
2. `bcl-soc` on: temperatures reach Android.
3. Group A one at a time, starting with `migt`, measured in a game.
4. uclamp + newer power HAL: ADPF for apps and games.
5. Lineage CIP security patches.
6. `kcompressd` and the rest of group B only if measurements justify them.
