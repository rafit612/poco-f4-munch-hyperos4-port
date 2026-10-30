# 01 — Camera app and OS layer (MASTER_PLAN P2)

Status: **in progress** (started 2026-10-28). Camera app: MiuiCamera 6.7.000070.0, build v6 of `tools/re/camera_watermark_patch.sh`.
Tags: [Observed] = seen on the phone or in the code; [Inferred] = conclusion not yet proven.

## 1. The chain, top to bottom [Observed]
```
Mode button (mode bar / "More" panel)
  → mode entry (u3.a registry, 55 entries)  → module class (e.g. PortraitModule)
  → module device (getOperatingMode → HAL session opmode, e.g. 0x9001 ALGO_UP, 0x9003 single bokeh, 0x9005 normal)
  → camera id mapper (C2.c getActualOpenCameraId: mode + facing + zoom → camera id 0–6)
  → Camera2 session (framework cameraserver → camera provider "legacy" HAL 3.5, CamX/CHI on kona)
  → capture result → app post-processing:
       MiCameraAlgo (Java) → libcamera_algoup_jni (MI_Algo_JNI) → vendor libmialgoengine.so (MIA session, node graph)
       → vendor algorithm libraries (libwa_depth / libanc_dc_base, ArcSoft, Almalence SR, MIALGO HDR, ...)
  → JPEG/HEIC → MediaStore (DCIM/Camera)
```
The app always runs the fixed **Marble** (POCO F5) device profile (`com.mi.device.Marble`), patched by us:
watermark POCO F4 5G, filter set 25 (Leica looks), bokeh width 4625, short-video generation 4 (see `CAMERA_PROJECT.md`).

## 2. Camera ids (HAL static metadata, `dumpsys media.camera`) [Observed]
| Id | Camera | Focal | Aperture | Pixel array | Notes |
|---|---|---|---|---|---|
| 0 | Main OV64B40 (64 MP) | 4.71 mm | f/1.79 | 4624×3472 | Photo/Video default |
| 1 | Front | 2.84 mm | f/2.45 | 2592×1952 | |
| 2 | Ultra-wide (8 MP) | 1.65 mm | f/2.2 | 3264×2448 | "0.6" zoom, stereo partner for Portrait |
| 3 | Macro (2 MP) | 1.94 mm | f/2.4 | 1600×1200 | |
| 4 | Logical **bokeh** camera (main + ultra-wide) | 4.71 mm | f/1.79 | 4624×3472 | Back Portrait opens this; dual calibration 419 B, `xiaomi.dualcal.streamsize` 4624×3472 + 3264×2448, `bokehVendorID` 3 |
| 5 | Logical main (SAT/zoom) | 4.71 mm | f/1.79 | 4624×3472 | |
| 6 | Logical front | 2.84 mm | f/2.45 | 2592×1952 | |

## 3. Modes [Observed]
Full generated table: [`p2_modes_generated.md`](p2_modes_generated.md) (`tools/camera_lab/map_modes.py`).
* 55 mode entries: **41 always available, 13 switched off in this build, 1 conditional** (Legendary).
* Switched off (`support()` returns false): AI Capture Assist (168), Night video (214), AI Watermark (205), Long exposure v2 (191),
  Supermoon (188), Director mode (164), Fastshot (225), Equip street (229), Instant photo (228), Friend (226),
  Live cinematography (231), Underwater photo/video (233/234). → candidates for P7 (which of them work on SD870?).
* Same visible name, different modes: "Short video" = classic FunModule (161, 1080p); "Xiaomi Short Video" = MiLiveMaster (190, 720p,
  label changed in v6); old MiLive (183) is registered but not shown. "Long exposure" = Ambilight (187, visible) and LongExposure (191, off).

