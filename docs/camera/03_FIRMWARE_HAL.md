# 03 — Firmware and vendor camera HAL (MASTER_PLAN P4)

Status: **in progress** (started 2026-10-28). Source: the phone's `/vendor` (identical to stock HyperOS 1.0.9 for the camera libraries
checked so far). Xiaomi/Qualcomm files are not copied into this repo; text configs are kept on the pendrive
(`camera_project/p4_vendor_camera_configs/`, 21 files). Tags: [Observed] / [Inferred].

## 1. Installed camera modules on this phone [Observed]
`persist.vendor.camera.mi.module.info` = `back_main=ov64b40_i; back_ultra=ov8856_i`, `infoext` = `front_main=imx596_i; back_macro=gc02m1_i`.
| Camera | Sensor | Module maker | Evidence |
|---|---|---|---|
| Main (id 0) | OV64B40 64 MP | **Sunny** | actuator `com.qti.actuator.munch_sunny_ov64b40_dw9800v_wide_actuator.so` loaded |
| Ultra-wide (id 2) | OV8856 8 MP | **AAC** | CamX probe + bokeh label |
| Front (id 1) | IMX596 | **OFilm** | CamX probe (test logging) |
| Macro (id 3) | GC02M1 2 MP | Sunny or OFilm — open | both module files exist |
The vendor also carries the second POCO F4 build variant (OFilm **IMX582** main) — not used on this unit.

## 2. Camera stack files [Observed]
* HAL core: `/vendor/lib64/hw/camera.qcom.so` (CamX, 9.4 MB), `com.qti.chi.override.so` (CHI, 4.9 MB).
* Per module: `com.qti.sensor.munch_<sensor>.so` (driver), `com.qti.sensormodule.munch_<maker>_<sensor>_<pos>.bin` (modes, OV64B40 966 KB),
  `com.qti.tuned.munch_<maker>_<sensor>_<pos>.bin` (**ISP tuning: colour, AWB, noise, sharpness, tone**), EEPROM and actuator drivers.
  Tuning sizes: OV64B40 39.6 MB (`tuned.default.bin` has the same size → likely a copy), OV8856 AAC 26.7 MB, IMX596 10.6 MB, GC02M1 5.8 MB,
  IMX582 (unused) 67.2 MB.
* 3A: `com.qti.stats.{aec,awb,af,afd,asd,haf,pdlib,pdlibsony}` (+ wrappers, `hafoverride`).
* CamX nodes: depth, eisv2/eisv3, fcv, gpu, ldc, remosaic, softisppost, stich, swregistration, customhw, memcpy, dummy rtb/sat; HVX: binning, addconstant.
* Xiaomi nodes: `com.mi.node.{aiasd, hdr, mimovie, realtimebokeh, rearvideo, skinbeautifier, superlowlightraw, videobokeh, watermark}`,
  ArcSoft `smoothtransition` (zoom switch).
* `/vendor/etc/camera` (72 files): 20 video-filter LUT PNGs (102–128), Almalence SR configs (wide/64M/tele), DLC neural models
  (`ai_enhance`, `model_back/front`, `seg_quantized`, `det_quantize`, `goturn_*` tracking, `reid_float`), beauty styles (`.cng`),
  `mibokeh_855_*`, `bokehParams.json`, `miai_hdr_config.yaml`, `hdrd_ui9_params.config`, `sceneDetection.xml`, Vidhance calibration,
  CFR params (W / UW / T_2x), `model/` (depth/segmentation networks).

