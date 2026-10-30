# 02 — Kernel camera and video layer (MASTER_PLAN P3)

Status: **in progress** (started 2026-10-28). Source: port kernel tree `~/kernel_build/src` (Linux 4.19.325, `rohmanurip/kernel_munch`
base, same as the running kernel `4.19.325-zyndong-perf`) + live device nodes on the phone. Stock HyperOS 1.0.9 kernel (4.19.157) is
only available as a boot image (pendrive `stock_kernel_1.0.9/`). Tags: [Observed] / [Inferred].

## 1. Camera driver tree (`techpack/camera/drivers`) [Observed]
| Driver | .c files | Lines | Hardware / role |
|---|---|---|---|
| `cam_isp` | 30 | 56 101 | IFE/VFE front end (RAW in, stats, crop/scale), CSID; realtime pipeline |
| `cam_sensor_module` | 29 | 29 855 | sensor, CCI (I²C), CSIPHY, actuator, EEPROM, flash, OIS, sensor I/O, resource manager |
| `cam_icp` | 13 | 13 090 | ICP (A5 firmware CPU) controlling **BPS** (Bayer processing) and **IPE** (image processing: noise, sharpen, colour, LTM) |
| `cam_cpas` | 5 | 11 659 | camera power/bandwidth/clock voting (AHB/AXI), camnoc |
| `cam_req_mgr` | 7 | 9 608 | request manager: per-frame sync of sensor, ISP, flash, actuator |
| `cam_fd` | 6 | 5 439 | **hardware face detection** |
| `cam_utils` | 7 | 5 247 | common helpers (soc, io, packet, trace) |
| `cam_cdm` | 6 | 4 760 | camera DMA / register programming |
| `cam_lrme` | 6 | 4 694 | **LRME hardware motion estimation** (multi-frame alignment) |
| `cam_cust` | 7 | 4 593 | Qualcomm "custom HW" node framework (`qcom,cam-custom`) — not Xiaomi code |
| `cam_smmu` | 1 | 4 387 | camera IOMMU mapping |
| `cam_core` | 4 | 4 218 | context/node state machines |
| `cam_jpeg` | 9 | 4 088 | JPEG encoder + JPEG DMA (scaler) |
| `cam_sync` | 2 | 2 189 | sync objects (fences) between camera blocks |
| `cam_log` | 1 | 217 | logging |
Other media drivers: Venus video `techpack/video/msm/vidc` + `drivers/media/platform/msm/vidc_3x`, **CVP** `drivers/media/platform/msm/cvp`,
**NPU** `drivers/media/platform/msm/npu`, `synx`, display `sde`.

## 2. Active on this phone [Observed]
`/sys/class/video4linux` device names: 6× `cam-csiphy-driver`, 4× `cam-sensor-driver`, 4× `cam-eeprom`, 3× `cam-flash-dev`,
**1× `cam-actuator-driver`** (only the main camera focuses), `cam-isp`, `cam-icp`, `cam-jpeg`, **`cam-fd`**, `cam-cpas`, `cam-req-mgr`, `cam_sync`.
Bound platform drivers include `cam_vfe`, `cam-a5`, `cam-bps`, `cam-ipe`, `cam-jpeg-enc`, `cam-jpeg-dma`, `cam_lrme_hw`, `cam_fd_hw`,
`cam_custom`, `msm_vidc_v4l2`, **`msm_cvp_v4l2`** (`/dev/cvp`, group camera), **`msm_npu`** (`/dev/msm_npu`, system only).
* **No `cam-ois` device node** — traced 2026-10-28, see §7 "How OIS works on munch".

## 3. Venus video encoder on kona (`techpack/video/msm/vidc/msm_vidc_platform.c`, `msm_venc.c`) [Observed]
* HEVC profiles up to **Main10**; 10-bit input format **TP10 UBWC**; **HDR10+** per-frame metadata (`EXTRADATA_ENC_INPUT_HDR10PLUS`) and
  static **HDR PQ** information control → the encoder side of HDR10 video is fully present.
