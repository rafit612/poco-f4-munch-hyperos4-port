# GCam (LMC 8.4) tuning for POCO F4 (munch) with the OV64B40 main sensor

Date: 2026-10-23. Scope: research plus static file analysis only. Nothing was flashed or pushed to the phone, and no adb or fastboot was used. `secure_build/` was not touched.

Device ground truth comes from `camera_dump.txt`, `camera_dump_after.txt` and `audit/agents/hardware/HARDWARE_REPORT.md`:
main OV64B40 (Sunny), UW OV8856 (AAC), macro GC02M1 (Sunny), front IMX596 (OFilm).
The app in use is Hasli LMC8.4 **R16** Snapcam (`org.codeaurora.snapcam`).

---

## 1. Short answer

1. **No config on the web names "OV64B40" or "OmniVision variant".** No such variant tag exists. The global POCO F4 *is* the OV64B variant (GSMArena and Celso Azevedo both say "64MP OmniVision OV64B"). The IMX582 module (`munch_ofilm_imx582_wide`) belongs to the Chinese Redmi K40S hardware. Configs shared in the **POCO F4** community (Telegram @PocoF4Photography, XDA munch thread) were therefore made on OV64B phones.
2. **The best base for this phone is `POCO-F4-FINAL.xml`.** It descends from **BubNois v2** (Telegram @Bubnois, 2024-10/11), which is itself built on **KCPD 4.1** (color) and **PP v4E** (noise and sharpness). Its manual main-camera CCM matches the CCM that this phone's OV64B40 HAL reports to within about 0.02 per coefficient (section 4.2). That is hard evidence that it was tuned on an OV64B40 unit.
3. The `bubnois-v2` family has three problems on this ROM. The macro button is labelled "Wide". The aux slots use the wrong noise models (IMX363 instead of OV8856 and GC02M1). The main camera uses OnePlus vendor op-modes (`33041` "OPS EIS+OIS", night `61442` "QBC HDR"). Also, BubNois v2 was published for **LMC 8.4 R17** (file `bubnois_v2_lmc8.4.17.xml`), and you run R16.
4. **Alternative: `POCO-F4-ULTIMATE-.xml`** is Sachin Rai's **Pixel Perfect v3** (shared on XDA by Edilson-89) with 24 small edits. It uses the "Standard" color transform, which takes the CCM from camera metadata, so it is correct for whatever sensor is fitted. It has the correct UW noise model (39, OV8856) and the Xiaomi "Super Night" op-mode. Its output is 27 MP upscaled (x1.3).
5. **Black level and white level are not sensor-variant traps on this phone.** The HAL reports BL = 64/64/64/64 and WL = 1023 (10-bit) on all four sensors. Every local config already uses about 64. A wrong-variant config would show up as a wrong CCM or AWB preset, not as wrong BL/WL. The sample photos confirm this: shadows are neutral (1st-percentile RGB is equal, e.g. [3,3,3], [5,5,6]).

---

## 2. Lens / camera-ID map (this ROM, from `camera_dump.txt`)

| Camera2 ID | Sensor (module) | Facing | Raw size | CFA | BL / WL | Max exposure | ISO range | Use in LMC |
|---|---|---|---|---|---|---|---|---|
| **0** | OV64B40 64MP (Sunny), 4-in-1 binned to 16MP, f/1.79, 4.71 mm, OIS | back | 4624x3472 | BGGR | 64 / 1023 | 32.1 s | 50-877 (Xiaomi tag 50-6400) | Main (`back_1`) |
| **1** | IMX596 20MP (OFilm), binned 5MP, f/2.45 | front | 2592x1952 | RGGB | 64 / 1023 | 0.35 s | 50-3200 | Front (`front_1..5`) |
| **2** | OV8856 8MP (AAC) ultrawide, f/2.2, 1.65 mm | back | 3264x2448 | BGGR | 64 / 1023 | 9.99 s | 50-853 | **"Wide Camera" slot (`back_3`)** |
| **3** | GC02M1 2MP (Sunny) macro, f/2.4, 1.94 mm | back | 1600x1200 | RGGB | 64 / 1023 | 0.43 s | 50-600 | **"Tele camera" slot (`back_2`)** |
| 4 | Logical multi-cam (physical 0 + 2) | back | 4624x3472 | - | - | - | - | avoid |
| 5 | Main-sensor alias (Xiaomi aux) | back | 4624x3472 | - | - | - | - | optional ID5 |
| 6 | Front alias | front | 2592x1952 | - | - | - | - | not needed |