## 3. HAL-wide switches: `camxoverridesettings.txt` [Observed]
Levers for later phases (changing any of them = per-change approval, test module first):
| Setting | Value | Note |
|---|---|---|
| `enableRawHDR` | 0 | RAW HDR off |
| `enable3ADebugData`, `enableTuningMetadata` | FALSE | turning on (test only) embeds AE/AWB/AF decisions → essential for colour tuning in P8 |
| `pdafHWEnable` | TRUE | hardware phase-detect AF |
| `enableOISOptimization`, `oisMaxWaitingTime` | TRUE, 50 | |
| `overrideFlashTorchCurrent` / `overrideFlashlightCurrent` | 500 / 150 | flash current (mA) |
| `enableSensorHWSync`, `multiCameraFrameSync` | 1, 1 | multi-camera sync (bokeh/SAT) |
| `vsquality` | `5@30|6@30` | video stabilisation quality |
| `algoNormalSupportedValue` / `algoHQSupportedValue` | `0:99|21:99|1:39|G:33` / `0:66|21:66|1:6|G:0` | algorithm quality levels |
| `minReprocessInputWidth/Height` | 8000×6000 | |
| feature flags | `ismfnrbokehsupported`, `isSuperPortraitSupported`, `isVideoBokehSupported`, `isVideoLogformatSupported`, `isVideoMimovieSupported`, `isVideoFilterSupported` = TRUE | |
| logging | all masks 0, `systemLogEnable` TRUE | raise only for debugging |

`eisoverridesettings.txt`: EIS margin 20 % (width/height), Super EIS 35 % × 51 % (UW 35.5 % × 51.7 %), LDC grid on, frame delay 30.

## 4. Main camera tuning file: what is inside [Observed]
`com.qti.tuned.munch_sunny_ov64b40_wide.bin` (39.6 MB, Qualcomm **"QTI Chromatix Header"** format; `com.qti.tuned.default.bin` is
byte-identical). Block names with the number of tuned instances (per usecase / lighting trigger), from the strings in the file:

| Area | Blocks (instances) | What it decides |
|---|---|---|
| Noise reduction | `anr10_ipe` (79), `tf20_ipe` (79, temporal/multi-frame), `hnr10_ipe` (48), `lenr10_ipe` (37), `abf40_ife/bps` (31/27, RAW), `mf11_sw` (13) | noise vs detail per ISO |
| Sharpening | `asf30_ipe` (74), `upscale20_ipe` (7) | edge strength, halos |
| Colour | `cc13_ipe/bps` (13/7, colour matrix), `cv12_ipe` (31, saturation/hue), `cs20_ipe` (24, chroma suppression), `cst12` (colour space), `tdl10_ipe` (7, 3D LUT) | colour rendering, saturation, skin |
| Tone | `gamma15_ipe` (22), `ltm14_ipe` (17, local tone), `gtm10_bps` (7, global tone), `tmc12_sw` (7) | contrast, shadows/highlights |
| Lens/optics | `lsc34/40` (shading), `cac22/23_ipe` (colour fringing), `ica10/20/30` (warp/LDC), `ldc10_sw`, `pdpc*` (PD/defect pixels), `gic30_bps`, `bls12`, `pedestal13`, `linearization33/34` | corners, fringing, distortion |
| Other | `gra10_ipe` (17, grain), `cvp10_ipe` (20), `lrme10`, `sce11`, `demux13`, `tintless20_sw` | |
| HDR | `hdr30_ife/bps`, `shdr10_sw`, `hdrvideo10_sw` | sensor/staggered HDR |
| 3A | `CCTTables`, `AWBExtensionParam`, `awbSceneChangeConvergeV1`, `AECParamExtension`, `CCTBasedExpComp`, `aecGyro/Depth/MultiCamSync/SkipCtrl`, `AFAlgoTuning`, `PDAF`, `AFMONITOR`, `AFaceLumaAssist`, `ASDTuningData`, `AFDTuningData` (flicker), `SpotLightTuning`, flash `flashWV1/flashDecV1/ledTorchV1` | white balance, exposure, focus, flicker |

**Consequence for P8 [Inferred]:** colour/noise/sharpness of the main camera are decided here, per usecase and lighting zone. Editing this
binary needs the Chromatix layout (Qualcomm tool, not available) → keep to the safer layers first (L1 app profile, L2 request params/vendor
tags, L3 own LUT/tone/sharpen stage) and treat Chromatix edits as L4 (per-change approval, only for values we can locate exactly).

## 5. HDR, portrait denoise and bokeh configs [Observed]
* `miai_hdr_config.yaml` (Xiaomi MIAI HDR, model **L11R** = POCO F4/K40S): frame alignment (global block 28 px, search 48, local
  cross-filter), deghost, Laplacian merge with luma/chroma LUTs (selfie set shown), CLAHE 0.9–1.1. **`algo_params_dsp: hdsr: enabled: false`**
  — the DSP part of HDR is switched off → candidate for step 16 (unused DSP capability).
