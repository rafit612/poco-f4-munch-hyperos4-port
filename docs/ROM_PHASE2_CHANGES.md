# Phase 2 change list (prepared 2026-10-31, nothing applied)

Every change comes from a Phase 1 finding (`docs/hardware/subsystems/`). Rules from `ROM_OPTIMIZATION_PLAN.md`: one change per build, measured with `tools/baseline.sh`, a rollback for each, flash only with the owner's OK. Nothing here touches the phone before the owner's camera shots are analysed.

## A. Cleanup (no behaviour change expected)
| # | Change | Where | Evidence | Check |
|---|---|---|---|---|
| A1 | Remove the first computility block (`persist.sys.computility.cpulevel=6`, `gpulevel=6`, `version=2025`, lines 296-298) | `secure_build/payload_tele/product/etc/build.prop` | The same keys are set to 4 near line 407; the phone ends on 4 | `getprop persist.sys.computility.cpulevel` still 4 |
| A2 | Find who writes `persist.sys.mqs.gps.rtk=ON` and `supl.qxwz.com` | Not in `payload_tele` or any `.prop`/`.rc` of the base images, so a runtime writer (an app writes `persist.*`) | Phase 1 GNSS | Then block or reset it; confirm no connection to port 7275 |
| A3 | Find who sets `persist.vendor.wifi.interrupt_test_mode=true` | Not found in base images | Phase 1 Wi-Fi | Read-only search first |
| A4 | `dalvik.vm.background-dex2oat-threads` is 4 in `product/etc/build.prop` but 8 live: `system_ext/etc/init/init.miui.ext.rc` sets it at boot | Base `system_ext` | Phase 1 memory | Decide the value (4 proposed); an rc override needs a base-image change, not just `payload_tele` |

## B. Measured tuning (each one build, baseline before and after)
| # | Change | Gain to look for | Rollback |
|---|---|---|---|
| B1 | `vm.page-cluster` 3 to 0 | Lower swap-in latency; fewer `pswpin` stalls | Remove the rc line |
| B2 | zram `zstd` instead of `lz4` | More swap in the same RAM; compare app launch | Revert the rc line |
| B3 | Background compile threads to 4 (A4) | Small cores free during background compile | Revert prop |
| B4 | `sched_schedstats` 1 to 0 | Small constant CPU saving | Revert |
| B5 | Skia Vulkan test: `debug.hwui.renderer=skiavk` (non-persistent) | Fewer slow frames than the baseline 3.14 % janky, p90 18 ms | Reboot |
| B6 | Disable Joyose (`pm disable-user`) for one day | Idle wakeups and about 67 MB; game frame rate unchanged | Re-enable |
| B7 | `loc_sys_service` stopped | One wakeup per second saved; GPS must still fix outside | Re-enable |

## C. SELinux rules (one `product_sepolicy.cil` change, offline `secilc` check, new `.sha256`)
| Who | Wants | Seen |
|---|---|---:|
| `mediaserver` | read `vendor_default_prop` | 65 |
| `surfaceflinger` | read `vendor_frc_prop`; find `vendor.perfservice` | 4; 2 |
| `audioserver` | find `vendor_hal_perf_hwservice` | 2 |
| `system_server` | read `wifi_hal_prop` | 2 |
| `artd` | read `vendor_default_prop` | 4 |
Review each before adding: allowing a boost path can change heat and battery, so give those their own build or compare before and after.

## D. Needs a kernel or HAL (Phase 3, not in a ROM build)
`bcl-soc` on (temperatures), uclamp and a newer power HAL (`mipowerhal` request), `migt` and the other Xiaomi modules, tracing and BPF. See `HYPEROS4_KERNEL_TARGET.md`.

## Order
A1, A2, A3 first (reading and one prop line), then one B item per build starting with B1, then C when the first B items are settled. Keep `out_tele_T20261031_v14` as rollback until a new release has run a few days.
