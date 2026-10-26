# POCO F4 5G (munch) - hardware subsystem audit

Date: 2026-10-23, about 20:50. This is a read-only audit, with no changes, reboots or flashes.
Phone state at audit time: up about 1 h 40 min, locked, charging (AC), 98 %, after the no-wipe flash of the official vendor camera/audio/fingerprint stack.
Raw dumps: `/tmp/claude-1000/-home-odoo-dbsl-poco-f4-5g-8gb-256gb-munch/155acf9c-1946-41a4-8e72-96ea9676041c/scratchpad/hwaudit/`.
Cross-reference: `hardware_vendors.md` (same folder).

## Scorecard

| # | Subsystem | Status | One-line verdict |
|---|---|---|---|
| 1 | Modem / radio | OK / WARN | LTE B1 10 MHz on Banglalink (shown as RYZE), RSRP -95 dBm. NR allowed (mode 32). No VoLTE/VoWiFi: the carrier config disables it, same as official. |
| 2a | Wi-Fi | OK | 11ac 5745 MHz (ch 149), 2x2 VHT80, link 520 Mbps (max 866), country BD, driver 5.2.022.12B. |
| 2b | Bluetooth | OK | On, A2DP offload on, codecs SBC/AAC/aptX/aptX HD/aptX Adaptive/LDAC/LHDC V3/V5. LE Audio profiles off (correct for this chip). |
| 2c | NFC | OK | On, HCE payment/other categories present, Secure NFC off. |
| 3 | Sensors | OK | 65 sensors, nothing missing. Proximity = Elliptic ultrasonic, ALS = ams TCS3701 (front, behind the OLED) + Rohm BU27030 (back), IMU = ST LSM6DSO, mag = AKM AK0991x, SAR = Semtech SX932x/SX933x, OIS sensor present. No hall sensor (none fitted on munch). |
| 4 | Audio | OK (re-test with screen on) | Official audio HAL now: 0 `pcm_prepare` failures, 0 `hal_stream_write` stalls, 0 `Invalid snd_device`. Before, about 5550 speaker failures happened while the ultrasound proximity was active. A final check needs a screen-on test. |
| 5 | Display | WARN | The panel supports 60/90/120 Hz, but the user setting is 60 Hz: `peak_refresh_rate=60`, `user_refresh_rate=60`, `miui_refresh_rate=60`, `persist.vendor.dfps.level=60`. HDR10/HLG/HDR10+. Max luminance 420 nits (HDR metadata), brightness spline 2-500(-900 HBM) nits. Auto-brightness adj is now 0.0 (fixed). DC dimming is off. Double-tap to wake and to sleep are both on. |
| 6a | Storage | OK | UFS, /data f2fs with inlinecrypt (hardware ICE) and discard, FBE aes-256-cts plus metadata encryption, 187 GB free of 225 GB. |
| 6b | Thermal | WARN | mi_thermald is running, sconfig=0 (normal), all cooling devices at 0, CPU zones 44-46 °C while charging. But the Android thermal HAL reports no temperatures ("Current temperatures from HAL:" is empty), so framework thermal status and headroom are blind. |
| 6c | Battery / charging | WARN | Health good, 32.8 °C, 4.35 V. The health HAL reports a max charging current of 1.5 A at 5 V (about 7.5 W) on the current charger: either the charger is not the 67 W MI Turbo one, or the fast-charge handshake is not happening. Cycle count and charge type are unreadable without root. |
| 7 | Security | OK / WARN | SELinux enforcing, FBE+metadata encrypted, release-keys, user build (`ro.debuggable=0`), FRP partition present. Verified boot is orange (unlocked bootloader), even though `ro.boot.flash.locked=1` and `vbmeta.device_state=locked` are reported. Security patch: system 2026-08-01, vendor 2025-04-01. ADB and developer options are enabled. |
| 8 | Calibration | OK / unknown | Camera modules identified (OV64B40 Sunny main, OV8856 AAC ultra, IMX596 OFilm front, GC02M1 Sunny macro). /mnt/vendor/persist (sensor, audio and panel calibration) is unreadable without root, but nothing fails at runtime. |
| 9 | Fingerprint (side, in the power key) | FAIL (hardware) | Feature enabled (user choice), but `vendor.fps_hal` cannot start because the sensor is broken. The framework retries in a loop: `FingerprintUpdateActiveUserClient: Failed to setActiveGroup: HIDL daemon is null` about 15 000 times a minute (plus matching HidlToAidl* and HwBinder lines). Earlier measurement: hwservicemanager at about 46 % CPU and system_server at about 39 %. |

