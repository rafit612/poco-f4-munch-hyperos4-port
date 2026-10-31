# Phase 2 change list (prepared 2026-10-31, nothing applied)

Every change comes from a Phase 1 finding (`docs/hardware/subsystems/`). Rules from `ROM_OPTIMIZATION_PLAN.md`: one change per build, measured with `tools/baseline.sh`, a rollback for each, flash only with the owner's OK. Nothing here touches the phone before the owner's camera shots are analysed.

## A. Cleanup (no behaviour change expected)
| # | Change | Where | Evidence | Check |
|---|---|---|---|---|
| A1 | Remove the first computility block (`persist.sys.computility.cpulevel=6`, `gpulevel=6`, `version=2025`, lines 296-298) | `secure_build/payload_tele/product/etc/build.prop` | The same keys are set to 4 near line 407 under `#Blur Optimize` (deliberate); the phone ends on 4, so this only removes a dead duplicate | `getprop persist.sys.computility.cpulevel` still 4 |
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

## E. Security fix, its own build (C2, found 2026-10-31)
Restore the original signature and downgrade logic in `services.jar` (`PackageManagerServiceUtils`: `verifySignatures`, `compareSignatures`, `checkDowngrade` x3, `isDowngradePermitted`, `matchSignaturesCompat`, `matchSignatureInSystem`), taking the method bodies from the matching AOSP code (the Xiaomi 17 reference is a newer build, so only the logic, not the text, can be reused). Risk: any preinstalled app whose signing key differs from what the package database holds would stop installing or updating, and a wrong patch can stop the system booting, so: system partition build with a ready rollback, boot test, then check every priv-app (`tools/privcheck.py`), updates of Play Store, GMS and the camera/PhotoStage app, and an install of a differently signed APK that must now fail. `framework.jar` has the same kind of patch, worse: seven checks in `ApkSignatureSchemeV2Verifier`, `V3`, `V4` and `ApkSigningBlockUtils` call `com.xBuild.isOne()` (always true) where the original code calls `Signature.verify(...)` or `MessageDigest.isEqual(...)`; restore them too, and remove the `com.xBuild` helper once nothing uses it. **Dependency check done (read-only, 2026-10-31, `tools/re/ApkVerifyAll.java` over the 404 APKs of the shipped images):** 385 verify correctly; **12 fail** because they were modified after signing, so they only load because the checks are off: `MiuiSystemUI` (v1 signature references missing), `Settings`, `PowerKeeper`, `Joyose`, `MIUISystemUIPlugin`, `Phonesky` (Play Store), `HTMLViewer`, and the five overlays `AospFrameworkResOverlay`, `DevicesAndroidOverlay`, `DevicesOverlay`, `MiuiFrameworkTelephonyResOverlay`, `MiuiHomeLauncherResOverlay` (all `V3_SIG_APK_DIGEST_DID_NOT_VERIFY`). Restoring the checks everywhere would stop these from loading and the phone would not boot to a usable system. The camera (v15, debug key) and PhotoStage verify fine. `mi_ext` Dialer, Calendar, messaging, Contacts and the Mtk apps are 0-byte placeholders, and the GPU driver APK only failed in my checker (old JDK has no RSA-PSS).
**Design that keeps those apps working and closes the hole:** enforce the real checks for every APK that is not on a read-only system partition (anything installed, updated or sideloaded under `/data`, including updates of these same apps), and skip only for APKs located under `/system`, `/system_ext`, `/product`, `/vendor`, `/odm`, `/mi_ext`. Those partitions are part of the signed-and-hashed OS image (EROFS with dm-verity), so they're as trusted as the framework itself. In `services.jar` the cached certificates of these modified apps are still the original Xiaomi ones, so the restored `compareSignatures` and `verifySignatures` keep matching for them. Alternative, bigger: put back the stock versions of the 12 apps (loses the porter's patches) or re-sign them (needs the platform key we don't have). Needs the owner's decision and a flash; goes after the camera shots are analysed.

## F. Telecom fix: loudspeaker button sometimes does nothing (found 2026-10-31)
Cause and evidence: `docs/hardware/subsystems/CALL_SPEAKER_BUG.md`. Telecom keeps a stale cached communication device after another app used the speaker, then skips switching to the speaker. Fix: patch `isCurrentCommunicationDevice` in `/system/priv-app/Telecom/Telecom.apk` to read the real device from `AudioManager` (as the Xiaomi 17 reference does). System partition build with rollback; test with a WhatsApp speaker call followed by a phone call. Workaround until then: tap Speaker off and on.

## G. Dynamic Island check (owner request 2026-10-31)
Find out which Island features HyperOS 4 offers (call, music, timer, navigation, charging, recording, hotspot, delivery and others), which ones work on this phone, and whether the Island sits correctly around the front camera hole. Read-only first (settings, SystemUI resources, device feature flags, window frames, comparison with the Xiaomi 17 reference); fixes only after the findings. **Done in part (2026-10-31):** position is correct (centred on the camera hole within 1 px) and the code matches Xiaomi 17; only the charging island is seen working. The other island types need the apps to run (call, music, timer, navigation, recording, hotspot, delivery); the call island may not appear because the ROM uses Google Dialer. Results and checklist: `docs/hardware/subsystems/DYNAMIC_ISLAND.md`.

## D. Needs a kernel or HAL (Phase 3, not in a ROM build)
`bcl-soc` on (temperatures), uclamp and a newer power HAL (`mipowerhal` request), `migt` and the other Xiaomi modules, tracing and BPF. See `HYPEROS4_KERNEL_TARGET.md`.

## Order
A1, A2, A3 first (reading and one prop line), then one B item per build starting with B1, then C when the first B items are settled. Keep `out_tele_T20261031_v14` as rollback until a new release has run a few days.