### How LMC 8.4 R16 names its slots

Verified from the APK's `res/xml/camera_preferences.xml` via `aapt2 dump xmltree`:

| LMC slot | ID key (default) | Enable key | Per-lens suffixes | Manual CCM index |
|---|---|---|---|---|
| Main | `pref_manual_cameraid_back_1_key` (0) | always | no suffix / `_main` | `rr_0..bb_0` |
| "Tele camera" | `pref_manual_cameraid_back_2_key` (2) | `pref_aux_tele_key` | `_2` / `_tele` | `*_2` |
| "Wide Camera" | `pref_manual_cameraid_back_3_key` (3) | `pref_aux_wide_key` | `_3` / `_wide` | `*_3` |
| ID4 | `back_4` (4) | `pref_aux_4_key` | `_4` / `_id4` | `*_4` |
| ID5 | `back_5` (5) | `pref_aux_5_key` | `_5` / `_id5` | `*_5` |
| Front | `front_1` (1) | - | `_front` | `*_1` |

**Correct munch mapping:** `back_1=0`, `back_2=3` (macro in the "Tele" slot), `back_3=2` (UW in the "Wide" slot), `front_*=1`. ID4 and ID5 can be pointed at `0` to get alternative "styles" of the main camera, which is what bubnois and PP do. Do **not** use 4 (logical), and use 5 only for testing.

Every POCO F4 config found on the web already uses `back_2=3, back_3=2`. The exceptions are `gCom` and `Best-Night-Mode`, which use 2 and 3 (a stock-MIUI generic layout). With 2/3 the UW sits in the Tele slot. This still works, because the per-slot tuning follows the slot, but the labels and per-lens settings then belong to the other lens.

Note: `pref_list_camera_key` = `0|1|20|21` in most configs was inherited from the author's ROM. IDs 20 and 21 do not exist here. This is harmless because `pref_enable_manual_array_key=1` with `0,1,2,3,4,5` is used.

---

## 3. Recommended configs and why

| Rank | Config | Author / origin | LMC build | Why | What to fix for this phone |
|---|---|---|---|---|---|
| **1** | `POCO-F4-FINAL.xml` (local) | BubNois v2, from KCPD 4.1 and PP v4E, tone/gamma "Leica-ish" edits made locally | made for R17, works on R16 | Main CCM matches the OV64B40 HAL. Manual BL 64.2. OV60A noise model (closest OmniVision quad-bayer in the list). Pixel 6 HDR+ model. Neutral output in the samples. | See 3.1 |
| 2 | `POCO-F4-ULTIMATE-.xml` (local) / `xda_Pixel-Perfect-v3.xml` | Sachin Rai "Pixel Perfect v3" (XDA, Edilson-89, 2024-01-24) | R17/R18 | Metadata CCM ("Standard"), so it is always correct for the installed sensor. UW noise model OV8856 (39). Xiaomi Super Night op-mode. | Macro noise model 117 (OV60A) is wrong; use 10 or 47. Output is upscaled to 27 MP (`pref_upscale` 13 = x1.3), a large file with no real detail gain. AWB preset 72 = "OV60A (X30 Front)". |
| 3 | `xda_Pixel-Perfect-V4-Extended.xml` (downloaded) | Sachin Rai PP v4E (XDA, 2024-05-30) | **R18** | Newest PP. It is the noise and sharpness source used by BubNois. Its own main CCM differs (`rr_0 1.543`, a softer, desaturated look). | Same slot mapping as bubnois. Test it on R18. |
| 4 | `celso_kcpd-2v.xml` (downloaded) | KCPD v2 ("R16_Hakuna_" prefix) | R16 | Made for R16. Correct labels (Macro=id3, Wide=id2). BL preset "64". Macro noise model GC02M1 (10). UW noise model ov8856 RN8P (107). | Older than KCPD 4.1. Main noise model 36 (OV48C). |
| - | `celso_SPYdr-Stable-v2.xml` | unknown | R16 | Correct ID mapping. | Gives the UW the GC02M1 noise model (wrong). System noise model on main. |
| - | `xda_PF4_Beasty_*_LMC8.4R15.xml` | Beasty07 (XDA, 2024-02-12) | R15 | - | **Needs its own lib** (`libs_key=-1`, a third-party lib that is not included). AWB 77 = **"IMX582 (X3Pro Main)"**, an IMX582-flavored preset. Do not use as-is. |
| - | `xda_ImgDynmx-9.xml` | sa2uration / Shubham Meena | **SGCam 8.4 (Shamim)**, not LMC | - | Wrong app. Reference only. |
| - | `celso_gCom.xml`, `celso_Best-Night-Mode-By-Ganesh-Patel.xml` | unknown / Ganesh Patel | R16 era | - | IDs 2/3 not swapped. Generic CT/noise models (Best-Night: CT 5 "HMX Mi Note 10", astro 15 s). |