## 4. Session opmode per mode [Observed]
Full logged sweep on camera v7 (19 visible modes, no photo taken, back Portrait skipped): [`p2_mode_sweep_generated.md`](p2_mode_sweep_generated.md)
(`tools/camera_lab/mode_sweep.py`; opmode from `setOperatingMode`, MIA nodes from `createNode`). All modes use camera id 0 (main) except
back Portrait (4). **0 camera crashes.**

| Opmode | Modes | Meaning |
|---|---|---|
| 0x9005 | Photo, Documents, ID photo | ALGO_UP normal (MIA graph: HDR 7 → SkinBeautifier 10 → AIIE 2) |
| 0x9004 | Ultra HD | ALGO_UP HD (MIA graph 0x80f3, node 1) |
| 0x9001 | Portrait back (cam 4) | ALGO_UP dual bokeh (MIA graph 0x8002/0x301, node 24 JiiGAN) |
| 0x9300 | Long exposure (Ambilight) | |
| 0x800a | Night | SUPER_NIGHT (MIA graph 0x800a, node 1) |
| 0x803c | Video | video recording session (60 fps preview) |
| 0x8032 | Movie (Cinematic) | |
| 0x8019 | Xiaomi Short Video (MiLiveMaster) | |
| 0x8004 | Short video (classic), VLOG, Time-lapse, Dual video (with 0x8009) | |
| 0x8008 | Panorama | |
| 0xf010 | Pro | |
| 0x1 / 0x0 | Slow motion / Short film | constrained high-speed / normal |
Not opened by the sweep: Sticker avatars (needs a feature download), Movie effects (opens a template picker).

## 5. Post-processing engine (MIA) [Observed]
* `libmialgoengine.so` (vendor, identical to stock HyperOS 1.0.9) builds a node graph per session (`MiaSession::buildGraph`):
  Photo: HDR (type 7) → SkinBeautifier (10) → AIIE (2); Portrait back: `MiaNodeJiiGANCapBokeh` (type 24).
* Debug switches it reads: `persist.camera.capture.*.dump` (beauty, mibokeh, jiigandc, sr, ...), `persist.vendor.camera.forcenoncalib`
  (must stay unset/0), ArcSoft `persist.vendor.camera.arcsoft.*`. Depth/ANC engines: `debug.wa.log.level` (`verbose`), `debug.wa.dump`.
* Models: `/vendor/etc/camera/model/{cap_model,rt_model,ldc_model}` + `dof_l11r_mecp.bin`; HAL copies rt_model to `/data/vendor/camera/model`.

## 6. Vendor tags [Observed]
Generated comparison: [`p2_vendor_tags_generated.md`](p2_vendor_tags_generated.md). The munch HAL defines **729** vendor tags. The app uses
**452** tag names in sections the HAL knows: **189** exist, **263** do not. Missing tags mean the app treats the feature as unsupported, e.g.
`supportedfeatures.{hdrSupported, supportedBokehHdr, bokehDepthBufferSize, portraitStarMode, aiportraitdeblur, MfnrSupernight,
cinematic, insensorzoom, stableDiffusionSR, supportVideoLofic, ...}`, plus groups `xiaomi.beauty` (25), `com.xiaomi.sessionparams` (20),
`xiaomi.ai.asd` (17), `xiaomi.ai.misd` (15), `xiaomi.camera.bokehinfo` (15), `xiaomi.capabilities.videoStabilization` (8), `xiaomi.superResolution` (7).
Most belong to newer phones; for P7 the question per tag is "does the 2021 HAL/firmware have the block at all, or only the tag is missing?".

## 7. Marble (POCO F5) vs Munch (POCO F4) profile [Observed, partial]
Both profiles are fully obfuscated (6.7: `Marble.H1()`…; 5.1: `Munch.OooO00o()`…, and their feature wrappers too), so values cannot be
named in bulk. Known so far: watermark (Munch K40S/F4 → patched Marble POCO F4 5G), bokeh width (Munch_pro 4625 = patched Marble C()),
zoom "capture:0.6:1.0:2.0" and 960 fps slow motion in Munch, filter set (Marble E1 17 → 25), short-video generation (Marble H1 3 → 4).
Other values are traced one by one when a later step needs them.