## 1. Modem / radio

- Baseband `2.5.1.c1-14.1-0324_0657_6488b87c` on both stacks (HyperOS 1 modem). DSDS dual SIM.
- SIM in slot 2: MCC 470 / MNC 03, Banglalink (the PLMN alpha shows the RYZE brand).
  - LTE, EARFCN 100 = Band 1 (2100 MHz), FDD, 10 MHz.
  - Serving cell: RSSI -65, RSRP -94/-95, RSRQ -10/-12, RSSNR 13 dB, level 3-4.
  - Neighbour LTE cell: 3 MHz carrier, RSRP -106/-108.
  - No carrier aggregation reported, ENDC not available, NR=invalid.
  - The carrier offers no NSA anchor here, which is normal for this area and SIM.
- Slot 1 is empty (OUT_OF_SERVICE, expected).
- Network mode: `preferred_network_mode=32,32` (NR/LTE/TDSCDMA/GSM/WCDMA), so 5G is allowed. `carrier_nr_availabilities_int_array=[1,2]` means NSA and SA are both allowed.
- IMS: an MMTEL feature is bound for both slots, but the carrier config has `carrier_volte_available_bool=false` and `carrier_wfc_ims_available_bool=false`.
  - This is the same as official HyperOS 1, because Xiaomi's munch carrier overlay has no MCC 470 entries.
  - Calls go over CSFB (2G/3G), so there is no VoLTE HD voice.
- SAR: Semtech SX932x/SX933x and the sar_algo sensors are present, so the antenna back-off machinery is alive.
- Bands: per the official Global spec (22021211RG, per GSMArena, unverified here):
  - 2G GSM 850/900/1800/1900;
  - 3G B1/2/4/5/8;
  - LTE B1/2/3/4/5/7/8/12/13/17/18/19/20/26/28/32/38/40/41/42/66;
  - 5G n1/3/5/7/8/20/28/38/40/41/66/77/78.

  The ROM does not restrict bands; that is fixed by the modem firmware and MBN.
- Fix option: add a VoLTE carrier-config override for 470-03. This needs a product or mi_ext overlay, and the modem MBN must support it. Medium risk, and success is not guaranteed.

**Update 2026-10-25 (`out_tele`):** VoLTE/VT/Wi-Fi calling are now allowed for 470-03 and every operator Xiaomi
supports (AOSP overlay + Xiaomi CarrierStudio layer in `/mi_ext/product/etc/vendor_device.xml`); the VoLTE switch shows
(`persist.dbg.volte_avail_ovr=0`); the Banglalink IMS APN is in the APN database. IMS still does not register
(`CODE_REGISTRATION_ERROR`) - next step is the modem MBN / IMS logs. See `ROM_HISTORY.md`.

## 2. Wi-Fi / Bluetooth / NFC

- Wi-Fi: QCA6390, driver 5.2.022.12B, firmware 1.0.1.0.1235.10. 11ac VHT80 2x2 on 5 GHz ch 149, RSSI -61, 520 Mbps, country BD (telephony-derived). No 6 GHz (correct).
  - The framework has `Ieee80211beEnabled=true` and logs `Fail to get mlo info` 1037 times. This is harmless noise, because the Android 17 framework queries Wi-Fi 7 multi-link (MLO) on a Wi-Fi 6 chip.
