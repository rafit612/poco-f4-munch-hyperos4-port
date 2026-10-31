# Wi-Fi, modem and audio (Phase 1, 2026-10-31)

Read-only. One passive reading of the running phone (charging, about 9 hours since boot) plus the Xiaomi 17 HyperOS 4 reference on the pendrive. No taps, no calls, nothing changed.

## Wi-Fi
| Item | Value |
|---|---|
| Chip | Qualcomm QCA6390 (`ro.hardware.wlan.chip=639x`), Wi-Fi 6 (11ax), 2x2, DBS on |
| Stack | `cnss-daemon`, `wifi_hal_legacy`, supplicant; two station interfaces `wlan0` and `wlan1` (dual Wi-Fi flag on) |
| State | `wlan0` connected on 11ax to the home network; `wlan1` idle |
| Firmware | Closed, loaded by `cnss`; final official version |

**Wasted work from the newer Android framework** (log counts from one 75-minute window):
| Message | Count | Cause | Cost |
|---|---:|---|---|
| `Fail to get mlo info` plus a netlink request each time | 718 | Android 17 asks for Wi-Fi 7 multi-link data; Wi-Fi 6 firmware has none | About one netlink round trip every 6 s, bursts at screen on |
| `getCachedScanData is not implemented by HIDL` | 770 | New framework call on the old HIDL Wi-Fi HAL | Log line only |
| `bestIfaceCreationProposal is null, requestIface=STA` | 718 | Same retry loop as the MLO call | Same |
All three come from the Wi-Fi mainline module (framework side, replaced as one unit), so a fix means changing the module and isn't worth the risk. Treat as known noise, small cost.

* `persist.vendor.wifi.interrupt_test_mode=true` is set. It's a test-mode name, but it isn't in the porter's or official vendor `build.prop` (grep found no entry), so its origin is unknown: find who sets it before touching it.
* `ro.wifi.channels` is empty; fine.
* Earlier note stays open: 85-second drops on a 160 MHz router channel; needs the router change from the owner.

## Modem and telephony
| Item | Value |
|---|---|
| Baseband | `2.5.1.c1-14.1-0324_0657_6488b87c`, final official firmware for this phone |
| SIMs | Dual SIM, both LTE. SIM 1 Robi, SIM 2 Banglalink (shown as RYZE) |
| Signal at reading | SIM 1 RSRP -96 dBm, SIM 2 RSRP -65 dBm |
| Calls over Wi-Fi | Network type `LTE,IWLAN`: Wi-Fi calling active on at least one SIM |
| RIL | `qcrild` x2 (one per SIM), IMS daemons running, `vsimservice` running |
| Subsystems | `adsp`, `cdsp`, `npu`, `ipa_fws`, `ipa_uc`, `esoc0` (modem) all ONLINE |
| Carrier config | 105 modem software configs (MBN) loaded; `modem_mbn_check` on; VoLTE override 0 as designed |

Nothing wrong found. Still open from before, owner only: SIM 1 outgoing answered call, voice both ways.
**Rule stays:** never write modem, EFS or persist.

## Audio
| Item | Value |
|---|---|
| Card | `kona-mtp-snd-card`, 37 PCM devices |
| HALs | audio 6.0, effects 6.0, soundtrigger 2.3, Bluetooth audio 2.0, Qualcomm `audiohalext`, `qcrilaudio` per slot |
| Output threads | Mixer threads at 48 kHz; normal buffer 960 and 1920 frames; all in standby at the reading (good for battery) |
| Offload | Enabled for PCM 16 and 24 bit, video and gapless |
| Bluetooth | A2DP source, HFP AG, AVRCP target, GATT on. LE Audio profiles (BAP, CSIP, HAP, VCP) **off**, and the log says `could not find HW module for AUDIO_DEVICE_OUT_BLE_HEADSET`: LE Audio can't work on this chip |

**Findings**
| # | Finding | Count | Meaning | Candidate |
|---|---|---:|---|---|
| 1 | `Failed to load XML file: /odm/etc/audio/audio_lowpower_app_list.xml` | 23 | The file exists in the Xiaomi 17 odm (2870 bytes: volume and power-save templates per app group) but not here | Copy it into our odm only if the Qualcomm audio HAL reads it. It's an app list with volume factors, so it may change loudness for the listed apps: test, don't assume |
| 2 | `vendor.qti.bluetooth@1.0-wake_lock: Acquire write to wakelock file failed -1` | 862 in 37 min | EPERM on `/sys/power/wake_lock` means the process lacks `CAP_BLOCK_SUSPEND`. The Bluetooth HAL's rc asks for it, yet its ambient capabilities are empty while every other service with the same line (audio HAL, sensors HAL, `qcrild`, `sscrpcd`, `dspservice`, suspend service) has it. So the HAL gives up the capability itself after start | The vendor binary is official, so official probably does the same. Effect: Bluetooth can't hold its own wakelock while the phone sleeps, which could cause stutter during screen-off streaming. Not measured. Test candidate: rc-level `capabilities` can't fix it, since the process drops it later |
| 3 | `acdb_loader_adsp_set_audio_cal ... active device/stream not found` | 84 | Calibration sent when no stream is active | Qualcomm HAL noise |
| 4 | `Failed to fetch the lookup information of the device NB` | 170 | Narrow-band device lookup for calls | Noise unless call audio fails |
| 5 | `Could not get ctl for mixer cmd - Audio Stream Capture ... App Type Cfg` | 21 | A mixer control the kernel audio driver doesn't expose | Check against the audio driver in the new kernel (`techpack/audio` differs in 9 files between LineageOS and liyafe) |
| 6 | `audioserver` cannot find `vendor_hal_perf_hwservice` | 2 | Audio server asks for performance boosts | Same family as the display denial; candidate rule |

**Hotword and Bluetooth silence:** the earlier note stands (Google hotword on the LPI path loops the ADSP). It's a kernel and audio-module matter (`ROADMAP` A4), not a config one.

## Call speaker bug (found 2026-10-31)
The loudspeaker button can show Speaker while the sound stays on the earpiece, after another app has used the speaker. Cause is a stale device cache in the port's Telecom: `CALL_SPEAKER_BUG.md`. Fix planned in `ROM_PHASE2_CHANGES.md` section F.

## Kernel consequences
* The audio and Wi-Fi drivers are Qualcomm's `techpack/audio` and `qcacld` module trees: keep the same versions as the running kernel, and compare `techpack/audio` file by file before the first test (LineageOS and liyafe differ in 9 files there).
* `wlan` is built from `qca6390` sources; the Wi-Fi module is the porter's (`CONFIG_QCA_CLD_WLAN_PROFILE=qca6390`).

## Next
GNSS, sensors, charging, storage and security are in `GNSS_SENSORS_POWER_STORAGE_SECURITY.md`.
