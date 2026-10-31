# Status of the old audit findings, rechecked on the running ROM (2026-10-31, tag T20261031b)

Sources: `audit/agents/security/SECURITY_REPORT.md`, `audit/agents/hardware/HARDWARE_REPORT.md` (both from before most fixes). Read live from the phone.

## Security
| ID | Finding | Now | Evidence |
|---|---|---|---|
| C1 | Data not encrypted | **Fixed** | `ro.crypto.type=file`, `/data` mounted with `inlinecrypt`, metadata encryption files present |
| C2 | Signature/downgrade bypass in the framework | **Open** | `ROM_HISTORY.md`: still in the port framework; to be confirmed by code in Phase 1 |
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
| 4 | Thermal HAL no temperatures, ADPF off | **Open, mechanism found**: `subsystems/POWER_THERMAL_PERF.md` |
| 5 | GNSS raw measurements missing | Open, not rechecked |
| 6 | `traced`, `vendor_security` restarting | **Fixed**: `traced` stopped on purpose, `vendor_security` removed |
| 7-9, 13, 16 | Flags and limits (virtualisation flag, LE Audio, Camera2 limits, haptics, spatializer) | Open, Phase 1 subsystems |
