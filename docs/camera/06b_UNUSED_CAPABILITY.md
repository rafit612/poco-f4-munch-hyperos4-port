# 06b — Capability the hardware has but the shipped software does not use (MASTER_PLAN step 16, P5 audit)

Status: **first list** (2026-10-28). Each item: evidence → what to verify → where it could help. Nothing here is enabled yet; every item
goes through P7 (gain / risk / effort) and the N13 gate (must beat the reference and test results without crashes, lag or heat).
Tags: [Observed] evidence seen on the phone / in vendor files; [Inferred] conclusion still to verify.

| # | Capability | Evidence [Observed] | Verify | Possible gain |
|---|---|---|---|---|
| U1 | **HDR10 video recording** | CHI has `UsecaseVideo4kEIS3PreviewEIS2WithHdr10`, `RealTimeFeatureZSLPreviewRawYUVWithHdr10`; camera app logs `isCurrentDeviceSupportHdr10 AVAILABLE_CONFIGURATIONS is not defined` | HAL 10-bit stream configs, Venus HEVC Main10 encoder profile, app flag | 10-bit HDR video with more highlight range |
| U2 | **DSP stage of Xiaomi HDR** | `miai_hdr_config.yaml`: `algo_params_dsp: hdsr: enabled: false`; DSP program `libMIAIHDR_skel.so` present | what `hdsr` does (HDR super-resolution?), quality vs CPU path, timing | faster / better HDR merge, less CPU heat |
| U3 | **Sensor HDR (RAW HDR)** | OV64B40 sensor file has `HDR3ExposureInfo`, `ZZHDRInfo` (3-exposure / zig-zag HDR); `camxoverridesettings.txt` `enableRawHDR=0`; tuning has `hdr30`, `shdr10`, `hdrvideo10` blocks | which sensor modes support it, does the HAL pipeline work when enabled (test module) | single-shot HDR for moving scenes and video |
| U4 | **60 fps for third-party apps** | main camera AE fps ranges stop at 30 (`14–30, 15, 24, 25, 30`) while Xiaomi's camera records 60 | HAL can stream 60 fps in a normal Camera2 session | Instagram/YouTube/Open Camera 60 fps |
| U5 | **Main-camera ISO above 877 for apps** | Camera2 sensitivity range 50–877 (front 50–3200) | sensor analog/digital gain limits in the sensor file | better third-party low light |
| U6 | **Video RAW capture** | `UsecaseVideoWithRawCapture` in CHI | which app path triggers it | RAW frames for own video denoise/grade |
| U7 | **NNAPI on GPU / HVX / HTA for all apps** | `android.hardware.neuralnetworks@1.3-service-qti` with `unnhal-acc-{adreno,hvx,hta,common}` | NNAPI devices list on Android 17, TFLite delegate works | own AI denoise / segmentation / SR stage (step 16 build path b) |
| U8 | **Hexagon DSP + HTA tensor accelerator for camera AI** | `libSNPE`, `libPSNPE`, `libhta`, `libhta_hexagon_runtime`, `libsnpe_dsp_domains*`, DSP skels `libcamera_nn_skel`, ArcSoft `hdrplus/beauty` HVX skels | free DSP time during capture, which shipped `.dlc` models already run there | move heavy AI from CPU/GPU to DSP |
| U9 | **CVP (computer-vision processor)** | `libcvpdsp_skel.so` | what the camera uses it for (motion estimation / feature tracking?) | multi-frame alignment, EIS, tracking at low power |
| U10 | **Adreno 650 GPU compute** | `libOpenCL.so`, CamX `com.qti.node.gpu.so`, depth/ANC engines already on OpenCL | GPU load during capture / preview | own LUT / tone / sharpening / merge stage (step 16 build path b) |
| U11 | **13 app modes switched off** | `support()` false: Fastshot, Instant photo, Director mode, Supermoon, Underwater, Live cinematography, AI Watermark, Night video, AI Capture Assist, Long exposure v2, … (`01_APP_OS_LAYER.md` §3) | which need hardware we lack vs only a flag | extra modes (e.g. Night video, Supermoon with Almalence configs present) |
| U13 | **NPU (Snapdragon 870 tensor accelerator)** | kernel driver `msm_npu` bound, `/dev/msm_npu`, `npu_cc-kona`; HTA runtime `libhta*` and NNAPI `unnhal-acc-hta`; **never opened by the camera in Photo/Night/Video** (lsof, P3 §4) | which apps/models use it; access from our own stage via NNAPI | fastest/lowest-power AI denoise/segmentation |
| U14 | **Hardware face detection + LRME motion estimation** | kernel `cam-fd`, `cam_lrme_hw` active (P3) | used by HAL today? (FD for AF/AE, LRME for MFNR) | cheaper face/motion data for our own stage |
| U15 | **Higher video bitrate** | Venus HEVC/H.264 up to 160 Mbit/s (P3 §3); owner's clip 2026-10-28: **4K 60 fps HEVC = 50 Mbit/s** (AAC 319 kbit/s) | bitrates for 4K30 / 1080p60 / 1080p30; detail gain vs file size at 80–100 Mbit/s | cleaner 4K detail, fewer blocks in motion |
| U12 | **8K preview pipelines** | `RealTimeFeatureZSLPreviewRawYUV8k(WithHdr10)` | sensor 8K mode + encoder limits (likely not for SD870 recording) | probably none — listed to close it out |