* Bitrate: HEVC and H.264 CABAC up to **160 Mbit/s**; B-frames (1), hierarchical-P up to 6 layers, 2 long-term refs, all-intra up to 240 fps.
* HEIC still images up to 16384×16384 (tiles 512×512).
→ U1 (HDR10 video) is blocked only by the camera side (no 10-bit stream for apps), not by the encoder.

## 4. Who uses CVP / NPU / DSP / GPU (lsof on the phone, 2026-10-28) [Observed]
| State | CVP `/dev/cvp` | NPU `/dev/msm_npu` | DSP `adsprpc-smd` | GPU `kgsl-3d0` |
|---|---|---|---|---|
| Camera closed | nobody | nobody | — | home, systemui, surfaceflinger, camera provider (2) |
| Photo | camera HAL (1) | **nobody** | camera HAL (1) | camera app 109, HAL 2 |
| Night | camera HAL (1) | **nobody** | camera HAL (1) | camera app 207, HAL 2 |
| Video | camera HAL (1) | **nobody** | camera HAL (1) | camera app 178, HAL 28 |
→ The NPU is not used by the camera at all; CVP and DSP are used by the HAL; the app's heavy work runs on the GPU.

## 5. Port 4.19.325 vs stock 4.19.157 kernel [Observed]
Symbol tables of the stock image cannot be decoded with `tools/kallsyms_dump.py` ("token table not found"), so the two boot-image kernels
were compared by their unique driver strings (C locale, `strings -n 8`):
| Area | Stock | Port | Only stock | Only port | Reading |
|---|---|---|---|---|---|
| Camera (`cam_`, `CAM_`, csiphy, cci) | 4975 | 5438 | 75 | 538 | port camera techpack is a **newer** Qualcomm release (extra VFE dump/debug functions, e.g. `cam_vfe_*_reg_dump`, `cam_vfe_top_query`) |
| Venus video | 1396 | 1399 | 7 | 10 | practically the same |
| GPU (kgsl) | 271 | 283 | 7 | 19 | practically the same |
| NPU | 186 | 166 | 21 | 1 | close; a few stock messages missing |
| Vision CVP (`msm_cvp`) | 923 | 110* | 858 | 45 | *port count is mostly the **audio** "voice CVP"; the port's vision-CVP driver has almost no log strings → different build/version; device ids (`qcom,kona-cvp`) and `/dev/cvp` present and used by the HAL |
| DSP FastRPC | 128 | 127 | 4 | 3 | same |
Still unknown: whether the newer camera techpack or the different CVP build changes behaviour (e.g. the back Portrait crash runs in the app,
not in the kernel; the stock kernel cannot boot Android 17 — `MODE_TEST_RESULTS.md`).

## 6. Processing stages and their tuning blocks [Observed: block lists; Inferred: order]
Kernel drivers only move buffers and program registers; *what* each stage does is set by the per-sensor Chromatix tuning
(`03_FIRMWARE_HAL.md` §4). Block names in the OV64B40 tuning file grouped by the hardware stage suffix:
| Stage | Kernel driver | Tuning blocks (OV64B40) | Role |
|---|---|---|---|
| **IFE** (front end, realtime, every frame) | `cam_isp` (`cam_vfe`, CSID) | `pedestal13`, `bls12` (black level), `linearization33/34`, `pdpc11/30` (PD/bad pixels), `bpcbcc50`, `abf34/40` (RAW denoise), `lsc34/40` (lens shading), `demux13`, `demosaic36/37`, `cc12/13`, `gtm10`, `gamma16`, `cst12`, `hdr30`, `bincorr10`, `ica20` | preview/video path, 3A statistics |
| **BPS** (Bayer processing, offline snapshot) | `cam_icp` → `cam-bps` | `pedestal13`, `bls12`, `linearization34`, `pdpc20/30`, `gic30` (green imbalance), `abf40`, `hnr10`, `lsc34/40`, `demux13`, `demosaic36`, `cc13`, `gtm10`, `gamma16`, `cst12`, `hdr30`, `bincorr10` | full-quality RAW → YUV for photos |
| **IPE** (image processing, preview + snapshot) | `cam_icp` → `cam-ipe` | `anr10` (multi-scale noise), `tf10/20` (temporal/multi-frame), `hnr10`, `lenr10` (luma edge noise), `asf30` (sharpening), `upscale20`, `cac22/23` (fringing), `cc13` (colour matrix), `cv12` (saturation/hue), `cs20` (chroma suppression), `cst12`, `gamma15`, `ltm14` (local tone), `tdl10` (3D LUT), `gra10` (grain), `ica10/20/30` (warp/LDC/EIS), `lrme10`, `sce11` (skin colour), `cvp10` | final look: noise, sharpness, colour, tone |
| **SW / HAL** (CPU/GPU/DSP) | — | `mf10/11` (multi-frame), `tmc12` (tone-map control), `tintless20`, `ldc10`, `eis10/11/12`, `shdr10`, `hdrvideo10`, `video10` | MFNR/HDR merge, EIS, LDC |
**For colour/detail tuning (P8):** the photo look is decided mostly in **IPE** (`asf30`, `anr10`/`tf20`, `cc13`/`cv12`/`tdl10`, `ltm14`/`gamma15`,
`sce11` skin) plus `gtm10` in BPS — these are the blocks to locate first if a Chromatix (L4) change is ever approved.
Hardware helpers outside this chain: `cam-fd` (face detection), `cam_lrme_hw` (motion estimation), JPEG encoder/DMA.

