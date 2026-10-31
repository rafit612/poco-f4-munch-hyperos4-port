# GNSS, sensors, charging, storage and security (Phase 1, 2026-10-31)

Read-only, one passive reading. Same method as the other subsystem pages.

## GNSS (location)
| Item | Value |
|---|---|
| Services running | `android.hardware.gnss@2.1-service-qti`, `gnss_service`, `loc_launcher`, `lowi-server`, `xtra-daemon`, `loc_sys_service` |
| Providers | Google network and fused providers plus the GNSS provider |
| Last fix | Network location 46 m accuracy and fused 100 m, both about 9 hours old (phone indoors) |

* **Loop still present:** `loc_sys_service` (HyperOS 4's new AIDL location service) waits for an AIDL GNSS HAL the old vendor doesn't have. The vendor's HIDL 2.1 GNSS works. Plan: test stopping `loc_sys_service` and confirm a GPS fix outside.
* `persist.sys.mqs.gps.rtk=ON` with `supl.qxwz.com:7275` (a China RTK correction service) is set. No log mention and no open connection to port 7275 at the reading, so nothing is sent now. It's still a leftover to remove from the ROM properties in cleanup.
* Dual-frequency flags (`miui_gnss_dc`) are on: whether the hardware uses L5 isn't proven.
* **Needs a walk outside** (owner): time to first fix and satellites in view, for a baseline.

## Sensors
73 entries reported. The hardware list matches `SENSORS_ARCHITECTURE.md`:
| Kind | Parts |
|---|---|
| Motion | STMicro `lsm6dso` accelerometer and gyroscope, AKM `ak0991x` magnetometer |
| Light | ams `tcs3701` ambient light and front colour sensor, Rohm `bu27030` rear flicker sensor |
| Proximity | Elliptic Labs ultrasound proximity, Semtech `sx933x` SAR (two) |
| Xiaomi virtual | pickup, pocket mode, screen down, `har` (activity recognition), AOD, `device_orient`, `ois_manager`, touch |
| Android virtual | rotation vector, game rotation, gravity, linear acceleration, step detector, pedometer |
All run on the SLPI DSP (closed firmware). At the reading eight sensors were active (step, pedometer, motion, light, orientation); `har` and `sns_smd` run at 1 to 200 ms. The kernel needs only the glue: `US_PROXIMITY` (the running kernel has 16 symbols for it) and the DSP RPC drivers. Nothing to change except keeping `US_PROXIMITY=y` in the next kernel.

## Charging and battery
| Item | Value |
|---|---|
| Health | Full charge 4400 mAh of 4500 design: **97.8 %**, 144 cycles, good |
| Temperature | 29.1 C at 100 % |
| Charger | Charge pumps `bq2597x` (master, slave), gauge `bq27z561`, switcher `qpnp_smb5` (munch variants), LN8000 |
| Port at reading | `USB_CDP` from the laptop, 5.1 V, limit 1.2 A |
Max charge speed can't be read on the laptop port. Retest on the real charger (owner), with the phone's battery below 50 %. Everything else is fine.
Cooling device `battery` at level 2 at 100 % was seen earlier; it's the charge-full taper, not a fault.

## Storage
| Item | Value |
|---|---|
| UFS | SK hynix `HN8T15BZGKX016`, firmware A043 |
| Wear | Life estimate A `0x03` (20-30 % of the SLC area used), B `0x01` (0-10 % of the main area), end-of-life info `0x01` normal |
| Data | f2fs on `/data`, 225 GB, 84 GB used (38 %), 141 GB free; discard on, background GC on |
| Power | Clock gating on, auto-hibernate on |
| I/O scheduler | `cfq`, read-ahead 128 KB (see `MEMORY_SCHEDULING.md`) |
Nothing to fix. The wear on the SLC part is the one to watch over a year.

## Security status
| Item | State |
|---|---|
| SELinux | Enforcing |
| Verified boot | `orange` while the lock flags say locked and `vbmeta` locked: known issue C3 (lock state spoofed), cannot be fixed without a signed boot chain |
| Encryption | File-based, on |
| Build | `user`, `release-keys`, not debuggable, `adb` secure |
| Root | `ksu`, `ksud` and `/data/adb` are present; 0 modules; research access still works through `su` |
| First API level | 31 (the vendor is SDK 30) |

**Denials seen** (one window of the log), as narrow-rule candidates for Phase 2, each to be tested separately:
| Who | Wants | Count |
|---|---|---:|
| `mediaserver` (thread `NPDecoder`) | read `vendor_default_prop` | 65 |
| `surfaceflinger` | read `vendor_frc_prop`; find `vendor.perfservice` | 4; 2 |
| `artd` | read `vendor_default_prop` | 4 |
| `system_server` | read `wifi_hal_prop` | 2 |
| `audioserver` | find `vendor_hal_perf_hwservice` | 2 |
| a platform app, every 10 min | find `vendor.xiaomi.aidl.mipowerhal.IMiPowerHalAIDLService/default` | 6+ |
The last one matters: **HyperOS 4's framework looks for a Xiaomi AIDL power HAL (`mipowerhal`) that the Android 11 vendor doesn't have.** It joins the ADPF finding (`POWER_THERMAL_PERF.md`): the vendor's power HAL is the old HIDL one.
Each rule needs the offline `secilc` check and a new `product_sepolicy_and_mapping.sha256` (see `AGENTS.md` rule 2), so they ship with the next build, not before.

## Kernel options to keep in the next kernel
From the LineageOS munch config, compared with `liyafe`: `US_PROXIMITY`, `INPUT_AW86927_HAPTIC`, `QPNP_SMB5_MUNCH`, `BQ2597X_CHARGE_PUMP_STANDALONE_MUNCH`, `CHARGER_LN8000_MUNCH`, `FUEL_GAUGE_BQ27Z561_MUNCH`, fingerprint and `TOUCHSCREEN_XIAOMI_TOUCHFEATURE` are all `=y` in `liyafe`. Seven others (`BACKLIGHT_KTZ8866`, `DUALKTZ8866`, `MOTOR_DRV8846`, `HALL_AKM09970`, `LEDS_AW2015`, `PS5169`, `TOUCHSCREEN_COMMON`) are not set there, and the running kernel has no symbol for any of them, so they aren't needed on this phone.

## Phase 1 status
Done as first pass: power and thermal, memory and scheduling, display and touch, Wi-Fi, modem, audio, GNSS, sensors, charging, storage, security. Still open inside them: each page's "next" list, mostly measurements that need the owner or a game session.