* `hdrd_ui9_params.config` (ArcSoft HDR-D AE table): same row for every camera (wide, front, tele, ultra, macro, bokeh): lux 250–300,
  contrast 0.5–0.7, DRC 2–4, EV set like −12 / +6 (units to confirm) → no per-camera HDR tuning.
* `miai_psn_config.yaml`: daylight above 275 lux; deep-learning denoise below 250 lux or above ISO 230 (front 0.3–0.6, back 0.3–0.7 weight),
  NLM 7/3; portrait sharpening 3.2/2.0/2.0/2.0; face light/contrast/gamma 0.
* `bokehParams.json`: 10 generic numbers + data path `/data/vendor/camera/`.
* Also copied for later: `hdrcheckerparamsettings.yml`, `sceneDetection.xml`, 13 Almalence super-resolution configs (wide, wide 64M, tele variants).

## 6. HAL pipelines (CHI override) [Observed]
`com.qti.chi.override.so` names 133 usecases/features/pipelines. Groups:
* **Realtime features**: `RealTimeFeatureZSLPreviewRaw{,YUV,Front,Ultra,LAZ,Mimoji}`, `...YUV8k`, `...YUV8kWithHdr10`, `...YUVWithHdr10`,
  `...EIS2Pro`/`NoEISPro`, `SuperNightPreviewRaw`, `NZSLSnapshotRDI`, `ThirdCamera`.
* **Multi-frame / offline**: MFNR `Prefilter → Blend → PostFilter` (+`Aux` for the second camera), **SWMF** RAW merge (`MergeRaw`,
  `MergeIdealRaw`, `MergeSoftIsp`, `MergeYuv`), `SuperNightMergeYuv`, `OfflineNoiseReprocess(+Aux)`, `OfflineFusionSnapshot`, `BokehSnapshot`.
* **Usecases**: ZSL/Snapshot/Preview/Raw/Raw8, `UsecaseQuadCFA` (64 MP full resolution), `UsecaseRTB` (bokeh), `UsecaseSAT` (zoom
  switching), `UsecaseDualCamera`, `UsecaseDepth1/2`, `UsecaseAmbilight`, `UsecaseVideoHFR` (slow motion), video with EIS2/EIS3/SUPER-EIS3(PRO),
  `UsecaseVideo4kEIS3PreviewEIS2WithHdr10`, `UsecaseVideoWithRawCapture`, `UsecaseVRVideo`, `UsecaseVTCam`, `UsecaseSecurePreview`, many
  YUV/JPEG reprocess usecases.
* **Unused-capability candidates [Inferred, to verify in P5/P7]**: HDR10 video pipelines exist, while the app logs
  `isCurrentDeviceSupportHdr10 AVAILABLE_CONFIGURATIONS is not defined` → HDR10 recording may be possible but not offered; 8K preview
  pipeline names exist (8K recording needs sensor/encoder support — check); video RAW capture usecase.

## 6b. Pipeline, sensor mode and tuning branch per camera mode (2026-10-30) [Observed]
CamX info/config logging switched on for one sweep (runtime bind-mount of `camxoverridesettings.txt`, reverted; no crash), modes opened
by the guarded `mode_sweep.py`, one logged Photo shot. Source lines: `SetRealtimePipeline() … Selected Sensor Mode`,
`FindBestSensorMode() FORCING SENSOR MODE`, IPE `DumpTuningModeData()`.