## 7. How OIS works on munch (trace, 2026-10-28)
1. **Device tree [Observed]:** neither the stock HyperOS 1.0.9 munch overlay nor the port's has a `qcom,ois` node (the 71 OIS entries in
   the stock dtbo belong to other Xiaomi boards: umi, cas, lmi, thyme, apollo, cmi, psyche). Camera bus = 4 sensors, 4 EEPROMs, 1 actuator.
   → the kernel camera OIS driver is never used on munch, in stock or port (not a port regression).
2. **Sensor-module file [Observed]:** the OV64B40 module config names actuator `munch_sunny_ov64b40_dw9800v_wide_actuator` and OIS
   **`munch_ois`**; no `com.qti.ois.*` library exists in stock or port vendor.
3. **Sensor hub [Observed]:** vendor has `sensors/proto/sns_ois_manager.proto`; `dumpsys sensorservice` lists Xiaomi **`ois_manager`**
   (`xiaomi.sensor.ois_sensor`, wakeup + non-wakeup) next to the **LSM6DSO** gyroscope — OIS runs on the SLPI sensor-hub DSP.
4. **Camera HAL link [Observed]:** the camera provider has `libsnsapi.so` and the QMI libraries (`libqmi_cci`, `libqmi_common_so`,
   `libqmi_encdec`) loaded → it talks to the sensor hub directly (not through Android's sensor service); CamX contains
   `ConfigureOISMode` / `CreateOISModeCmd` / `DualOISInitDone`.
5. **Live [Observed]:** with the camera open (Photo/Video) the LSM6DSO gyroscope gets 1 client in Android's sensor service; `ois_manager`
   does not appear there (expected if the HAL uses the direct sensor-hub client).
**Confirmed with test logging:** CamX `OIS device found on camera 0`, OIS gain calibration read from the main EEPROM, sensor hub `ois_manager init`.
**Conclusion [Observed at HAL level]:** main-camera OIS = Xiaomi OIS manager on the SLPI sensor hub, fed by the LSM6DSO gyro, configured by the
camera HAL through the sensor-hub API — same design as stock. **Not yet proven** that the lens is actively stabilised during capture on the
port → P8 test: handheld video/long-exposure photo, OIS on vs off (Pro mode / Camera2 `LENS_OPTICAL_STABILIZATION_MODE`), compare blur.
Side note: device tree camera difference stock → port = only `cam-sensor@2`/`eeprom2` third supply 1.21 V → 1.20 V (10 mV); rest renumbering.

## 8. Still to do in P3
- [x] Stage ↔ tuning-block map (§6).
- [x] Port vs stock driver comparison (§5).
- [x] Venus encoder limits (§3).
- [x] CVP / NPU / DSP / GPU users (§4).
- [x] `kernel_for_future/KERNEL_NOTES_2026-10-28.md` on the pendrive (build recipe, stock-kernel test, v1–v4 lessons, recovery).
