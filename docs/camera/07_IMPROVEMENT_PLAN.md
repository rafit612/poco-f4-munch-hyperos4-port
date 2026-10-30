# 07 — Improvement plan, ranked (MASTER_PLAN P7 → gate G3)

Prepared 2026-10-28 from `01`–`06b`, `MODE_TEST_RESULTS.md` and the reference library. Scores: **Gain** = visible quality / features for
the owner; **Risk** = chance of crashes, lag, heat or a broken build; **Effort** = work until a tested module exists.
Layers (safest first): **L1** app profile/flags · **L2** request params / vendor tags / config overlays · **L3** own processing stage
(LUT, tone, sharpen, AI) · **L4** HAL tuning binaries (per-change approval). Every item passes the N13 gate: measurably better against the
reference library and test protocol, no new crashes, lag or heat.

## 1. Ranked list
| Rank | Item | Layer | Gain | Risk | Effort | Depends on | First step |
|---|---|---|---|---|---|---|---|
| 1 | **Colour / tone / sharpness look** of the main camera (photo) matched to the reference library (Xiaomi 17 look, natural South-Asian skin) | L3 (own LUT + tone curve + sharpening on the saved JPEG/HEIC), later L4 | high | low | medium | **daylight test shots (P0)**, measurement scripts | baseline sheet, then LUT/curve candidates |
| 2 | **Photo analysis with 3A debug data** (AE/AWB/AF decisions per photo) | L2 test overlay (D2 approved) | enabler | low | low | — | re-enable `enable3ADebugData`/`enableTuningMetadata` only during test-shot sessions |
| 3 | **OIS verification** (handheld video, long exposure, OIS on/off) | test | proof | none | low | — | 2 short handheld clips + Pro-mode 1/4 s shots |
| 4 | **C5 hidden modes** — start with Night video (214), Supermoon (188, Almalence configs present), Fastshot (225) | L1 (`support()` patch, one mode per build) | medium | medium (mode may crash or lack HAL support) | low per mode | — | enable Night video in a test build, mode sweep |
| 5 | **U15 higher video bitrate** (Venus allows 160 Mbit/s; 4K60 today = 50 Mbit/s HEVC) | L1/L2 (camera app bitrate table / media profiles) | medium (video detail) | low | low-medium | — | read the app's bitrate per resolution |
| 6 | **C2 DSP stage of Xiaomi HDR** (`hdsr`) | L2 (`miai_hdr_config.yaml` overlay) | unknown → medium | low-medium | low | find what `hdsr` does | A/B HDR scenes with `hdsr: enabled: true` |
| 7 | **Video stabilisation / EIS margins + 50 Hz flicker** (N4/N5) | L2 (`eisoverridesettings.txt`, anti-banding) | medium | low | low-medium | video baseline | measure crop vs shake at 20 % / lower margins |
| 8 | **One GCam/LMC xml** (13 → 1) built from measured results | app config | medium | low | low-medium | items 1, 3 | diff the 13 files |
| 9 | **C4 own AI stage** on NNAPI (GPU / HVX / HTA / **NPU — unused by the camera**): AI denoise, sharpening, sky/skin segmentation | L3 (own service/app step) | high | low for the system (runs after capture) | high | items 1, 2; NNAPI device list on Android 17 | list NNAPI devices; prototype denoise on saved photos |
| 10 | **Back Portrait in the native camera** | native (vendor engine contract) | high | medium | high / unknown | decompiling the graph loader (may be blocked) | keep LMC as workaround |
| 11 | **C1 sensor RAW HDR** (`enableRawHDR`, sensor 3-exposure modes) | L2 → HAL | medium-high | high (pipeline may not exist for munch) | medium | item 2 | test overlay `enableRawHDR=1`, check preview/capture |
| 12 | **C3 60 fps and ISO > 877 for third-party apps** | HAL static metadata | medium (other apps) | high | high | third-party matrix (N6) | confirm HAL can stream 60 fps in a plain Camera2 session |
| 13 | **U1 HDR10 video** | vendor path + app flag | medium | high | high | Main10 runtime check | read encoder profiles; look for the app's HDR10 switch |
| 14 | Front camera / selfie track (N10) | L3 + profile | medium | low | medium | item 1 | selfie baseline (front works today) |
| 15 | Security checklist (indicators, permissions, no debug props left, EXIF location off) | config | trust | none | low | — | run the checklist on the current build |