Settled / not possible:
* **Macro through ultra-wide autofocus (plan N11):** the ultra-wide is fixed-focus → not possible.
* **Third-party apps getting 4K60 / 8K recording:** depends on U4 and the Venus encoder; 8K recording is not expected on SD870.

## Still to verify
- [x] U1 HDR10 (2026-10-28): encoder `c2.qti.hevc.encoder` up to 4096×2304 (240 fps at 1080p; Main10 profile still to read at runtime).
  Main camera Camera2 capabilities: BACKWARD_COMPATIBLE, CONSTRAINED_HIGH_SPEED_VIDEO, **RAW**, YUV/PRIVATE_REPROCESSING, READ_SENSOR_SETTINGS,
  MANUAL_SENSOR, BURST_CAPTURE, MANUAL_POST_PROCESSING — **no DYNAMIC_RANGE_TEN_BIT and no P010 stream** → HDR10 is not available to
  standard apps; only Xiaomi's vendor path (CHI `…WithHdr10` usecases) could provide it → test in P8 with the native camera only.
  **Closed 2026-10-30:** the native app's HDR10 check (`isCurrentDeviceSupportHdr10`) needs the HAL's 10-bit stream configurations
  (`AVAILABLE_CONFIGURATIONS` not defined on munch) and the HAL advertises no 10-bit/P010 output; the encoder side (Venus, HEVC) is not
  the blocker. Enabling it would mean adding 10-bit stream configs to the HAL's static metadata (HAL change, same class of risk as C3)
  → **not pursued**. HDR video on this phone = the app's normal video HDR (tone mapping), not HDR10.
- [x] U7 NNAPI device list on Android 17 (2026-10-30, own probe `tools/camera_lab/nnapi_probe/`, run as adb shell, no root): runtime feature
  level 8; devices `qti-default`, `qti-dsp` (ACCELERATOR), `qti-gpu` (GPU), `qti-hta` (ACCELERATOR), all NNAPI 1.3 (feature level 30, driver
  `1.3-22.01:build_kona`), plus `nnapi-reference` (CPU). → an own AI stage (C4) can reach DSP/HTA/GPU through NNAPI without root.
  Caveat: NNAPI is deprecated in new Android releases (still present in Android 17); a TFLite/LiteRT build with the NNAPI delegate is the simplest path.
- [x] U2 what `hdsr` is: HDR + super-resolution on the cDSP (8 EV0 + 1 short frame, zoom 1–20x), off in three config switches;
  test kit c2b ready (`MODE_TEST_RESULTS.md` C2 follow-up), A/B needs root + window scene.
- [x] GPU load during Photo / Video (2026-10-30, `MODE_TEST_RESULTS.md` P5 load budget): GPU 3-4 % mean, ≤ 12 % peak → large budget
  for U10; CPU 28-45 %. DSP load not readable without vendor tools (open).
