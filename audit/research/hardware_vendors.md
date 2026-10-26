# POCO F4 5G (munch) - Hardware and Vendor Component Reference

Device: POCO F4 5G, model 22021211RG (Global). The same board ships as the Redmi K40S (22021211RC, China) and the POCO F4 India (22021211RI). Xiaomi's internal project name is **L11R**. That name appears in the touch firmware `fw_ft3658_l11r.i` and the camera model `dof_l11r_mecp.bin`.

Research date: 2026-10-23. The research was web and source-tree only. No adb or fastboot command was run.

Each claim is tagged with how it was verified:
- **[OFFICIAL]**: Xiaomi, Qualcomm or OmniVision pages.
- **[SRC]**: kernel or device-tree source (LineageOS or MiCode).
- **[3P]**: third-party spec database or press.
- **[DEVICE]**: ground truth from this phone's vendor props, supplied by the coordinator.
- **[INFERENCE]**: reasoning from the evidence, not directly sourced.
- **[UNVERIFIED]**: could not be confirmed.

---

## 0. Corrections to the brief (read first)

| Brief said | Actual finding | Evidence |
|---|---|---|
| "Under-display fingerprint is Goodix optical" | **Wrong.** The POCO F4 / K40S has a **side-mounted capacitive fingerprint sensor in the power key**. It is not under the display. `uinput-goodix` is the input device that the *non-FOD* Goodix `gf_spi` driver creates. | Official spec says "Side fingerprint sensor" [OFFICIAL]. `persist.vendor.fingerprint.type=side` and `sensor_location=1080\|965\|115` (right edge, y=965 px, 115 px long) [SRC: LineageOS munch vendor.prop]. Kernel config enables `CONFIG_FINGERPRINT_GOODIX` and `CONFIG_FINGERPRINT_FPC`, not the `_FOD` variants [SRC: munch.config]. `GF_INPUT_NAME "uinput-goodix"` [SRC: goodix/gf_spi.h]. |
| Main camera "Sony IMX582 64MP, 1/1.73"" | IMX582 is a **48MP**, 1/2", 0.8 um sensor. It is used only in the **K40S/China variant** (OFilm module). **This phone** has an **OmniVision OV64B40** (64MP, 1/2", 0.702 um, Sunny module). | [DEVICE], [OFFICIAL: ovt.com], [3P: GSMArena K40S], vendor blob list [SRC] |
| Ultrawide "Sony IMX355" | The ultrawide is an **OmniVision OV8856** in both module sources (AAC and Sunny). There are no IMX355 blobs. | [DEVICE], [SRC: proprietary-files.txt] |
| Vendor = "HyperOS 1, Android 13" | Version string `V816.0.9.0.ULMMIXM` = **HyperOS 1.0.9.0 Global**, and the "U" letter means Android 14. LineageOS keeps the vendor fingerprint as `munch:13/RKQ1.211001.001/V816.0.9.0.ULMMIXM`, so the vendor image reports **13** as its release. This fits GRF vendor freezing. Both statements hold: the ROM package is Android 14 and the vendor build reports API 33. | [3P: miuirom.org], [SRC: libvariant_xiaomi_munch.cpp], [INFERENCE] |
| Touch IC "FT3680 or Goodix?" | The original touch IC is **FocalTech FT3658U** on SPI. The kernel driver is `focaltech_3658u` and its input name is `fts_ts`. | [SRC: munch.config `CONFIG_TOUCHSCREEN_FOCALTECH_3658U=y`; focaltech_config.h `FTS_CHIP_TYPE _FT3658U`] |

**Consequence for the user's complaints.** The weak fingerprint cannot be caused by the aftermarket OLED's optical transmittance, because the sensor is not under the display. Look at the power-key sensor and its flex, the enrolment, and the vendor fingerprint HAL. Double-tap-to-wake is a separate issue in the touch-controller firmware and its suspend path (section 4.4).

---

## 1. SoC - Qualcomm Snapdragon 870 5G (SM8250-AC, "kona")

### 1.1 CPU - Kryo 585, 7 nm (TSMC N7P)

| Cluster | Cores | Core type | Max freq | OPP steps (kHz) [SRC: munch power_profile.xml] |
|---|---|---|---|---|
| Silver (policy0) | cpu0-3 | Cortex-A55 based | 1.80 GHz | 300000 ... 1804800 (17 steps) |
| Gold (policy4) | cpu4-6 | Cortex-A77 based | 2.42 GHz | 710400 ... 2419200 (18 steps) |
| Prime (policy7) | cpu7 | Cortex-A77 based, 512 KB L2 | 3.19 GHz (marketed 3.2) | 844800 ... 2841600, **3187200** (21 steps) |

- The L3 cache is 4 MB, shared [3P: XDA].
- The official Xiaomi spec gives 1x3.2 GHz, 3x2.42 GHz and 4x1.8 GHz [OFFICIAL: mi.com/uk spec]. The Qualcomm brief gives part number SM8250-AC, up to 3.2 GHz [OFFICIAL].
- Power model for the prime core [SRC: power_profile]. Going from 2841.6 to 3187.2 MHz (+12% frequency) raises current from 493 to 677 mA (+37%). This is the least efficient OPP on the chip.

### 1.2 GPU - Adreno 650

- Per [SRC: kona-v2-gpu.dtsi], SM8250-AC speed bins run up to **670 MHz**. The power levels are 670 / 587 / 525 / 490 / 441.6 / 400 / 305 MHz.
- The 865 bin 0 tops out at 587 MHz.
- API support: Vulkan 1.1, OpenGL ES 3.2, OpenCL 2.0 FP [OFFICIAL: Qualcomm brief].
- Qualcomm advertises updateable GPU drivers and 10-bit HDR gaming.

### 1.3 ISP - Qualcomm Spectra 480 (dual 14-bit) [OFFICIAL: Qualcomm SD870 product brief]

- Throughput: up to 2 gigapixels/s, with a CV-ISP hardware accelerator.
- Photo:
  - up to 200 MP photo capture;
  - up to **64 MP single camera @30 fps with ZSL**;
  - up to **25 MP dual camera @30 fps with ZSL**.
- Video:
  - 8K @30 fps;
  - 4K @120 fps;
  - 4K HDR with Portrait (bokeh);
  - 4K video + 64 MP photo;
  - 720p @960 fps slow-motion;
  - 10-bit Rec.2020;
  - HDR10, HDR10+, HLG and Dolby Vision capture;
  - HEIC and HEVC.
- These are **SoC ceilings, not device capabilities**. The device and sensor limits are in section 3.

### 1.4 AI, DSP, modem and memory controller [OFFICIAL: Qualcomm brief]

- **AI:** 5th-gen AI Engine. The Hexagon 698 has a Tensor Accelerator, HVX and a Scalar Accelerator, for up to **15 TOPS**. It also has the Qualcomm Sensing Hub.
- **Modem:** Snapdragon X55 5G Modem-RF.
  - Peak speeds: 7.5 Gbps down and 3 Gbps up.
  - Sub-6: 200 MHz, 4x4 MIMO.
  - mmWave: 800 MHz, 8 carriers. The POCO F4 is sub-6 only per its band list [OFFICIAL].
  - The X55 is a discrete chip next to the SoC, not integrated [3P: 9to5google/XDA].
- **Memory:**
  - LPDDR5 up to **2750 MHz** (5500 MT/s) or LPDDR4X up to 2133 MHz, max 16 GB.
  - The SM8250 has a 3 MB system-level cache (LLCC) [3P: XDA, 865 table].
- **Display engine:**
  - On-device: 4K60 or QHD+ 144 Hz.
  - External: 4K60 over DP alt-mode. The LineageOS munch tree sets `&sde_dp { status = "disabled"; }` [SRC]. **DP output is disabled on munch.**
- **Connectivity:**
  - FastConnect 6800: Wi-Fi 6 2x2, 1.774 Gbps peak, 2.4 and 5 GHz (no 6 GHz).
  - Bluetooth 5.2 with aptX Adaptive and aptX Voice.
- **Charging:** QC4+.
- **Audio:** WCD938x-class codec (Aqstic).

### 1.5 Governor and scheduler reference (LineageOS sm8250-common, branch lineage-23.2) [SRC]

The settings below come from `rootdir/etc/init.qcom.power.rc`.

**Governor:**
- All three policies use `schedutil`.
- `up_rate_limit_us=500`.
- `down_rate_limit_us=20000`.

**Kernel scheduling model:**
- The kernel is 4.19 and uses EAS with **schedtune** (`/dev/stune`).
- At runtime `top-app` has `schedtune.boost=10` and `prefer_idle=1`. Foreground has `prefer_idle=1` and boost 0.

**Runtime cpusets:**

| cpuset | CPUs |
|---|---|
| top-app | 0-7 |
| foreground | 0-3,5-6 |
| background | 0-1 |
| system-background | 0-3 |
| restricted | 0-3 |

**Boot and runtime extras:**
- At boot, all stune groups get `boost=100` and `prefer_high_cap=1`. At `sys.boot_completed` they are reset to the runtime values.
- A `camera-daemon` stune/cpuset group is created.
- The rc writes `sched_lib_name "UnityMain,libunity.so"` with `sched_lib_mask_force 255`.

**Block layer and UFS:**
- `nr_requests 128`, `discard_max_bytes 128MB`.
- After boot it re-enables UFS `clkscale_enable=1` and `clkgate_enable=1`.

**PowerHAL:** `android.hardware.power-service.lineage-libperfmgr` reads `configs/powerhint.json`. Its key hints:

| Hint | What it sets |
|---|---|
| INTERACTION | min freqs 1171.2 / 1286.4 / 1190.4 MHz (silver/gold/prime); CPU-LLCC BW min 9155; LLCC-DDR min 2597 |
| LAUNCH (5 s) | all clusters max; GPU force clk/rail on; L3 min 1.6128 GHz; `cpu_dma_latency 61` |
| SUSTAINED_PERFORMANCE | caps silver 1075.2, gold 1478.4, prime 1305.6 MHz; GPU max_pwrlevel 1 (587 MHz) |
| CAMERA_STREAMING_MID/LOW | caps gold 1958.4, prime 1862.4 MHz |
| CAMERA_STREAMING_HIGH | caps gold 1766.4, prime 1747.2 MHz |
| EXPENSIVE_RENDERING | GPU min_pwrlevel 1, max_pwrlevel 0 |
| DOUBLE_TAP_TO_WAKE | `/sys/touchpanel/double_tap` (the LineageOS kernel exposes this node; the stock kernel uses TouchFeature) |

**Thermal profile switching:** LineageOS writes scene IDs to `/sys/class/thermal/thermal_message/sconfig`. The stock Mi thermal-engine reads the same node.

| Scene | ID |
|---|---|
| default | 0 |
| dialer | 8 |
| gaming | 9 |
| benchmark | 10 |
| browser | 11 |
| camera | 12 |
| streaming | 14 |

The vendor ships `thermal-normal/-camera/-video/-4k/-8k/-mgame/-tgame/-nolimits/...conf` [SRC: proprietary-files.txt]. These are generic Mi thermald profiles. The presence of `thermal-8k.conf` does **not** mean munch records 8K.

---

## 2. RAM and storage

- **RAM:** LPDDR5 [OFFICIAL: mi.com/uk "LPDDR5+ UFS 3.1"].
  - Retail configurations: 6+128 and 8+256 (UK). GSMArena also lists 12 GB.
  - The SoC maximum is 2750 MHz (LPDDR5-5500) [OFFICIAL Qualcomm]. The exact DRAM part and vendor (Micron, Samsung or SK hynix) are **[UNVERIFIED]** and can differ per unit. Read them on the device from `/proc/meminfo` and `/sys/class/devfreq/*ddr*` OPPs.
- **Storage:** UFS 3.1 [OFFICIAL]. It is exposed as `/dev/block/sda`, and LineageOS tunes `sda` [SRC]. The A/B layout is virtual A/B with a vendor ramdisk (`TARGET_IS_VAB := true`) [SRC].

---

## 3. Cameras

### 3.1 Sensor and module inventory (from vendor blobs) [SRC: LineageOS munch proprietary-files.txt] [DEVICE]

| Role | Kernel slot (cell-index / CSIPHY / CCI) | Variant A (**this phone**) | Variant B (K40S / other) | Actuator / EEPROM |
|---|---|---|---|---|
| Rear wide (main) | 0 / CSIPHY1 / CCI0 | `munch_sunny_ov64b40_wide` (OmniVision OV64B40, Sunny) | `munch_ofilm_imx582_wide` (Sony IMX582, OFilm; the sensormodule bin comes "from munch_cn") | DW9800V VCM AF (`..._dw9800v_wide_actuator`); EEPROM GT24P128E |
| Front | 1 / CSIPHY4 / CCI1 | `munch_sunny_imx596_front` or `munch_ofilm_imx596_front` (Sony IMX596) | same | EEPROM P24C64 (Sunny) or GT24P64E (OFilm); no actuator (fixed focus) |
| Rear ultrawide | 2 / CSIPHY2 / CCI0 | `munch_aac_ov8856_ultra` (OmniVision OV8856, AAC) [DEVICE] | `munch_sunny_ov8856_ultra` | EEPROM GT24P64E; fixed focus |
| Rear macro | 3 / CSIPHY0 / CCI1 | `munch_sunny_gc02m1_macro` (GalaxyCore GC02M1, Sunny) [DEVICE] | `munch_ofilm_gc02m1_macro` | EEPROM GT24P64E (Sunny) or BL24SA64 (OFilm); fixed focus |

Notes:
- The kernel cell-index is the sensor slot. It is **not necessarily** the Camera2 ID that the Xiaomi camera HAL exposes. [INFERENCE]
- There is **no `qcom,ois` node** in `munch-sm8250-camera-sensor-mtp.dtsi` or the camera-board dtsi, and there is **no `com.qti.ois.*` blob**. Xiaomi still officially advertises "64MP main camera with OIS" [OFFICIAL]. The OIS is therefore most likely a **module-internal, self-contained OIS** (driver IC and gyro inside the Sunny or OFilm module), which the AP cannot tune. **[INFERENCE]**
- Electronic stabilisation is AP-side. The vendor ships `vidhance_calibration` (Imint Vidhance EIS) and `eisoverridesettings.txt` [SRC].
- Unused stray blobs are also in the vendor: `com.qti.sensor.imx563.so`, `com.qti.eeprom.truly_cmb433.so` and `com.qti.eeprom.umi_sunny_s5k5e8yx_depth.so` (leftovers from other kona projects) [SRC].

### 3.2 Camera sensor table

| Camera | Sensor | MP (array) | Optical format | Pixel | Aperture / lens | FOV | Focus | OIS | Video max (as shipped) | Sensor-native video capability |
|---|---|---|---|---|---|---|---|---|---|---|
| Main (this phone) | **OmniVision OV64B40** (PureCel Plus-S stacked) | 64 MP (9248x6944) | 1/2" | 0.702 um; 1.4 um 4-in-1 binned | f/1.79, 6P lens [OFFICIAL] | about 80 deg wide (focal length not published) [UNVERIFIED] | PDAF: Type-2 2x2 microlens-PDAF [OFFICIAL ovt] | Yes, module OIS [OFFICIAL Xiaomi] | **4K60, 4K30, 1080p60/30, 720p30** [OFFICIAL Xiaomi spec] | 64MP@15, 16MP binned@30, **8K@30**, 4K@60 (4K+EIS@30), 1080p@240, 720p@480; staggered HDR with 2 or 3 exposures (3-exposure up to 16MP video); MIPI 4-lane D-PHY up to 3.0 Gbps per lane or C-PHY 2/3 trio at 2.45 Gsps [OFFICIAL ovt.com] |
| Main (K40S variant) | Sony IMX582 (Quad Bayer) | 48 MP (8000x6000) | 1/2" | 0.8 um; 1.6 um binned | f/1.79 | about 80 deg [UNVERIFIED] | PDAF | Yes | **4K30**, 1080p 30/60/120, 720p@960 (interpolated), gyro-EIS [3P: GSMArena K40S] | IMX582 does not offer 4K60 in Xiaomi's implementation [3P] |
| Ultrawide | **OmniVision OV8856** | 8 MP (3264x2448) | 1/4" | 1.12 um | f/2.2 | 119 deg [OFFICIAL] | Fixed | No | 1080p (8 MP is too narrow for 4K) [INFERENCE] | 8MP@30, 1080p@60, EIS crops at 2112x1188 and 1408x792; alternate-row (interlaced) HDR; 4-lane MIPI; on-chip OTP [OFFICIAL ovt.com] |
| Macro | **GalaxyCore GC02M1** | 2 MP (1600x1200) | 1/5" | 1.75 um | f/2.4 | n/a, about 4 cm working distance [UNVERIFIED] | Fixed | No | 720p-class (1600x1200 cannot natively produce 1080p) [INFERENCE] | basic RGB Bayer, no PDAF [3P: helpix] |
| Front | **Sony IMX596** | 20 MP | about 1/3.1" (sources disagree: 1/3.06" GSMArena, 1/3.4" helpix) | 0.8 um (Fonearena, K40S launch); GSMArena POCO page says 1.0 um | f/2.45 [OFFICIAL] | n/a | Fixed | No | 1080p30 (POCO page) or 1080p 30/120 (K40S page) [3P] | Xiaomi-specific part from 2022, also used in K50, 12T and 13T. No public datasheet [UNVERIFIED] |

Front-camera arithmetic: 20 MP at 0.8 um is about 4.15x3.11 mm, a 5.18 mm diagonal, which is about the 1/3.1" type. That supports 0.8 um. A 1.0 um pixel would imply 1/2.5".

### 3.3 Differences that matter for camera tuning (OV64B40 vs IMX582)

1. **Resolution and remosaic.**
   - The OV64B full readout is 9248x6944 at **15 fps** max. The default stream is the 4-cell-binned 16 MP (4624x3472) at 30 fps.
   - The OV64B has an **on-chip 4-cell-to-Bayer remosaic**, so a 64 MP RAW comes out as normal Bayer.
   - The IMX582 variant is 48 MP / 12 MP binned.
   - A port that hard-codes 48 MP or 12 MP picture sizes, or IMX582-specific `almalence_sr_params_wide.config` choices, may misbehave on OV64B. The vendor ships both `almalence_sr_params_wide.config` and `..._wide_64M.config` [SRC].
2. **Video.**
   - The OV64B variant officially supports **4K60**. The IMX582 variant (K40S) tops out at **4K30**.
   - Neither variant ships **8K** or **4K120**, although the Spectra 480 and the OV64B silicon can do 8K30. Xiaomi did not tune or enable it, and there is no 8K sensor-mode tuning in `com.qti.tuned.munch_sunny_ov64b40_wide.bin` as far as public data shows [UNVERIFIED].
3. **HDR.**
   - The OV64B supports **staggered HDR** with 2 or 3 exposures (3-exposure only at 16 MP and below).
   - The IMX582 supports Sony Quad-Bayer HDR modes.
   - The Xiaomi HDR pipeline (`miai_hdr_config.yaml`, `hdrd_ui9_params.config`, Arcsoft HDR+ HVX skel) is tuned per module through the `com.qti.tuned.*` bins. **Do not cross-load the tuning bins** between the two variants.
4. **AF.** Both variants use a DW9800V VCM (per-module actuator libs). PDAF differs: the OV64B uses 2x2 ML-PDAF, while the IMX582 uses Sony shielded-pixel PDAF. The AF tuning lives in the sensormodule and tuned bins.
5. **Pixel pitch and low light.** The OV64B 0.7 um pixel is smaller than the IMX582 0.8 um. Expect more noise per native pixel, and rely on 4-in-1 binning (1.4 um) for preview, video and night.
6. **Ultrawide.** The OV8856 is a 1/4" fixed-focus sensor that comes from two module sources (AAC or Sunny) with separate tuning. Its sensor-side maximum is 1080p60. The ultrawide is therefore the limiting lens for any multi-camera 4K zoom-switch video.

---

## 4. Display, touch, fingerprint and light sensors

### 4.1 Original display panel

| Property | Value | Source |
|---|---|---|
| Type | 6.67" **E4 AMOLED**, 2400x1080 FHD+, 20:9, 2.76 mm punch-hole ("DotDisplay") | [OFFICIAL] |
| Refresh | 60 / 90 / 120 Hz levels (automatic switching) | [OFFICIAL overview] |
| Touch sampling | **360 Hz** | [OFFICIAL spec page] |
| Colour | DCI-P3 100% (typ), TrueColor, HDR10+, Dolby Vision, MEMC | [OFFICIAL] |
| Brightness | 900 nits HBM, 1300 nits peak; contrast 5,000,000:1; "Sunlight display 3.0"; GSMArena measured 1003 nits | [OFFICIAL], [3P] |
| Protection | Corning Gorilla Glass 5 | [OFFICIAL] |
| Panel ID | `qdcm_calib_data_xiaomi_38_08_0a_cmd_mode_dsc_dsi_panel.xml`: command-mode DSC panel. The Redmi K40 / POCO F3 (alioth) ships the identical ID, so the two phones share the **same Samsung Display E4 panel family** | [SRC: munch and alioth proprietary-files]; Samsung attribution is [INFERENCE] |
| Backlight | DSI brightness 1..2047 (11-bit), init 536 (LineageOS dts). LineageOS maps user brightness 255 to about 455 nits sustained (`config_screenBrightnessNits` max 455); HBM is separate | [SRC] |
| DC dimming / PWM | MIUI on K40-family devices offered "anti-flicker" DC-like dimming. No official PWM frequency is published for munch | [UNVERIFIED] |
| Display out | DP alt-mode disabled in the device tree | [SRC] |

### 4.2 Original touch controller

- **FocalTech FT3658U**, chip type `0x3658D488` [SRC: focaltech_config.h].
  - Bus: SPI (`qupv3_se4_spi`, 6 MHz).
  - IRQ on GPIO39, reset on GPIO33.
  - Supplies: vdd L10C, vcc_i2c L1C.
  - Up to 10 touch points.
  - Coordinates are reported at 10800x24000, 10x the panel resolution.
- **Driver name `fts_ts`.** It registers into `xiaomi_touch` (TouchFeature) [SRC].
- The kernel embeds Xiaomi's panel-specific firmware **`fw_ft3658_l11r.i`** and has `FTS_AUTO_UPGRADE_EN 1`. At probe it compares the firmware version in the IC with the built-in host firmware and **reflashes if they differ** (`fts_fwupg_need_upgrade`: `fw_ver_in_tp != fw_ver_in_host`). `FTS_GET_MODULE_NUM 0` means it does no vendor or module-ID check [SRC: LineageOS kernel focaltech_3658u]. The stock HyperOS kernel is presumably the same Xiaomi driver [UNVERIFIED].
- TouchFeature modes come from `xiaomi_touch.h`. They include 0 Game, 9 Report_Rate, 10 Fod_Enable, 11 Aod_Enable, **14 Doubletap_Mode**, 15 Grip and 19 Power_Status [SRC].

### 4.3 Fingerprint

- **Side-mounted capacitive sensor in the power key** [OFFICIAL "Side fingerprint sensor"]. The location string `1080|965|115` means the right edge, centre y=965 px, 115 px long, and is used for the SystemUI side-FPS indicator [SRC].
- Two second-source suppliers share the board, on the same GPIO23 (IRQ) and GPIO24 (reset) [SRC: munch-sm8250.dtsi]:

| Supplier | Kernel driver | HAL | Input device |
|---|---|---|---|
| **Goodix** | `goodix,fingerprint`, non-FOD `gf_spi` | `fingerprint.goodix.so` (with `libgf_ca.so`, `libgf_hal.so`, `libgoodixhwfingerprint.so`) | `uinput-goodix` |
| **FPC** | `fpc,fpc1020` (FPC1020-family TEE driver) | `fingerprint.fpc.so` | FPC equivalent |

- **This phone reports `uinput-goodix`, so it has the Goodix side sensor.** The exact Goodix part number is [UNVERIFIED]. The `_FOD` (optical, under-display) drivers exist in the shared sm8250 tree but are **not enabled for munch** [SRC: munch.config].
- The LineageOS munch tree does not set `TARGET_HAS_UDFPS` [SRC].

### 4.4 Why double-tap-to-wake fails with the replacement screen (driver-level analysis)

Source: [SRC: LineageOS kernel `drivers/input/touchscreen/focaltech_3658u/focaltech_core.c` and `focaltech_gesture.c`]. Interpretation is [INFERENCE].

The path when the ROM writes TouchFeature mode 14 = 1:

1. `fts_set_cur_value(Touch_Doubletap_Mode, 1)` calls `fts_update_gesture_state()`.
2. **That function returns early if the TP is already suspended.** It logs `"TP is suspended, do not update gesture state"`. If the framework or HAL sends mode 14 only *after* screen-off, the request is ignored. The value must be set while the screen is on, for example at boot or when the setting changes, and it persists in `gesture_status`.
3. Otherwise it sets `gesture_status |= 0x01` and `gesture_mode = ENABLE`. AOD (mode 11) sets bit 0x02.
4. On suspend (`fts_ts_suspend`), with `gesture_mode` set and `poweroff_on_sleep` false:
   - The driver writes 0xFF to gesture registers 0xD1/0xD2/0xD5-0xD8, then writes `0xD0 = 1` and reads it back, up to 5 tries.
   - Success logs `"Enter into gesture(suspend) successfully"`.
   - Failure logs `"make IC enter into gesture(suspend) fail,state:%x"`.
   - The touch IRQ is kept as a wake source (`enable_irq_wake`).
5. In the IRQ, the gesture packet's `buf[0]` must equal ENABLE, otherwise the log reads `"gesture not enable in fw"`. Gesture ID **0x24** (double click) is translated to `KEY_WAKEUP`.

Likely failure points with a non-original screen:

- **(a) Touch-IC firmware without the gesture engine.** Aftermarket OLED assemblies come with their own touch controller and firmware. That is often a cloned or alternate FocalTech-compatible part, tuned by the panel assembler, which can lack Xiaomi's low-power gesture (0xD0) implementation. The driver then fails at step 4 or step 5. Normal touch keeps working, because the base reporting protocol is the same.
- **(b) The firmware auto-upgrade fights the part.** If the IC is FT3658U-compatible, the stock driver tries to reflash Xiaomi's `l11r` firmware whenever the versions differ. Either the reflash succeeds, and Xiaomi's firmware runs on a sensor pattern it was not tuned for, or it fails each boot. Check dmesg for `fw version in tp:%x, host:%x` and the upgrade result.
- **(c) Panel power in suspend.** On the original Samsung panel the touch controller stays powered through doze. An aftermarket panel with a different power-up sequence, or an **incell/TDDI LCD copy** where touch lives inside the display driver IC, loses touch when the panel is blanked. Gesture wake then becomes impossible in hardware. This phone still probes `fts_ts`, which suggests an on-cell FocalTech controller rather than TDDI, but the IC firmware version and lockdown info should be checked.
- **(d) Proximity gating.** Xiaomi suppresses wake gestures when the proximity sensor reads "near". munch uses **Elliptic Labs ultrasound proximity** (`sensors.elliptic.so`, `libultrasound.so`, `ro.vendor.audio.us.proximity=true`, `CONFIG_US_PROXIMITY=y`) plus `sensors.mius.proximity.so` [SRC]. This path is unaffected by screen optics, but it can stick at "near" if the earpiece or ultrasound path is disturbed after a repair. Repairers report that proximity faults cause tap-to-wake failures on other phones [3P: iFixit answers].

**Quick checks on the phone** (for the other agent; not run here):

```
dmesg | grep -iE "fts|focal|gesture"
cat /proc/tp_lockdown_info
cat /proc/tp_info
```

Look for:
- `Enter into gesture(suspend) successfully` or `...fail`;
- `gesture not enable in fw`;
- `TP is suspended, do not update gesture state`;
- the firmware version in the TP vs the host.

The `fts_gesture_mode` sysfs attribute shows `Reg(0xD0)`.

### 4.5 Ambient-light sensors and their relevance to the replacement panel

The vendor sensor configs list the following [SRC: proprietary-files.txt]:

| Sensor | Part | Role |
|---|---|---|
| Front light / colour | **ams TCS3701** | RGB/clear ALS + proximity front end, designed to sit **behind an OLED** [OFFICIAL: ams-osram, EDN] |
| Rear light | **ROHM BU27030** | `bu27030_0_back` |
| IMU | ST LSM6DSO | accelerometer and gyro |
| Compass | AKM AK991x | magnetometer |
| SAR | Semtech SX932x / SX933x | antenna SAR proximity |

Xiaomi markets this as a "360 deg Ambient Light Sensor" [OFFICIAL].

- **Implication [INFERENCE]:** if the front TCS3701 sits behind the display (the usual design for this part), an aftermarket OLED with a different stack and transmittance shifts the factory ALS calibration. Auto-brightness then reads too dark or too bright, and the colour sensor can misjudge white balance. The vendor `sensors/calibratedCheck.json` and `judge_calibrated.json` hold factory-calibration checks.

### 4.6 Aftermarket screens in general (what to expect)

- **Incell TFT LCD copies.** Sellers say these cannot support optical under-display fingerprint and that AOD is limited or unavailable, with lower contrast and higher power draw [3P: REWA soft-vs-hard OLED blog and similar]. On munch the fingerprint is on the side, so that limitation does not apply. Expect loss of AOD efficiency, no true black, likely broken DC-dimming, and possibly broken gesture wake (TDDI powers down).
- **Hard and soft OLED copies.** These are self-emissive, so AOD works, but colour and brightness calibration (QDCM `38_08_0a` calibration and gamma) do not match. HBM and peak brightness are usually lower. The touch layer and controller are supplier-specific (see 4.4).
- No POCO F4 or K40S-specific forum report on replacement-screen DT2W was found. The general pattern (tap-to-wake lost after third-party screens, proximity-seal fixes) is reported for other phones [3P: iFixit, GrapheneOS forum].

---

## 5. Audio, haptics and other peripherals

| Component | Part / spec | Source |
|---|---|---|
| Speakers | Dual stereo: 1216 "super-linear" bottom speaker + 1012 top/earpiece speaker; Dolby Atmos; Hi-Res certified | [OFFICIAL] |
| Smart amplifiers | **2x NXP TFA98xx** (I2C 0x34 and 0x35, IRQ GPIO113/112; `tfa98xx.cnt` firmware). The exact TFA98xx sub-part is [UNVERIFIED]. No Qualcomm WSA (`qcom,wsa-max-devs = <0>`) | [SRC: munch-sm8250.dtsi, munch-audio-overlay.dtsi] |
| Codec | Qualcomm WCD938x; FSA4480 USB-C audio switch (no 3.5 mm jack; adapter in box) | [SRC], [OFFICIAL] |
| Haptics | X-axis linear motor [OFFICIAL]. Driver: **Awinic AW8697**, with **AW86927** as a second source (both parameter sets in the DT). `CONFIG_INPUT_AW86927_HAPTIC=y`; firmware `aw8697_haptic.bin` and `aw8697_rtp_1.bin`. f0 is about 130 Hz (AW8697) or about 170 Hz (AW86927 preset) | [SRC] |
| IR blaster | Yes [OFFICIAL]. HAL `android.hardware.ir-service.lineage` (SPI-driven IR, `ir-spi` in xiaomi-sm8250-common.dtsi) | [SRC] |
| NFC | **NXP SN100U** (`libsn100u_fw.so`, `libnfc-nxp*.conf`); regional availability | [SRC], [OFFICIAL] |
| Wi-Fi | Wi-Fi 6 (802.11ax) 2x2 + 4x4 MIMO cellular. The chip is **Qualcomm QCA6390** (FastConnect 6800; `qcom,cnss-qca6390` in kona.dtsi; `BOARD_WLAN_DEVICE := qcwcn`) | [SRC], [OFFICIAL] |
| Bluetooth | 5.2 [OFFICIAL Xiaomi spec]. Fonearena's "5.1" is a K40S pre-launch error. Same QCA6390 combo chip | [OFFICIAL] |
| GNSS | GPS L1+L5, Galileo E1+E5a, QZSS L1+L5, GLONASS L1, BeiDou B1I+B2a, NavIC | [OFFICIAL] |
| Battery | 4500 mAh (typ), 67 W turbo (in-box charger); PD 3.0, QC3 | [OFFICIAL], [3P] |
| Charging ICs | Dual charge pump TI **BQ2597x** with Lion Semi **LN8000** as second source; PM8150B SMB5 (USB ICL 6.2 A, FCC max 12.4 A, Vfloat 4.48 V, FFC); fuel gauge TI **BQ27Z561**; battery authentication Maxim **DS28E16** | [SRC: munch.config, munch-sm8250.dtsi] |
| Cooling | "LiquidCool 2.0": 3112 mm2 vapour chamber + 7-layer graphite | [OFFICIAL overview] |
| Thermistors | DT zones include `cpu_therm` (near SoC), `flash_therm` (near flash FPC), `wireless_therm`, XO, and others on PM8150/PM8150L/PM8150B ADCs, governor `user_space` (controlled by Mi thermald) | [SRC] |

---

## 6. Official software history (brief)

| Track | Version line (Global, MIXM) | Android | First stable |
|---|---|---|---|
| MIUI 13 | 13.0.1.0 - 13.0.6.0 SLMMIXM | 12 | 2022-04/06 |
| MIUI 14 | 14.0.1.0 - 14.0.6.0 TLMMIXM | 13 | 2023-01 |
| HyperOS 1 | OS1.0.1.0 - OS1.0.12.0 ULMMIXM (internal `V816.x`) | 14 | 2024-04 (Mi Pilot), 2024-05 stable |
| HyperOS 2 | **Not released for the POCO F4**. Only the POCO F4 GT is on Xiaomi's HyperOS 2 list | - | - |

Sources: [3P: miuirom.org, Gizchina, xmfirmwareupdater]. Our vendor `V816.0.9.0.ULMMIXM` is HyperOS 1.0.9.0 (recovery ROM 2025-04-15). A newer 1.0.12.0 build exists (2026-05-06) [3P: miuirom.org, unverified against Xiaomi].

---

## 7. Tuning implications for our port (HyperOS 4 / Android 17 on HyperOS 1 vendor)

### 7.1 Camera

- **Per-variant capability gating.** Detect the main sensor at runtime (the coordinator's props give `munch_sunny_ov64b40_wide`, or the `com.qti.sensormodule.*` in use) and advertise only what Xiaomi enabled:

| Variant | Allow | Never advertise |
|---|---|---|
| OV64B40 (this phone) | 4K 60/30, 1080p 60/30, 720p; slow-motion at the 1080p120/240 and 720p ladder that the vendor HAL actually exposes | **8K** and **4K120** |
| IMX582 (K40S) | 4K30 max | 4K60 |

  For 8K and 4K120: the Spectra 480 and OV64B silicon could do 8K30, but there is no munch tuning or thermal validation for it. Remove these from any Android 17 or HyperOS 4 camera feature XML, MIUI camera `device_features`, or "camera capability" overlays copied from newer devices.
- **Ultrawide and macro limits.** Ultrawide max 1080p, macro max 720p-class. Disable 4K for the ultrawide lens in multi-camera zoom transitions. Otherwise the app must crop or switch and may crash or black-screen.
- **Front camera.** 1080p30 is safe. 1080p120 is only listed for the K40S, so expose it only if the vendor HAL returns it in stream configurations.
- **Aux/privileged camera lists.** Keep `vendor.camera.aux.packagelist` (LineageOS uses `org.codeaurora.snapcam,com.android.camera,org.lineageos.aperture,org.lineageos.aperture.dev`). For HyperOS the Xiaomi camera package is `com.android.camera` and must be in the aux list (and in `persist.vendor.camera.privapp.list` if the vendor uses it) to see the ultrawide and macro physical cameras. Add Google Camera or other apps only if they will be used. The aux list exposes the hidden IDs: 2 (ultrawide) and 3 (macro), using the kernel slots, with the Camera2 ID to be confirmed on device.
- **Tuning bins.** Never mix tuning bins across module sources (Sunny vs OFilm vs AAC). The HAL picks the tuned bin by the module EEPROM ID. A ported vendor overlay that replaces `com.qti.tuned.munch_*` with another device's bins will break AWB, AF and LSC.
- **Stabilisation.** OIS is not AP-controllable, so don't ship OIS toggles that write CamX OIS settings. EIS is Vidhance (vendor), so keep `vidhance_calibration` and `eisoverridesettings.txt` intact.
- **ZSL.** LineageOS sets `camera.disable_zsl_mode=true`. The ISP limit is 64 MP@30 single-camera ZSL and 25 MP dual-camera ZSL, so do not enable dual-camera ZSL at 64 MP.

### 7.2 CPU and GPU

**CPU frequency and boosting:**
- Keep `schedutil` with LineageOS's 500 us up / 20 ms down rate limits as the baseline.
- The prime-core top OPP (3187.2 MHz) costs about 37% more power for 12% more frequency. A sustained or thermal cap at **2841.6 MHz** on cpu7 (and about 2265.6 MHz on cpu4-6 when hot) gives much better performance per watt.
- Keep launch and touch boosts short: LAUNCH 5 s, INTERACTION min freqs about 1.17 / 1.29 / 1.19 GHz.

**Scheduler interface:**
- The kernel is 4.19 with schedtune, not cgroup-v2 uclamp.
- The Android 17 `task_profiles.json` must map to **`/dev/stune`** (schedtune) attributes. If the port's task profiles assume uclamp (`cpu.uclamp.min`), top-app boosting silently does nothing. **[INFERENCE, verify on device]**
- Keep the cpusets from section 1.5. Add the `camera-daemon` group.

**GPU:**
- Max 670 MHz. Use `max_pwrlevel 1` (587 MHz) for SUSTAINED_PERFORMANCE and gaming-thermal.
- The Adreno 650 driver is in the vendor. Android 17 may expect Vulkan 1.3 features that Adreno 650 on a HyperOS 1 vendor does not expose. Keep `android.hardware.vulkan.level-1` and `version-1_1` permission XMLs consistent with the actual vendor driver; don't spoof a higher version.

**Memory bandwidth:** Keep the bw_hwmon/LLCC hints. The DDR maximum is 2750 MHz.

### 7.3 Thermal

- Use the vendor Mi thermald with `sconfig` scenes (0, 8, 9, 10, 11, 12, 14).
- Map HyperOS 4 scene hints to these IDs. In particular, set camera to 12 and video recording to the vendor's `thermal-video`/`-4k` profile.
- Do not enable `thermal-nolimits` by default.
- The DT thermal governors are `user_space`, so all throttling is userspace (thermal-engine). If thermald fails on the new system (sepolicy or socket path), the phone runs **unthrottled**, so verify it is running.

### 7.4 Display

- Refresh levels 60, 90 and 120 Hz only. Don't add 144 Hz or 30 Hz modes, even though the SoC supports QHD+ 144.
- Set `ro.surface_flinger.use_content_detection_for_refresh_rate=true`, idle timer 80 ms, touch timer 200 ms (as in LineageOS).
- Brightness:
  - DSI range 1..2047.
  - The original panel gives about 455 nits sustained manual, 900 nits HBM and 1300 nits peak.
  - The replacement panel's nits-per-level will differ. If auto-brightness feels wrong, re-measure and adjust `config_screenBrightnessNits` and the auto-brightness curve, or the HyperOS equivalent.
  - The vendor QDCM file `38_08_0a` is calibrated for the original panel, so colour modes may look off on the replacement.
- Wide colour and HDR: `has_wide_color_display=true`, `has_HDR_display=true`, `persist.sys.sf.native_mode=2`, `color_mode=9`. Keep these from the vendor.

### 7.5 Touch, double-tap and fingerprint with the aftermarket screen

- **Set expectations.** DT2W depends on the replacement touch IC firmware supporting the FocalTech 0xD0 gesture mode. If dmesg shows gesture-enter failure or "gesture not enable in fw", **no ROM change can fix it** short of flashing compatible touch firmware, which is risky. The fallback is "raise to wake" or tilt-to-wake (`sns_tilt_to_wake.json` exists).
- **ROM-side fix to try first.** Make sure mode 14=1 is written **while the screen is on**, once at boot after `fts_ts` probe and on every settings change, never only on screen-off. The driver drops updates while suspended.
- **Diagnostics before blaming the panel.**
  - Look for "Enter into gesture(suspend) successfully" in dmesg after screen-off.
  - If the message is present and taps still don't wake the phone, check that the Elliptic proximity is not stuck at "near" and that the framework handles `KEY_WAKEUP` from `fts_ts`.
- **Fingerprint.** It is the Goodix *side* sensor, independent of the display.
  - For weak response: re-enrol, with more coverage of the finger edges.
  - Clean the power key.
  - Check whether the power-key or side-FPS flex was disturbed during the screen replacement (the frame is opened for it) [INFERENCE].
  - Make sure the vendor Goodix HAL stack is intact: `fingerprint.goodix.so` plus `libgf_*` and the TEE TA.
  - Keep `persist.vendor.fingerprint.type=side` and the `sensor_location` prop so HyperOS 4 treats it as side-FPS. Don't enable UDFPS overlays.
- **Touch feel.** 360 Hz sampling is the stock rate. The `focaltech,touch-range-array`, `-def-array` and `-expert-array` DT values are TouchFeature game-mode presets, and they apply on any panel with a compatible IC.

---

## 8. Sources

**Official (manufacturer):**
- Xiaomi UK - POCO F4 Specs: https://www.mi.com/uk/product/poco-f4/specs/ (fetched via curl; storage/RAM type, CPU, display incl. 360 Hz / DCI-P3 / brightness, camera f-numbers and video list, side fingerprint, NFC, IR, X-axis motor, BT 5.2)
- Xiaomi UK - POCO F4 Overview: https://www.mi.com/uk/product/poco-f4/ (E4 AMOLED, 60/90/120 Hz, 64MP OIS, 1216 + 1012 speakers, LiquidCool 2.0 3112 mm2 VC)
- Qualcomm Snapdragon 870 5G product brief (PDF): https://www.qualcomm.com/media/documents/files/snapdragon-870-5g-mobile-platform-product-brief.pdf
- Qualcomm SD870 product page: https://www.qualcomm.com/smartphones/products/8-series/snapdragon-870-5g-mobile-platform
- Qualcomm press release (Jan 2021): https://www.qualcomm.com/news/releases/2021/01/qualcomm-announces-boosted-snapdragon-870-5g-mobile-platform
- OmniVision OV64B: https://www.ovt.com/products/ov64b/
- OmniVision OV8856: https://www.ovt.com/products/ov8856/
- ams-OSRAM TCS3701: https://ams-osram.com/products/sensors/ambient-light-color-spectral-proximity-sensors/ams-tcs3701-color-and-proximity-sensor
- EDN on TCS3701 behind-OLED: https://edn.com/optical-sensor-measures-ambient-light-behind-an-oled-screen

**Source trees:**
- LineageOS device tree munch (lineage-23.2): https://github.com/LineageOS/android_device_xiaomi_munch (BoardConfig.mk, device.mk, vendor.prop, libinit/libvariant_xiaomi_munch.cpp, proprietary-files.txt, rro_overlays/FrameworkResOverlayDevice/res/xml/power_profile.xml and values/config.xml)
- LineageOS sm8250-common (lineage-23.2): https://github.com/LineageOS/android_device_xiaomi_sm8250-common (rootdir/etc/init.qcom.power.rc, configs/powerhint.json, parts/.../ThermalUtils.java, kona.mk, vendor.prop, system.prop, BoardConfigCommon.mk, proprietary-files.txt)
- LineageOS kernel sm8250 (lineage-23.2): https://github.com/LineageOS/android_kernel_xiaomi_sm8250
  - arch/arm64/configs/vendor/xiaomi/munch.config
  - arch/arm64/boot/dts/vendor/qcom/munch-sm8250.dtsi, munch-sm8250-camera-sensor-mtp.dtsi, munch-sm8250-camera-board.dtsi, munch-audio-overlay.dtsi, kona-v2-gpu.dtsi, kona.dtsi
  - drivers/input/touchscreen/focaltech_3658u/ (focaltech_config.h, focaltech_core.c, focaltech_gesture.c, focaltech_flash.c, include/firmware/fw_ft3658_l11r.i)
  - drivers/input/touchscreen/xiaomi/xiaomi_touch.h
  - drivers/input/fingerprint/goodix/gf_spi.h
- MiCode Xiaomi kernel, branch munch-s-oss: https://github.com/MiCode/Xiaomi_Kernel_OpenSource/tree/munch-s-oss (munch_user_defconfig, munch charger drivers; no panel dtsi published)
- LineageOS alioth proprietary-files (same QDCM panel ID): https://github.com/LineageOS/android_device_xiaomi_alioth

**Third-party:**
- GSMArena POCO F4: https://www.gsmarena.com/xiaomi_poco_f4-11627.php
- GSMArena Redmi K40S: https://www.gsmarena.com/xiaomi_redmi_k40s-11431.php
- Fonearena K40S launch specs (48MP IMX582, 20MP 0.8 um front, side FPS, LPDDR5/UFS 3.1): https://www.fonearena.com/blog/359046/redmi-k40s-price-specifications.html
- XDA - Snapdragon 870 announcement and spec table: https://www.xda-developers.com/qualcomm-unveils-snapdragon-870/
- 9to5Google - SD870 overview: https://9to5google.com/2021/01/19/qualcomm-snapdragon-870/
- helpix sensor DB: IMX596 https://helpix.ru/isensor/sony_imx596/ ; IMX582 https://helpix.ru/isensor/sony_imx582/ ; GC02M1 https://helpix.ru/isensor/galaxycore_gc02m1/
- Unbox PH (POCO F4 = K40S global, E4, side FPS): https://unbox.ph/gadget/poco-f4-launching-on-june-23-redmi-k40s-global-variant/
- miuirom.org POCO F4 firmware list: https://miuirom.org/phones/poco-f4
- Gizchina - POCO F4 HyperOS (Android 14): https://www.gizchina.com/2024/04/26/poco-f4-gets-hyperos-update-based-on-android-14/
- xmfirmwareupdater OS1.0.1.0.ULMMIXM: https://xmfirmwareupdater.com/hyperos/munch/stable/OS1.0.1.0.ULMMIXM
- REWA - soft vs hard OLED / incell limitations: https://shop.rewa.tech/blog/detail/soft-oled-vs-hard-oled.html
- iFixit - tap-to-wake / fingerprint issues after screen replacement (general): https://www.ifixit.com/Answers/View/456411/ ; https://pt.ifixit.com/Answers/View/788748/Fingerprint+Sensor+Not+Working+After+Screen+Replacement
- GrapheneOS forum - Pixel 7 DT2W lost after screen replacement: https://discuss.grapheneos.org/d/11115-screenreplacement-pixel7
- XDA - POCO F4 strange touch problem (software, MIUI 14): https://xdaforums.com/t/poco-f4-strange-touch-problem.4710085/

**Device ground truth:** coordinator-supplied vendor props from this phone (OV64B40 Sunny main, OV8856 AAC ultrawide, IMX596 OFilm front, GC02M1 Sunny macro, DW9800V actuator).