Not worth doing (settled): macro via ultra-wide AF (UW is fixed focus); 8K recording (SD870 encoder max 4096 wide); reviving the Short-video
MiLive 183 entry (never listed).

## 2. Recommended order
1. **Now (no owner action needed):** item 3 OIS check, item 15 security checklist, item 5 bitrate reading, item 4 Night video test build.
2. **After the owner's daylight test shots:** items 2 + 1 (baseline, then colour/tone/sharpness rounds), then 8 (one GCam xml).
3. **Then:** item 7 video, item 6 DSP HDR, item 9 AI stage prototype.
4. **Research track in the background:** items 10, 11, 12, 13 — each only continues if its first step shows it is possible.

## 3. Gate G3 — owner decisions
* Approve the ranking / order above (or move items).
* Confirm the look target for item 1: Xiaomi 17 / Leica look vs natural POCO F4 stock look vs in between.
* Approve test builds for hidden modes (one mode per build, removed if it crashes).

## 4. Owner answers (G3, 2026-10-28)
* Order: **approved as recommended** (step 1 now; colour work after the daylight test shots).
* Look target: **in between** — Xiaomi 17 tone and colour, natural skin, less heavy contrast than Leica Vibrant.
* Hidden modes: **yes, one mode per test build**, switched off again if it crashes.

## 5. Feasibility notes (2026-10-30, desk work + read-only phone checks)
**C4 own AI stage / own processing stage on GPU, DSP, NPU (items 1 and 9)**
* Hardware access is there without root [Observed]: NNAPI on Android 17 lists `qti-dsp`, `qti-hta`, `qti-gpu` (NNAPI 1.3) to an ordinary
  process (`06b` U7); OpenCL (`libOpenCL.so`) is used by the vendor depth engine; the firmware for cDSP/NPU is the newest munch release
  (`03_FIRMWARE_HAL.md` §8), so there is nothing to upgrade first.
* Where it can hook in [Inferred]: the Xiaomi MIA graph and LMC's processing are closed binaries → an own step cannot be inserted *inside*
  them. The realistic design is a **post-capture step**: a small system app that sees each new photo of the native camera / LMC
  (MediaStore observer on `DCIM/Camera`), runs the stage (LUT + tone curve + sharpening first, later an NNAPI denoise/segmentation model) and
  writes the result back, keeping the original until the owner chooses. It works for both cameras in scope and touches neither app.
* Limits: works on the 8-bit JPEG/HEIC after Xiaomi's own processing (cannot undo over-smoothing, only shape colour/tone/sharpness);
  adds ~0.3–1 s per photo in the background (budget not measured yet — the load measurement was stopped, see `MODE_TEST_RESULTS.md`
  2026-10-30); NNAPI is deprecated in new Android releases → use LiteRT/TFLite with the NNAPI delegate and a CPU/GPU fallback.
* Verdict: **feasible, medium-high effort**; start with the non-AI part (item 1 LUT/tone/sharpen) once the owner's daylight set exists —
  it needs no model and gives most of the "Xiaomi 17 tone, natural skin" target.

**Xiaomi 17 portable parts**
* The Xiaomi 17 base (`stock_rom_global17`) keeps its camera HAL in `odm`: `camx.provider-impl.so` / `camx.device-impl.so` (AIDL provider),
  the CHI "feature2" set (`com.qti.feature2.{hdr,rawhdr,raw2yuvhdr,enhancedhdr,anchorsync}`), and feature-compatibility tables for
  **sm7750 / sm8750 / sm8850** only [Observed]. The munch HAL is HIDL `camera.provider@2.4` (device@3.5) on kona.
* → HAL, CHI features, tuning and DSP skels are **not portable** (different HAL interface, SoC tables, newer Hexagon generation [Inferred]).
* Portable = what runs in the app: the camera app itself (already done: MiuiCamera 6.7 on the Marble profile), its looks/filters (Leica set
  enabled, v3), and the **tone/colour target** as data (reference photos → our own LUT in item 1). That is the remaining Xiaomi 17 part.
* Verdict: **closed as "only the look is portable"**; no binary porting from the Xiaomi 17.