**Newer builds:** Hasli's latest LMC 8.4 is **R18** (2023-06-14). Its notes say "configs from previous versions are suitable" and "fixed default AUX for many devices". There is also LMC 8.8 R2 (2025-01) and **LMC 9.6 Release 1 (2026-06-21, Android 12+, Snapcam variant available)**. No POCO F4 configs exist for 8.8 or 9.6, and none exist for BigKaka AGC 9.x (`.agc` format; the celsoazevedo 9.4 and 9.6 lists have no F4 or SD870 Xiaomi entries) or BSG MGC 9.x. If you move to 9.x you will tune from scratch. The ID map and BL/WL above still apply.

### 3.1 Edits recommended on top of `POCO-F4-FINAL.xml`

**Applied 2026-10-25** to all 12 configs in the ROM (`secure_build/payload_tele/product/etc/gcam/`): macro name, macro and
UW noise models (10 / 39) and aux AWB presets (58 / 50), indices re-checked against the R16 APK's arrays. Op-modes were
not changed in the configs (they need a photo A/B test); `POCO-F4-FINAL-XiaomiNight-test.xml` has `pref_opmode_key` 0 and
`pref_opmode_night_key` 32778 for that test. The installed LMC is R16 (versionName ends in .18, which is a build number).
The configs are copied to `/sdcard/LMC8.4/` after the first unlock (`munch_gcam_configs`, see ROM_HISTORY.md).

| Key | FINAL now | Suggested | Reason |
|---|---|---|---|
| `pref_aux_tele_key` | 0 (macro hidden) | 1 if you want macro | The "Tele" slot is the macro (id 3) |
| `pref_manual_camera_name_key_2` | `Wide` | `Macro` | The "Tele" slot is GC02M1 macro. The A2Z/bubnois-macro variants currently show two "Wide" buttons |
| `pref_noise_model_key_2` (macro) | 31 = IMX363_0 (LGV50) | **10** = GC02M1 by ARNOVA (or 47 GC02M1_Macro SAVITAR, 54 GC02M1_20) | Sensor-matched model |
| `pref_noise_model_key_3` (UW) | 31 = IMX363_0 | **39** = OV8856 by ARNOVA (PP v3 uses it; alternatives 58, 101, 107) | Sensor-matched model; BubNois himself notes UW artifacts |
| `pref_awb_key_2` / `_3` | 45 = Samsung HMX | 58 = GC02M1 (RN10 Macro) / 50 = OV8856 (RN9S Wide) or 76 = OV8856 (X3Pro UW) | Only used when Google AWB is on. The author advises keeping AWB off |
| `pref_opmode_key` (main) | 33041 = "OPS EIS+OIS" (OnePlus) | try **0** (default) | Vendor op-modes are OEM-specific. 33041 is a OnePlus value. Keep it only if A/B shows no difference or regression |
| `pref_opmode_night_key` (main) | 61442 = "QBC HDR" | try 0, or 32778 = Xiaomi "Super Night" (PP uses it), or 32787 "Super NIGHT YUV2Engine" (KCPD) | Same reason. Xiaomi op-modes 0x80xx are listed in LMC's own table |
| `pref_black_level_key_wide/_tele` | 11 (manual 64.2 / 64) | keep, or 4 (= "64") | HAL is 64 on all lenses |
| LMC build | R16 | consider **R17/R18** | BubNois v2 was released for R17. R18 keeps config compatibility |

---

## 4. Local config analysis (Android SharedPreferences XML)

### 4.1 Family tree (key-by-key diffs computed locally)