- Bluetooth: name "POCO F4 5G", A2DP offload on.
  - Codec priorities list SBC, AAC, aptX, aptX HD, aptX Adaptive, LDAC and LHDC V3/V5.
  - The connected device reports "optional codec supported is 0", so it is SBC-only: the device's limit, not the phone's.
  - LE Audio unicast/broadcast profiles are disabled, which matches the hardware.
- NFC: state on, reader option on, Secure NFC off, HCE payment and other categories enabled (NXP SN100U per hardware_vendors.md).

## 3. Sensors

All expected munch sensors are present and registered (65 entries incl. AOSP fusion):
- Proximity: Elliptic Labs ultrasonic (virtual, uses the earpiece/speaker plus a microphone).
- Light: ams TCS3701 (front ALS and CCT, under the OLED), Rohm BU27030 (back lux).
- Motion: ST LSM6DSO accelerometer and gyroscope, AKM AK0991x magnetometer, plus Qualcomm/Xiaomi virtual sensors (step, tilt, pickup, pocket, screen_down, AOD, HAR, device orientation).
- SAR: Semtech SX932x / SX933x.
- OIS manager sensor (xiaomi).

The TCS3701 is calibrated to the original Samsung E4 panel's transmittance. On the aftermarket panel, auto-brightness levels can be off; `screen_auto_brightness_adj` is now 0.0. Fix if brightness still feels wrong: use the slider learning (Android stores a short-term model), not a ROM change.

IR blaster: the `consumer_ir` service, the `IConsumerIr/default` AIDL and the `android.hardware.consumerir` feature are all present, so it is OK (Mi Remote installed).

## 4. Audio

- The official HyperOS 1 `audio.primary.kona.so` and `sound_trigger.primary.kona.so` are installed. Output threads: speaker, telephony TX, 48 kHz mixers.
- The current log has no audio HAL errors: 0 pcm_prepare failures and 0 stalls, against the earlier 5550/5552 failures with the porter's HAL while the ultrasound proximity was on.
- Caveat: the phone has been locked or screen-off since boot, so the ultrasound proximity usecase has not started yet (0 `ultrasound-proximity=1` events). Re-check with the screen on while playing touch/notification sounds.
- Speaker amplifiers are TFA98xx (2x). Dolby/MiSound produced no errors.

**Update 2026-10-25:** "connected but no sound" on Bluetooth earbuds was the audio DSP restarting about once a second
(`out_snd_mon_cb ... status offline`, `out_write: sound card is not active/SSR state`), triggered by Google's "Hey Google"
DSP model (sound trigger vendor_uuid 7038ddc8-...). Not Bluetooth: same with Bluetooth off. The port kernel has its own
built-in audio drivers; official HyperOS 1 uses the vendor modules. Fix: Google engines removed from
`sound_trigger_platform_info.xml` + no audio HAL restart on `sys.audio.restart.hal` (`port_fixes/soundtrigger_fix/`).
After: 0 DSP restarts, 0 HAL restarts in 60 s; A2DP AAC to QCY MeloBuds N20 Pro plays. Earbud mic (HFP/SCO) not tested yet.

## 5. Display

- Modes: 1080x2400 at 60/90/120 Hz (mode ids 1/3/2); HDR types 2/3/4.
- The active mode is 60 Hz because the user or restored settings capped it: `peak_refresh_rate=60`, `user_refresh_rate=60`, `miui_refresh_rate=60` (and `persist.vendor.dfps.level=60`). `is_smart_fps=0`.
  - Fix: Settings → Display → Refresh rate → 120 Hz. Settings only, no risk.