Values traced and patched in camera builds (all in `tools/re/camera_watermark_patch.sh`, current build v13):

| Marble method | Meaning (where it is used) | Marble (F5) | Patched for F4 | Build | Effect on F4 |
|---|---|---|---|---|---|
| `d()` | watermark device text | XIAOMI / 17 PRO | POCO / F4 5G | v1 | correct watermark |
| `E1()` | filter set | 17 (no Leica looks) | 25 (Leica Vivid etc.) | v3 | Leica filters available |
| `C()` | largest bokeh picture width | 4000 | 4625 (= Munch_pro) | v4 | full-width Portrait output |
| `H1()` | short-video engine generation | 3 | 4 | v5 | Short video can finish/save |
| `C0()` | video bitrate table (`quality:fps[:codec]`) | inherited Common (30 fps only) | own table (`VideoBitrates.java`) | v9 | 4K60 100 Mbit/s etc. |
| `g9()` | front "binning" (process at half picture size, `Wr.K.b`) | true | false | v11 | no 800x600 front processing |
| `K4()` | halve front picture size (`o6.o`) | inherited (type-based) | added, false | v11 | front not halved |
| `m0()` | picture size ratio tolerance (`F1.n3.a`) | 0.005 | 0.006 | v11 | F4 front 5184x3904 (ratio 1.3279) accepted -> 20 MP selfies |
| `u6()` | super resolution for zoom (SR burst at 2x+) | true | false | v13 | zoom photos cropped normally (no SR node on munch → uncropped frame was saved) |
| `z.J0()` + settings checkbox (not Marble) | default of "Ultra-wide distortion correction" | on | off | v12 | ultra-wide photos save (the LDC GPU engine crashed the app) |

Not patched, by decision: `t6()` (auto night in Photo, true on Marble), `l5()` (MediaTek parallel-shot exception, false),
the HFR/60 fps advertising (HAL side, out of scope - native + LMC only). The app also caches computed picture sizes in
`shared_prefs/munch_GLOBAL_llnu_7_camera_cache.xml`; a profile change that affects sizes needs that key removed once.

## 8. Services and SELinux [Observed]
Camera services: `media.camera` (+proxy), `android.frameworks.cameraservice` (HIDL/AIDL bridge), MIUI `camera_covered_service`,
`cameraopt` (CameraOptManager), provider `android.hardware.camera.provider@2.4-service_64`.
Denials seen (enforcing): `hal_camera_default → default_prop` (616: `persist.camera.xiaomi.algoup` / `eebin.write`, unset on stock too → harmless),
`mediaserver/cameraserver → vendor_default_prop`, camera app → `vendor_audio_prop`, `vendor_display_prop`, `vendor_frc_prop`,
`vendor_camera_sensor_prop` (no property set with that label → harmless), `cameraserver → vendor_camera_data_file` (dir search),
`hal_camera_default → vendor_sysfs_kgsl` (GPU frequencies). The app *can* read `vendor_camera_prop`
(e.g. `persist.vendor.camera.mi.module.info.bokeh = s0_OV64B_AAC_64M`, read by libmialgoengine).

## 9. Known problems found at this layer
* Back Portrait: crash while building the `seg/human2` network (details in `MODE_TEST_RESULTS.md`).
* Vendor audio HAL use-after-free on `appname=±pkg` hints (rare, vendor bug).

## 10. Still to do in P2
- [x] Logged mode sweep (§4).
- [x] Vendor tag list (§6).
- [~] Marble vs Munch profile (§7: known values only, rest traced on demand).
- [x] Services and SELinux denials (§8). Resolved in P4: `persist.camera.xiaomi.algoup` / `persist.camera.eebin.write`, unset on stock too → harmless.
