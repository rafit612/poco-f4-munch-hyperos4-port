# Memory and scheduling (Phase 1, 2026-10-31)

Read-only. Measured once on the phone: up 9 hours, on the charger, about 118 processes, normal daily apps. Not a load test.

## Stack
```
Apps, ART             heap limits, freezer, smart_gc
Framework             ActivityManager, Xiaomi memory services, lmkd (minfree levels)
Vendor scripts        init.qcom.post_boot.sh: WALT, core_ctl, cpu_boost, schedutil
Kernel 4.19.325       WALT + schedtune, cpusets, memcg, zram (lz4), mi_reclaim, rtmm_reclaim
Hardware              8 GB RAM, UFS, cores 4 + 3 + 1 (1.8 / 2.42 / 3.19 GHz)
```

## Memory health: good right now
| Item | Value | Reading |
|---|---|---|
| RAM | 7.6 GB total, 1.76 GB available | Fine |
| Swap | 4.0 GB of 8 GB in zram, using 1.5 GB of RAM | Ratio about 2.7 |
| Memory pressure (PSI) | `some` 0.06 %, `full` 0.00 % over 5 min | No stalls |
| I/O pressure | `some` 0.32 %, `full` 0.27 % | Low |
| CPU pressure | `some` about 1.8-2.1 % | Low |
| `oom_kill` | 0 | Good |
| Direct reclaim stalls | 9311 in 9 hours | Minor |
| Compaction | 632 stalls, 392 failed | Minor |
| Refaults | `workingset_refault` 26.4 M, `pgmajfault` 1.6 M | Worth comparing after tuning |
| Swap traffic | 3.7 M pages out, 2.0 M in | Moderate |
| Top memory | `system_server` 466 MB, Facebook 429 MB, SystemUI 309 MB, Photos 294 MB, GMS 202 MB | Expected |
| zram writeback | `/dev/block/dm-48` attached, `bd_stat` all 0 | Set up, never used here |

So memory tuning should be small and measured. There's no sign of a serious memory problem at this load.

## Scheduling and CPU
* Governor `schedutil` on all clusters. Minimum frequency on the small cores is 691 MHz, set by the vendor script: the 300-614 MHz steps are never used. Same as official.
* `core_ctl`: big cluster 2 to 3 cores, prime 0 to 1. Unloaded cores can sleep.
* Sleep states are on: `lpm_levels.sleep_disabled=N` at runtime, though the command line starts it at 1.
* Input boost: small core 0 at 1.34 GHz for 120 ms. Power key boosts all clusters for 400 ms.
* I/O: `cfq` on UFS, read-ahead 128 KB, `nr_requests` 32.
* Cpusets: top-app 0-7, foreground 0-2 and 4-7, background 0-2, system-background 0-3.
* `sched_lib_name=libunity.so, libfb.so` with mask 240: threads using these libraries are pushed to big cores. That includes Facebook apps, so it may cost battery. It's a Xiaomi or Qualcomm choice, not measured.

## Differences found
The vendor boot script differs from official in one line only (power key boost). These live values don't match that script, so something writes them later. No init file checked sets them, so the writer is probably a binary service. Not identified.

| Setting | Script | Live |
|---|---|---|
| `schedutil up_rate_limit_us` | 0 | 500 |
| `schedutil down_rate_limit_us` | 0 | 20000 |
| `sched_downmigrate` | 85 85 | 85 40 |
| `watermark_scale_factor` | 10 | 70 |

## Candidates, in order (Phase 2, one at a time, measured)
| # | Change | Why | Risk |
|---|---|---|---|
| 1 | `vm.page-cluster` 3 to 0 | The script sets 0 only if the product name is `kona`, and here it's `munch`, so it stays 3. Each swap-in reads 8 pages, which suits disks and not zram. Same as official | Low |
| 2 | zram `lz4` vs `zstd` | zstd compresses better but costs more CPU. Compare app launch and swap-in | Low |
| 3 | `dalvik.vm.background-dex2oat-threads` 8 to 4 | 8 threads share cpuset 0-3, so background compile can take all small cores | Low |
| 4 | `sched_schedstats` 1 to 0 | Scheduler statistics are on, a small constant cost. Check nothing needs them | Low |
| 5 | Find the writer of the values above | Don't override before knowing why it sets them | None, reading only |
| 6 | Measure `sched_lib_name` for Facebook apps | Possible battery cost | Medium |
| 7 | zram writeback | Attached and unused. Check why before removing or enabling it | Medium |

## Not worth doing
* Lowering `swappiness` by guesswork: 60 is deliberate in the script for `munch`.
* Changing `cfq` now: it's what Android's I/O priorities use on 4.19. Measure first.

## Next
1. Same baseline after a normal day and in a heavy game, to see pressure under real load.
2. Identify the writer of the live values.