| Mode | Opmode | Realtime pipeline | Sensor output | Chromatix branch (sensor mode · usecase · feature1/feature2) |
|---|---|---|---|---|
| Photo | 0x9005 | RealTimeFeatureZSLPreviewRaw | 4624×3472 (CHI forces sensor mode 1, binned) | preview s1·u0·0/0; **photo frames** `ZSLSnapshotYUVHAL` IPE3 s1·**u1**·0/0 (×5 burst), JPEG `VTCamJpegEncodeNoCustomNode` |
| Video (4K) | 0x803c | RealTimeFeatureZSLPreviewRawYUV | 3840×2160 (mode 3) | s3·u0·0/20 |
| Night | 0x800a | RealTimeFeatureSuperNightPreviewRaw | 4624×3472 (mode 1) | s1·u0·0/18 (own night branch) |
| Ultra HD | 0x9004 | ZSLPreviewRaw + RealTimeFeatureNZSLSnapshotRDI | 4624×3472 preview, **9248×6944** remosaic for the shot | s1·u0·0/0 |
| Pro (video) | 0xf010 | RealTimeFeatureZSLPreviewRawYUV | 4624×2608 (mode 2) | s2·u0·0/19 |
| Slow motion | 0x1 | PreviewVideoHFR | 1920×1080 (mode 4, HFR) | s4·u2·0/0 |
| Panorama | 0x8008 | Snapshot | 4624×3472 | s1·u0·0/11 |
| Movie | 0x8032 | PreviewVideo | 4624×3472 | s1·u0·0/0 |

* Photo frames use the Chromatix branch sensor 1 / usecase 1 / feature 0/0 — exactly the blocks the L4 t1b test replaced → confirms the
  HAL snapshot ANR is not what makes native photos soft (`REFERENCE_LIBRARY.md`). The 5 snapshot frames are merged afterwards in the
  app's MIA engine (no MFNR prefilter/blend IPE passes appear in the HAL log for Photo).
* Night, Pro and Video have their own feature2 branches (18 / 19 / 20) → night/video look can be tuned separately from Photo (L4).
* Only Ultra HD reads the 64 MP remosaic (RDI 9248×6944); every other mode uses binned or cropped modes.

## 7. Still to do in P4
- [x] Pipeline catalogue (§6) + which pipeline / sensor mode / tuning branch each mode selects (§6b, CamX-logged sweep 2026-10-30).
- [x] OV64B40 tuning file structure (§4). Next: same for UW/front/macro, then locate exact values.
- [x] HDR, portrait denoise and bokeh notes (§5).
- [x] Firmware images compare across MIUI 13 (V13.0.6.0) / MIUI 14 (V14.0.6.0) / HyperOS 1 (OS1.0.12.0), pendrive firmware sets
  (2026-10-30, §8).
- [x] `default_prop` denials (616): the HAL properties under that label are `persist.camera.xiaomi.algoup` and `persist.camera.eebin.write`.
  Neither is set on the phone nor in stock HyperOS 1.0.9, and stock has no property rule for them either → same default value as stock;
  harmless log noise, no fix needed.

## 8. Processor firmware across munch releases (2026-10-30) [Observed]
Camera-relevant firmware sits in two places: `dsp.img` (DSP partition: shared DSP libraries) and `modem.img` (NON-HLOS FAT: `adsp`, `cdsp`,
`npu`, `venus`, `cvpss` images). The CamX ICP (ISP) firmware is in the vendor partition, not in these sets.

| Image | MIUI 13 (V13.0.6.0) | MIUI 14 / HyperOS 1 (OS1.0.12.0) | Running on the phone (`/sys/devices/soc0/images`) |
|---|---|---|---|
| `dsp.img` | identical hash in all three releases | same | — |
| cDSP (HDR/hdsr, NNAPI dsp/hta) | CDSP.HT.2.3-00602 | same version (re-signed build) | CDSP.HT.2.3-00602 |
| aDSP | ADSP.HT.5.3-00614 | same version | ADSP.HT.5.3-00614 |
| NPU | NPU.FW.2.0-00185 | same version | NPU.FW.2.0-00185 |
| CVP (motion/feature engine) | CVP.VPU.1.0-00054 | same version | — (not listed) |
| Venus (video codec) | VIDEO.VPU.1.0-00094 | **VIDEO.VPU.1.0-00113** | VIDEO.VPU.1.0-00113 |

Result: the port already runs the newest official munch firmware for every camera/video/DSP processor. Only Venus changed across releases
(00094 → 00113); the DSPs and NPU did not change after MIUI 13. → No firmware upgrade path exists for camera quality; work stays in
vendor configs (L2), the app (v-builds) and an own processing stage (C4).