- `bubnois-v2.xml` is byte-identical (md5 `cd038a26...`) to celsoazevedo's `bubnois-v2.xml` (BubNois v2).
- `bubnois-v2-macro.xml` = bubnois + `pref_aux_tele_key 0→1` (1 key).
- `POCO-F4-munch-A2Z.xml` = bubnois + macro on, `black_level_tele/id5 8→11`, `exposure_tele/wide +3→0` (5 keys).
- `POCO-F4-munch-A2Z-zoom.xml` = the same 4 keys without macro.
- `POCO-F4-FINAL.xml` = A2Z-zoom minus macro, plus `camcorder.4k60fps/camera.60fps → false`, video 4K/1080p FPS_60→FPS_30, `max_zoom 16→10`, `ois_api_supported=true` (10 keys).
- `POCO-F4-{Pixel,Samsung,iPhone,Leica-Authentic,Leica-Vibrant,vivo-Zeiss}-style.xml` = FINAL with only `lib_contrast_2_key*` (contrast) and `pref_tonecurve_preset`/`pref_gammacurve_preset` changed (11 to 13 keys). For example, Pixel = tone 13 "HDRQuality" + gamma 4 "HDR Quality"; Leica-Vibrant = tone 57 "GCAM 8.6"; Samsung = tone 35 "Etalon (r0m10)" + gamma 13. **Color science (CCM, AWB, BL) is identical across all style variants.**
- `POCO-F4-ULTIMATE-.xml` (md5 `e2e10930...`, same as celsoazevedo's) = Sachin Rai **Pixel Perfect v3** + 24 changes (CT 4→0 on all lenses, `pref_aux_key 4→0`, aux picture size 2592x1944→1600x1200, exposure comps → -3, WB correction off on aux). It differs from FINAL in 1010 keys.

### 4.2 Sensor-relevant keys, with value meanings from the R16 APK's own `arrays`

| Key (main unless noted) | FINAL / bubnois / A2Z | ULTIMATE (PP v3) | Meaning / OV64B40 vs IMX582 verdict |
|---|---|---|---|
| `pref_color_transform_key` | **16 = Manual color** (`rr_0..bb_0`) | 0 = Standard (metadata) | LMC list: 0 Standard, 1 System, 2 Arnova fix, 4 IMX686 K30 Pro, ..., **15 "IMX582 Mi9T"**, 16 Manual. No local config uses 15 |
| `rr_0..bb_0` manual CCM | `[1.767 -0.592 -0.175; -0.354 1.716 -0.362; -0.093 -0.817 1.910]` | LMC default `[1.68 -0.94 0.258; -0.148 1.063 0.086; 0.119 -0.914 1.83]` (unused, CT=0) | **This phone's OV64B40 HAL ForwardMatrix1 (D65) → sRGB = `[1.748 -0.587 -0.161; -0.349 1.703 -0.354; -0.008 -0.809 1.817]`**. FINAL matches it, so it is **tuned for OV64B40**. Caveat: a fixed D65 matrix does not adapt under tungsten (HAL FM2 → `[2.063 -0.796 -0.267; ...]`) |
| `rr_4..` (ID4 "SOFT") | `[1.609 -0.609 0.008; -0.133 1.320 -0.188; -0.008 -0.648 1.664]` | default | A desaturated variant for the "SOFT" style button (ID4 → id 0) |
| `pref_color_transform_key_2/_3` (macro/UW) | 2 = Arnova fix | 0 Standard | Generic; "Standard" uses each sensor's own metadata |
| `pref_color_transform_key_front` | 4 = IMX686 Redmi K30 Pro | 0 | No IMX596 preset exists |
| `pref_black_level_key_main` | **11 = Manual**, `bl0..bl3_key_main = 64.2` | 11, 64.2 | List: 0 System, 1 Dynamic, 2 "0", 3 "16", 4 "64", 5 "80", 6 "100", 7 "256", 8-10 "64 by Artz/BSG/MOD", 11 Manual. HAL = 64, so 64.2 is +0.2 DN (negligible deeper blacks). Same value for IMX582 or OV64B40 (both 10-bit, BL 64) |
| `pref_black_level_key_wide/_tele` | 11 (bl 64.2 / 64) | wide 0 System, tele 11 | All fine (HAL 64) |
| `pref_black_level_key_front` | 0 System | 0 | Fine (HAL 64) |
| `pref_dbl_key_main/_wide/_id4` | 100 = "10%" | 100 | "Dynamic Black Level" percentage (list 0%-100%). Effect is undocumented; leave it |
| `pref_white_level_key*` | 0 = Automatic | 0 | List: 0 Auto, 1023, 4095. HAL WL = **1023** on all sensors, so Auto is correct. Never pick 4095 (that is for 12-bit sensors) |
| `pref_model_key` (HDR+ model) | **14 = Pixel 6 (oriole)**; wide 11 = Pixel 4a 5G; tele(macro) 14; front 11 | 15 = Pixel 6 Pro (raven); tele 11, wide 11, front 14 | Model list 0-18, Pixel to Pixel 7 Pro. Pixel 6/6 Pro is what all modern F4 configs use |
| `pref_device_key` | 0; front 11 (Pixel 4a 5G) | 18 (out of list range) | Device-spoof list goes 0-13 |
| `pref_noise_model_key` | **117 = OV60A (EdgeX30)** | 117 | No OV64B entry exists in R16. OV60A (OmniVision 0.61 µm quad-bayer) is the closest. IMX582-flavored options would be 56 "IMX582_new_0 (PocoX3Pro)" and 81 "IMX582_0 (MI11X)". No local config uses them |
| `pref_noise_model_key_2` (macro) | 31 IMX363_0 (LGV50) | 117 OV60A | Both wrong; use 10/47/54 (GC02M1) |
| `pref_noise_model_key_3` (UW) | 31 IMX363_0 | **39 OV8856 by ARNOVA** | PP is right |
| `pref_noise_model_key_front` | 67 S5KGM1_0 (RN7) | 82 S5K3T2_1 (MI11X) | No IMX596 entry; generic |
| `pref_awb_key` (Google-AWB preset) | 18 = Sony IMX586 | 72 = OV60A (X30 Front) | Only active with the AWB button. Beasty uses 77 = **IMX582 (X3Pro Main)** |
| `pref_awb_key_2/_3` | 45 Samsung HMX | 45 / 45 | Better: 58 GC02M1, 50/76 OV8856 |
| `pref_fix_awbgains_key_*`, `WB_correction_key*`, `CCT_WB_intensity`, `pref_satCCT*` | AWB-gain fix on; CCT WB correction on; intensity 0.6 main | WB correction off | Look/WB taste controls, not sensor-specific |
| `pref_grgb_back_key` | 3 = Pixel 4 (G/B/G/R green-split calib) | 3 | CFA order comes from metadata (BGGR here), so this is not a variant trap |
| `pref_opmode_key` | 33041 = "OPS EIS+OIS" | 0 default | OnePlus vendor mode on a Xiaomi HAL. See 3.1 |
| `pref_opmode_night_key` | 61442 = "QBC HDR" | 32778 = Xiaomi "Super Night" | See 3.1 |
| `pref_samsungfix_key` | -1 "Fix enable" | 0 Auto | Samsung-specific workaround; leave it |
| `pref_merge_key_*` | 1 = SABRE merge | 1 | Normal |
| `pref_gcam_lens_logic_key` | main 1 = "Rear (High Quality)", aux 0 Auto, front 2 = "Front" | `_2`=5 "Rear Telephoto (SR zoom)" for the macro (odd), `_3`=9 "Rear Wide (NR)" | For the UW, 9 is the better choice |
| `pref_upscale_key` | 10 = x1.0 (native 4624x3472) | 13 = x1.3 (6010x4512, as seen in `PixP_...jpg`) | Upscale adds size, not detail |
| `pref_frames_hdr_key` / `pref_zsl_frames_key` | 13 / 27 | 22 / 22 | Frame counts (R16 max 28) |
| `pref_c2a_key` | 1 = HARDWARE LEVEL 3 | 0 Auto | HAL is LEVEL_3, so 1 is correct |
| `pref_exposure_max_back_key` | 5 = Max. exposure time | 5 | HAL allows 32 s on main |
| `pref_aemode_astro_key` | 4 = 4.0 s per frame | 7 = 15 s | See section 5 |
| `pref_aeautomax_key` | 7 = 1/7 s; front 12 = 1/15 s | same | Handheld auto max shutter |
| `pref_auto_ns_key` | 1 = Always (auto Night Sight) | 1 | - |
| `libs_key*` | 0 Google | 0 | No external lib needed (good) |
| `prefix_key` | `F4_` | `PixP_` | Filename prefix (matches sample names) |

### 4.3 Sample-photo check (`scratchpad/photos/`, LMC files)

All the LMC shots are from the main camera (4.71 mm, f/1.79, `HDR+ 1.0.414775603`). FINAL, Leica-Authentic and Leica-Vibrant are 4624x3472. PixP (ULTIMATE) is 6010x4512.

Shadow 1st-percentile RGB was neutral in every file (e.g. FINAL `[5,5,6]`, lmc `[3,3,3]`, PixP `[2,2,2]`) and shadow crush was 0-0.5%. **There is no black-level color cast.** That fits the HAL BL of 64 being honored.

One file (`020261023_181016_lmc_8.4`) has slightly cyan-green highlights (p99 `[224,237,233]`). This depends on the scene. If it happens repeatedly, lower `CCT_WB_intensity` or use Google AWB with the sensor-matched preset.

---

## 5. Night / astro settings for this hardware

- The main camera (OV64B40) is the only lens worth using for Night Sight or astro: up to 32.1 s per frame, OIS, f/1.79. The UW tops out at 9.99 s, the macro at 0.43 s and the front at 0.35 s, so astro on the aux lenses is pointless.
- `pref_exposure_max_back_key = 5` (max) lets GCam use the long HAL exposures. Keep it.
- `pref_aemode_astro_key` (per-frame astro shutter; LMC list: 0 = 1/5 s ... 4 = 4 s, 5 = 7 s, 6 = 10 s, 7 = 15 s):
  - **4 s (4)**: the safe default on SD870 (less heat and hot-pixel noise; works on a steady surface).
  - **10 s (6)**: for a real tripod under dark skies.
  - **15 s (7)**: what PP v3 and Best-Night use. Risk of hot pixels and warmth on a 0.7 µm sensor.
  - Celso's F4 review saw a 4 min 06 s astro capture with default settings.
- `pref_aeautomax_key = 7` (1/7 s) for handheld Night Sight on main is a sensible OIS-backed value. Use 5 (1/5 s) or more only with very steady hands.
- `pref_opmode_night_key`: A/B test `0`, `32778` (Xiaomi Super Night) and `61442`. Keep whichever gives the cleanest result with no HAL errors. None of these modes are documented for munch.
- Noise model for night: keep main 117 (OV60A). With "System model" (0) the noise-model setting is ignored (Hasli R16 note). `pref_iso_noise_key = 4` (dynamic ISO coefficient) is the default and is fine.

---

## 6. Downloaded configs (new folder; XML only, no executables)

`/home/odoo-dbsl/poco f4 5g 8gb 256gb munch/gcam_download/research_configs/`

| File | Source | md5 |
|---|---|---|
| `celso_kcpd-2v.xml` | celsoazevedo.com/files/android/p/f/2023/04/kcpd-2v.xml | 6e51fa39... |
| `celso_SPYdr-Stable-v2.xml` | .../p/f/2023/04/SPYdr-Stable-v2.xml | 001ac8d6... |
| `celso_gCom.xml` | .../p/f/2023/04/gCom.xml | d958fa88... |
| `celso_Best-Night-Mode-By-Ganesh-Patel.xml` | .../f/download/2023/Best-Night-Mode-By-Ganesh-Patel.xml | d5aba45a... |
| `xda_Pixel-Perfect-v3.xml` | XDA attachment 6059233 (via web.archive.org) | 2737e682... |
| `xda_Pixel-Perfect-v4.xml` | XDA attachment 6086608 (archive) | 5b077c12... |
| `xda_Pixel-Perfect-V4-Extended.xml` | XDA attachment 6108203 (archive) | ec8aebab... |
| `xda_PF4_Beasty_ExtraDetail_LMC8.4R15.xml` | XDA attachment 6067576 (archive); needs a missing lib | fbefee18... |
| `xda_PF4_Beasty_LessNoise_LMC8.4R15.xml` | XDA attachment 6067577 (archive); needs a missing lib | 479d988e... |
| `xda_ImgDynmx-9.xml` | XDA attachment 6185158 (archive); SGCam, not LMC | 19362420... |

`bubnois-v2.xml` and `POCO-F4-ULTIMATE-.xml` were also fetched, found byte-identical to the local copies, and removed as duplicates.

Not obtainable without the Telegram app: BubNois original posts (t.me/PocoF4Photography/115997, /117707), KCPD 4.1, PF4_DSLR_V1 (Beasty & Vizz) for R17.

---

## 7. Method notes and caveats

- Value meanings come from the **R16 APK's own resource tables**: `aapt2 dump resources` / `xmltree` on `gcam_download/LMC8.4_R16_Snapcam.apk` (arrays `pref_color_transform`, `black_level`, `white_level`, `model`, `device`, `pref_noise_model`, `pref_awb`, `opmode`, `pref_aemode_astro`, `gcam_lens_logic`, and the key-to-title map from `camera_preferences.xml`). This is static reading only; the APK was not run.
- HAL CCMs were computed as XYZ(D50) → Bradford → sRGB(D65) × ForwardMatrix1/2 from `camera_dump.txt`, with each row normalised to sum to 1. HAL-derived manual CCMs for the other lenses, if you want manual CT on them:
  - UW (id 2): `[2.208 -1.000 -0.208; -0.481 1.863 -0.382; -0.078 -1.464 2.541]`
  - Macro (id 3): `[2.014 -1.090 0.075; -0.175 1.525 -0.350; -0.038 -0.880 1.918]`
  - Front (id 1): `[1.715 -0.662 -0.053; -0.112 1.150 -0.038; 0.214 -1.296 2.081]`

  "Standard" CT (0) gives the same matrices with illuminant interpolation and is simpler.
- XDA is behind Cloudflare (403), so the thread and attachments were read from web.archive.org snapshots dated 2025-10/11.
- The op-mode advice is based on vendor-ID provenance (LMC's own labels). It has not been verified on the device.
- The meaning of `pref_dbl` (dynamic black level %) is not documented anywhere I could find.

---

## Sources

- Celso Azevedo, Config files for Hasli's LMC8.4_R16+ (POCO F4 / K40S list): https://www.celsoazevedo.com/files/android/google-camera/f/configs-hasli-02/
- Celso Azevedo, GCam for the Poco F4: https://www.celsoazevedo.com/files/android/p/gcam-poco-f4/
- Celso Azevedo, Poco F4 review (sensors OV64B / OV8856 / GC02M1 / IMX596, binned-resolution limit, astro 4:06): https://www.celsoazevedo.com/poco-f4-review/
- Celso Azevedo, useful links (Telegram @PocoF4Photography, XDA munch thread): https://www.celsoazevedo.com/files/android/google-camera/links/
- BubNois GCam F4 config article (KCPD + PP v4E basis, requires LMC R17): https://telegra.ph/BubNois-GCam-F4-Config-10-04 ; read-me image: https://www.celsoazevedo.com/files/random/2025/bubnois-v2.png
- Telegram posts: https://t.me/PocoF4Photography/117707 (bubnois_v2_lmc8.4.17.xml), https://t.me/PocoF4Photography/115997 (BubNois v1), https://t.me/gcamlm/340 (LMC R17 release)
- XDA "GCam for Poco F4 (munch)" thread (Pixel Perfect v2-v4E by Sachin Rai, PF4 Beasty R15, PF4_DSLR R17, ImgDynmx/SGCam): https://xdaforums.com/t/gcam-for-poco-f4-munch.4503565/ (read via web.archive.org snapshots 20251027/20251030)
- Hasli release pages: R16 https://www.celsoazevedo.com/files/android/google-camera/dev-hasli/f/dl12/ , R17 .../dl13/ , R18 .../dl14/ , index (LMC 8.8 R2, LMC 9.6 R1) https://www.celsoazevedo.com/files/android/google-camera/dev-hasli/ , LMC 9.6 R1 .../dl22/
- BigKaka AGC 9.4 / 9.6 config lists (no F4 entries): https://www.celsoazevedo.com/files/android/google-camera/f/configs-bigkaka-08/ , https://www.celsoazevedo.com/files/android/google-camera/f/configs-bigkaka-09/
- K40S camera module variants (munch_sunny_ov64b40_wide vs munch_ofilm_imx582_wide): https://github.com/godvmxi/magisk-module-fix-redmi-k40s-camera
- GSMArena POCO F4 review (camera hardware): https://www.gsmarena.com/poco_f4-review-2443p5.php
- Local: `camera_dump.txt`, `camera_dump_after.txt`, `audit/agents/hardware/HARDWARE_REPORT.md`, `gcam_download/LMC8.4_R16_Snapcam.apk` (resources), `gcam_download/*.xml`, sample photos in the session scratchpad.