- Brightness: spline min 2 nits, normal max 500, HBM 900. HDR luminance metadata max 420 / avg 210 / min 0.323.
- DC dimming: `persist.vendor.dc_backlight.enable=false` (threshold 450), as configured.
- Touch: FocalTech `fts_ts` (aftermarket panel; the original is FT3658U), `ro.vendor.display.touch.idle.enable=true`.
- Double-tap: `gesture_wakeup=1`, `double_tap_to_wake=1`, `double_tap_to_sleep=1`. The ROM sends TouchFeature mode 14=1 on change (verified earlier). Waking depends on the replacement panel's touch firmware supporting the gesture.

## 6. Storage / thermal / battery

- /data: f2fs on dm-47 (sda18), inlinecrypt, discard, checkpoint_merge. FBE aes-256-cts filenames plus metadata encryption.
  - 37 GB used of 225 GB.
  - /metadata is 84 % free.
  - Disk write latency 0 ms (512 B test).
- Thermal:
  - mi_thermald is running; the thermal message sconfig is 0 (normal profile).
  - All cpufreq, devfreq, cdsp and isolate cooling devices are at 0, so there is no throttling now.
  - Zones aoss0 40.7 °C, cpu-0-x 44-46 °C (charging plus the fingerprint retry loop).
  - The Android thermal HAL 2.0 is connected but returns no temperatures. Thresholds load fine: CPU/GPU 95/115 °C, battery 80/90 °C, NPU 95/115 °C.
  - Impact: the framework thermal status always stays 0, so apps and games using thermal headroom get no signal. Vendor throttling by mi_thermald still works.
  - Fix option: investigate the vendor thermal HAL config (which thermal sensors the HAL exposes). Low priority.
- Battery: health 2 (good), 32.8 °C, 4348 mV, 98 %, Li-poly.
  - On AC the health HAL reports a max charging current of 1.5 A at 5 V. On a 67 W MI charger with a 6 A cable this should show a higher current or voltage once it negotiates.
  - Fix: re-check with the original charger and cable; it's hardware or the charger, not the ROM.

## 7. Security

- `getenforce` = Enforcing, `ro.boot.selinux=enforcing`.
- Verified boot: orange (unlocked). `ro.boot.flash.locked=1` and `vbmeta.device_state=locked` are spoofed values, so Play Integrity "device" verdicts depend on that spoof.
- Build tags release-keys, `ro.debuggable=0`.
- Security patch: system 2026-08-01, vendor 2025-04-01 (the vendor is the last official munch HyperOS 1 build, so it can't get newer).
- `adb_enabled=1` and `development_settings_enabled=1`. Fine for maintenance; turn them off when you are done, for security.
- FRP partition: `/dev/block/bootdevice/by-name/frp` (ro.frp.pst) is present.

## 8. Calibration

- Camera: `persist.vendor.camera.mi.module.info`: back_main=ov64b40_i, back_ultra=ov8856_i, front_main=imx596_i, back_macro=gc02m1_i, bokeh `s0_OV64B_AAC_64M`. The official per-module tuning is now installed.
- Sensor, audio (speaker calibration) and panel calibration live in /mnt/vendor/persist, which is unreadable without root. No runtime errors point to missing calibration.

## Top fixes

1. Fingerprint retry loop (FAIL, CPU/battery/heat). It is either temporary until the new power-key sensor is fitted, or the feature must be hidden again. The user chose to keep it on, so it will stop once the sensor works.
2. Refresh rate is capped at 60 Hz. Set 120 Hz in Settings → Display (no flash).
3. Speaker/ultrasound: re-test with the screen on to confirm the official audio HAL fixed the 5550 failures. Watch `pcm_prepare returned` in logcat.
4. Charging at 1.5 A / 5 V: test with the 67 W charger and cable.
5. Thermal HAL reports no temperatures. Investigate the vendor thermal HAL sensor config (low priority; mi_thermald still throttles).
6. No VoLTE on Banglalink, same as official. A 470-03 carrier-config overlay could be tried (medium risk).
7. Optional: turn off developer options and ADB when the work is done.
