# Status of the old audit findings, rechecked on the running ROM (2026-10-31, tag T20261031b)

Sources: `audit/agents/security/SECURITY_REPORT.md`, `audit/agents/hardware/HARDWARE_REPORT.md` (both from before most fixes). Read live from the phone.

## Security
| ID | Finding | Now | Evidence |
|---|---|---|---|
| C1 | Data not encrypted | **Fixed** | `ro.crypto.type=file`, `/data` mounted with `inlinecrypt`, metadata encryption files present |
| C2 | Signature/downgrade bypass in the framework | **Open, confirmed by code (2026-10-31)** | `services.jar`, class `com.android.server.pm.PackageManagerServiceUtils` (decompiled with JADX, compared with the Xiaomi 17 reference): `verifySignatures` returns `true` without checking, `compareSignatures` returns 0 (match), the three `checkDowngrade` methods are empty, `isDowngradePermitted` returns `true`, `matchSignaturesCompat` and `matchSignatureInSystem` return `false`. Effect: an APK with the same package name signed by anyone can replace an installed app and keep its data, and downgrades are allowed. It still takes the user (or an installer) to install the APK. **Worse in `framework.jar` (checked 2026-10-31):** the cryptographic APK verification itself is disabled. In `ApkSignatureSchemeV2Verifier`, `V3`, `V4` and `ApkSigningBlockUtils` seven checks (4 `Signature.verify` results, 2 content-digest comparisons, the APK-verity digest) were replaced by calls to an injected helper class `com.xBuild` whose `isOne()` always returns true; the reference does `sig.verify(...)` and `MessageDigest.isEqual(...)` at the same places. So a tampered APK is accepted as validly signed, and the certificate it claims is never proven, which defeats signature-permission and shared-user checks too. Still needs a person to install the APK. More stubs found in `services.jar` (a scan of methods that are tiny in the port but long in the reference, 14 hits): `doesSignatureMatchForPermissions` always true, `assertMinSignatureSchemeIsValid` empty (v1-only signatures accepted), both key-set upgrade checks always true, and the install-time package verifier (`VerifyingSession.isVerificationEnabled`, `isAdbVerificationEnabled`, `sendApkVerificationRequest`) switched off, so Play Protect's check before install never runs. Twelve preinstalled apps were modified after signing and fail real verification, so a fix has to exempt read-only system partitions (list and design in `ROM_PHASE2_CHANGES.md` section E). Not yet checked: the permission-grant path |
| C3 | Unlocked bootloader, status hidden | **Open** | Real state `orange`, while `ro.boot.flash.locked=1` and `vbmeta.device_state=locked` are spoofed |
| H1 | Kaorios attestation hook | **Disabled** | Package absent; framework code still to check |
| H2 | Kernel root | **Open, deliberate for now** | `su` works (`u:r:ksu:s0`), ReSukiSU manager installed. Needed for this research; decide in Phase 7 |
| H3 | Privapp allowlist off | **Fixed** | `ro.control_privapp_permissions=enforce` |
| H4 | Old patch base | **Cannot be fixed** | Vendor SPL 2025-04-01, final official; kernel 4.19 end of life |
| M1 | FRP removed | **Fixed** | `ro.frp.pst` set |
| M2 | `vendor_security` kill switch | **Fixed** | Service and binary gone |
| M3 | Permissive SELinux domains | **Fixed** | No `typepermissive` in vendor policy, enforcing |
| M4 | Spoofed integrity props | **Open** | See C3; `ro.is_ever_orange=0` |
| M5 | ADB open | **Fixed** | `ro.adb.secure=1`; debugging is on by choice |

## Hardware report
| # | Finding | Now |
|---|---|---|
| 1 | `hwservicemanager` about 55 % of a core | **Gone** in the 2026-10-31 baseline |
| 2 | Fingerprint dead | **Hardware**: `persist.vendor.sys.fp.vendor=none`, flex damaged |
| 3 | Display 60 Hz | **Correct**: replacement panel is 60 Hz (`FIX_PLAN.md`). Do not change |
| 4 | Thermal HAL no temperatures, ADPF off | **Open, cause found**: `bcl-soc` is disabled in the device tree (official too), so the HAL's `soc` read fails; ADPF needs a newer power HAL and uclamp, and the framework also asks for a Xiaomi `mipowerhal` the vendor lacks: `subsystems/POWER_THERMAL_PERF.md` |
| 5 | GNSS raw measurements missing | Open. Services run; `loc_sys_service` still loops once a second; no outdoor fix test yet: `subsystems/GNSS_SENSORS_POWER_STORAGE_SECURITY.md` |
| 6 | `traced`, `vendor_security` restarting | **Fixed**: `traced` stopped on purpose, `vendor_security` removed |
| 7-9, 13, 16 | Flags and limits (virtualisation flag, LE Audio, Camera2 limits, haptics, spatializer) | LE Audio confirmed impossible on this chip (`WIFI_MODEM_AUDIO.md`); the rest still open |

## Corrections found during Phase 1 (2026-10-31)
* The app freezer works on the port kernel (earlier note said it was missing).
* The thermal problem is a disabled `bcl-soc`, not a missing zone name.
* Memory is healthy at normal load; `mi_thermald` caps the CPU from about 35 C (`MEMORY_SCHEDULING.md`, `POWER_THERMAL_PERF.md`).
* Per-subsystem pages: `subsystems/` (power and thermal, memory, display and touch, Wi-Fi/modem/audio, GNSS/sensors/charging/storage/security, kernel base, HyperOS 4 kernel target).
