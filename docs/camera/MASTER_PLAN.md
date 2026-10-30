# Camera Master Plan — POCO F4 5G (munch) custom ROM

Status: **APPROVED by the owner 2026-10-28** (see "Owner decisions" below). Written 2026-10-28.

### Owner decisions (2026-10-28)
* **Soft photos (2026-10-28):** owner chose all three paths — (3) LMC as daily photo camera + one tuned xml, (2) time-boxed search for a lighter photo path in the Xiaomi app, (1) **L4 approved**: tune the HAL snapshot noise reduction in the OV64B40 Chromatix file via removable test modules, one change at a time, each change reported.
* **G3 passed (2026-10-28):** improvement order approved (`07_IMPROVEMENT_PLAN.md`); look target "in between" (Xiaomi 17 tone/colour, natural skin, softer than Leica Vibrant); hidden modes allowed one per test build.
* **G2 passed (2026-10-28):** layer maps accepted, open items carried into P7/P8; P7 started. **D2:** test-only CamX logging / 3A-debug overlay (KSU module, removable) allowed.
| Question | Decision |
|---|---|
| Added steps N1–N14 | **Keep all** |
| Priority | **Photo colour and detail → video → selfie → portrait → macro** |
| Third-party apps that matter | **GCam/LMC**, plus every installable **video, social, video-calling and live-streaming app** (test list built in N6 from these categories) |
| Measurement tools (numpy, OpenCV, scikit-image, colour-science, ImageMagick, exiftool, Graphviz) | **Install** |
| Portrait | **Clean result first**: no crash, near-perfect behaviour; if the dual-camera depth bug turns out to be kernel-level, back Portrait is switched to a clean working fallback instead of crashing ("nothing is perfect, near perfect is the target") |
| Q6 own processing stage beside Xiaomi's pipeline | **Yes** (owner, 2026-10-28) |
| Q7 future test photos auto-added to set A with a build tag | **Yes** (owner, 2026-10-28) |
Goal in one line: the best possible photo and video quality (back, ultra-wide, macro, front/selfie, portrait, vlog, video) that this phone's hardware allows, in the native camera,
in GCam, and in third-party apps, with full documentation of every layer so a later kernel/ROM update can reuse the work.

Tags used everywhere: **[Observed]** (seen on the phone/in files) · **[Inferred]** (reasoned, not proven) · **[NEW]** (step added by Claude, not in the owner's list).

---

## 0. Reality check (read before approving the plan)

| Topic | What is true | Consequence |
|---|---|---|
| Sensors | Main OV64B40 64 MP (OIS), UW OV8856 8 MP, macro GC02M1 2 MP (fixed focus), front IMX596 20 MP [Observed] | The optics/sensors set the ceiling. Processing can make photos *cleaner, truer in colour, better exposed*; it cannot turn a small 64 MP sensor into the 1-inch sensor of the Xiaomi 17. "Looks like Xiaomi 17" = colour science + tone + HDR + noise + sharpening, not optics. |
| Megapixels | Native 64 MP (remosaic to 16 MP binned / 64 MP); 108 MP / 200 MP modes cannot exist on this sensor | "More megapixels" is only possible as multi-frame super-resolution (real extra detail, limited) or upscaling (no real detail). Plan treats this as *quality*, not a headline number. |
| Xiaomi 17 algorithms | Most are bound to the SM8850 NPU/ISP (Qualcomm "canoe"): ArcSoft raw/HDR/night, mialgo AINR/JDD/rawhdr etc. [Observed in OS4.0.0.9 odm]. Only LUTs, tuning data, some CPU-only code and config are portable. | Port what is portable (colour LUTs, Leica looks, tuning ideas); **re-implement** the rest with open algorithms (GPU/CPU/Hexagon DSP). |
| Closed layers | CamX/CHI camera HAL, ISP tuning binaries, vendor algorithm libraries, SLPI sensor drivers, modem/DSP firmware are binaries without source | Understanding = reverse engineering (Ghidra/JADX/strings/tracing). Changes are mostly *configuration, tuning data, app/framework code, and our own processing stage*, not new ISP hardware logic. |
| Today's bug | Back Portrait (dual-camera depth) crashes the app; the HAL itself is fine for preview [Observed] | Must be fixed (or cleanly disabled) before "best Portrait" is possible. It is Phase 1 work. |

## 1. Working rules (carried over, non-negotiable)
1. One change per test build; every change has a rollback (module disable / previous APK / previous image).
2. Never write or wipe `persist`, EFS, modem partitions. Ask the owner before any flash or partition write.
3. Repository (public) holds only our own code, patches, configs, docs. **No Xiaomi/Qualcomm binaries, no photos, no logs with identifiers.** Big data lives on the pendrive archive.
4. Findings are tagged [Observed]/[Inferred]; nothing "works" until verified on the phone with the test protocol (section 6).
5. SELinux stays enforcing; any permissive/diagnostic run needs the owner's explicit yes each time.
6. Commit without co-author lines, author rafit612 noreply.

## 2. Phase map (owner's steps 1–15 → phases)

| Phase | Owner step(s) | Goal | Main outputs | Depends on |
|---|---|---|---|---|
| **P0 Lab, baseline & reference library** [NEW] | 17 (new) | Measurable starting point before any change, plus the photo library used for every comparison | Test scenes, scripts, baseline sheet for every camera/mode, **indexed reference library** (own photos, Xiaomi 17 set, POCO F4 sets) + comparison tool | — |
| **P1 Stop the crashes** | 10 (part), 1 | Portrait fixed or cleanly disabled; Night/Short-video/Movie/Panorama verified; log errors triaged | Bug list with root causes, patches as module | P0 |
| **P2 Read the app + OS layer** | 1 | Full map of the camera app (6.7), framework, services, HAL interfaces | `01_APP_OS_LAYER.md` + call/data-flow diagram | P0 |
| **P3 Read the kernel layer** | 2, 14 | Camera/video/ISP/CCI/CSIPHY/ICP/JPEG/Venus/IOMMU/ION kernel drivers and algorithms; store everything for future kernel work | `02_KERNEL_CAMERA_VIDEO.md`, annotated source index, kernel-update notes | P0 |
| **P4 Read firmware + vendor HAL** | 3 | CamX/CHI usecases, node graph, tuning binaries, firmware (ISP/DSP/Venus), algorithm libs | `03_FIRMWARE_HAL.md`, usecase/pipeline diagrams | P2 |
| **P5 Hardware, drivers, sensors, lens** | 4, 5, 6, 16 (new) | Every camera-related hardware block with its driver, algorithm and the exact path to the app; sensor/lens/OIS/AF/flash/laser/EEPROM facts; **audit of image-processing capability the SoC has but Xiaomi did not use** | `04_HARDWARE.md`, `05_DRIVERS.md`, `06_SENSORS_LENS.md`, `06b_UNUSED_CAPABILITY.md` | P3, P4 |
| **P6 Knowledge map** | 7 | One connected graph + md files of all layers (app ↔ framework ↔ HAL ↔ kernel ↔ firmware ↔ hardware) | graphify knowledge graph, diagrams, index | P2–P5 |
| **P7 Improvement design** | 8, 9, 11, 16 | What is better than today: latest algorithms, tuning, security, AI, performance, **unused SoC capability** — ranked by gain/risk/effort; the look target is defined from the reference library | `07_IMPROVEMENT_PLAN.md` | P6 |
| **P8 Implement + tune** | 10, 11, 12, 13, 16, 17 | Native camera fixes, colour tuning, third-party app quality, one GCam xml, Xiaomi 17 portable parts, **own processing stages on unused hardware**; every round compared against the reference library | Modules/patches, tuned profiles, comparison sheets | P7 |
| **P9 Ship + report** | 14, 15 | Baked into the ROM, regression-tested, documented, kernel-ready notes stored | Release candidate, final report | P8 |

P2–P5 are mostly *reading and documenting* and can run in parallel (sub-agents) once P0 is done. P1 can start immediately in parallel because it unblocks testing.

## 3. Detailed steps

### Step 1 (P2) — Camera app and OS layer [owner step 1]
* Read: MiuiCamera 6.7 (Marble device profile, mode modules, filter system, shader effects, Camera2 request builder, vendor tags), `libcamera_algoup_jni`/MIA engine bridge, CameraMind, camera extensions service, deferred-camera service, framework Camera2/Camera service, SELinux contexts and properties used by the camera.
* Method: JADX/smali (installed), Ghidra for the JNI libs, `dumpsys media.camera`, logcat with `walog` debug level, vendor-tag dumps.
* Output: module list (each mode → class → HAL usecase), request/result data flow, list of every vendor tag with meaning, list of every feature flag/profile value (Marble vs official Munch profile).
* Exit criterion: every mode of the app can be traced from button to HAL opmode.

### Step 2 (P3) — Kernel camera and video [owner step 2, 14]
* Source: `rohmanurip/kernel_munch` (4.19.325) + stock 4.19.157 boot images (on pendrive) + Qualcomm techpack camera/video/display.
* Read: CAM-SS (CPAS, ICP/A5, IFE/IPE/BPS, JPEG, LRME, CCI/CSIPHY, sensor/actuator/OIS/flash/EEPROM drivers, request manager, sync, SMMU/IOMMU), Venus video (encoder/decoder), ION/dma-buf heaps, KGSL (GPU compute used by the camera), DSP FastRPC (cDSP/HVX), thermal/DCVS interaction, ISP clocks and bus voting.
* Differences to record: port kernel 4.19.325 vs stock 4.19.157 (open Portrait suspect), config options, patches.
* Output: `02_KERNEL_CAMERA_VIDEO.md`, per-driver notes, annotated source index, **kernel-update notes** (which patches/configs the camera needs, what broke before) → feeds step 14.
* Storage: everything kernel-related goes to the pendrive `kernel_for_future/` + repo notes.

### Step 3 (P4) — Firmware and vendor HAL [owner step 3]
* Read: `camera.qcom.so` (CamX), `com.qti.chi.override.so` (CHI), node libraries (`com.xiaomi.node.*`, mialgo, ArcSoft, Almalence), usecase XML/`.bin`, sensor module + tuning binaries (`com.qti.sensormodule.*`, `com.qti.tuned.*`), SNPE/HTA models, ISP firmware, DSP/aDSP/cDSP/SLPI images.
* Compare: HyperOS 1.0.9 vs 1.0.12 vs MIUI 13/14 firmware (already on the pendrive: 16 of 22 firmware images identical between 1.0.9 and 1.0.12).
* Output: pipeline diagrams per usecase (photo, night, portrait, HDR, video, slow-motion), tuning-parameter dictionary, algorithm list with inputs/outputs.

### Step 4–6 (P5) — Hardware, drivers, sensors, lens [owner steps 4, 5, 6]
* Hardware (4): Spectra 480 ISP, Hexagon 698 (HVX), Adreno 650 compute, Venus, memory/bandwidth, thermal — what each can do for imaging, with real limits. Source: live phone + datasheets + kernel docs (already collected in `hardware_docs/`).
* Drivers (5): for every block: driver source file, bound device, which HAL/algorithm talks to it, which app feature depends on it. Built on `hardware_inventory.md` (1152 devices already mapped).
* Sensors and lens (6): OV64B40 / OV8856 / GC02M1 / IMX596 modes, binning/remosaic, HDR/DOL support, PDAF/AF, OIS, lens shading, distortion, focal lengths/aperture, flash, laser AF (absent), light/colour sensors (TCS3701, BU27030) for AWB/flicker; sensor register/mode tables from the kernel and tuning files.
* Output: per-camera "datasheet-style" page: what the hardware offers vs what the software currently uses (the gap list = opportunities).

### Step 7 (P6) — Knowledge storage and mapping [owner step 7]
* Every finding goes to a `.md` file (one file per layer, one index) — **one structure, not many scattered files**.
* Graphical mapping: knowledge graph with the installed `graphify` skill (input: all md + code indexes), architecture diagrams with `drawio-skill` / `artifact-diagramming`, optional Graphviz/Mermaid (install needed). Layers map: Application → Framework → Camera service → HAL/CHI → Kernel drivers → Firmware → Hardware, with arrows for data and control and a list of algorithms per node.
* Output: interactive graph (HTML), PNG/SVG diagrams, index with links; kept in repo (`docs/camera/`) and pendrive.

### Step 8 (P7) — Latest algorithms, performance, tuning, security [owner step 8]
For each pipeline stage (see `07_IMPROVEMENT_PLAN.md`): current method → best available method → portable? → gain → risk → effort.
Stages: AWB/AE/AF, tone mapping, HDR/multi-frame, denoise (per ISO), sharpening, demosaic/remosaic, lens shading/distortion, super-resolution, night, portrait segmentation/depth, skin/beauty, video stabilisation, video encode, audio.
Security items: camera/microphone indicators intact, no spoofing hooks, no unauthorised access paths, permissions of the camera app, no debug properties left on, no identifiers in logs/photos (EXIF location off by default), SELinux domains for any new component.

### Step 9 (P7) — AI image/video processing [owner step 9]
* Inventory what runs today (mialgo/arcsoft/SNPE/HTA models) and where (CPU/GPU/DSP).
* Candidates that fit SD870 (GPU/Hexagon, not a modern NPU): semantic segmentation for portrait/sky, AI denoise (light models), AI scene detection, super-resolution for zoom, face/skin enhancement, video denoise. Open-source models (TFLite/NNAPI/GPU) vs ported Xiaomi models — decide per feature by quality, latency and heat.
* Honest rule: only ship what is measurably better in the test protocol and does not break shutter lag/thermals.

### Step 10 (P8) — Fix native camera and make third-party apps benefit [owner step 10]
* Native: Portrait, Night, Leica looks, correct Munch profile values, watermark (done), mode stability.
* OS level for other apps (WhatsApp, Instagram, Telegram, Snapchat, Meet/Zoom, Open Camera, Blackmagic/FiLMiC…): Camera2/CameraX capability levels, logical multi-camera exposure (main+UW), physical camera ids, RAW/DNG, 4K/60, HDR video, **Camera Extensions (OEM) for HDR/Night/Bokeh** so third-party apps can use the vendor algorithms, correct sensor/lens metadata, FOV/zoom ratios, flicker/anti-banding, front camera mirroring.
* Output: capability matrix before/after, compatibility test list, patches (property/config/HAL-feature level; no app-specific hacks).

### Step 11 (P8) — Tuning, enhancement, performance, full hardware use [owner step 11]
Layered approach (least risky first): **L1** app profile/flags → **L2** Camera2 request parameters and vendor tags → **L3** app/GL processing (LUT, tone curve, sharpening) → **L4** HAL tuning binaries (only with per-change approval).
Per camera (main, UW, macro, front) × per mode (photo, night, portrait, HDR, pro, video 4K30/60, 1080p60, slow-mo): AWB (mixed LED/CFL/tube light, 50 Hz), skin tones (South Asian), per-ISO noise vs detail, local tone mapping, AF speed/OIS, shutter lag, night capture time, video stabilisation and encode quality, thermal at 10-minute 4K, battery.
Reference material: Xiaomi 17 / 17T Pro sample photos (124, on the pendrive) as colour targets — used for look matching, never as a claim of optical equivalence.

### Step 12 (P8) — One GCam xml [owner step 12]
* Today: 13 near-identical XML configs (~173 KB each) in `LMC8.4`.
* Plan: diff all 13, extract the real differences (a handful of parameters), build **one final config** based on the measured results of steps 11/13 (+ optional "profile" switches inside it), validate on all lenses, ship one file. Needs a short discussion with the owner first (which looks to keep).

### Step 13 (P8) — Xiaomi 17 / latest algorithms and features [owner step 13]
* Source of truth: `stock_rom_global17` (OS4.0.0.9) + kernel branch `popsicle-w-oss` (on pendrive).
* Classify every algorithm/feature: **portable now** (LUTs, 69 video-filter LUTs incl. 11 Leica, tuning JSONs, watermark/Leica assets, CPU-only libs) · **portable with work** · **needs SM8850 NPU/ISP** (re-implement with open algorithms or drop).
* Implement in priority order by visible gain.

### Step 14 (P3/P9) — Keep everything kernel-related [owner step 14]
Pendrive `kernel_for_future/`: kernel sources (port + stock + Xiaomi 17), configs, diffs, camera driver notes, findings on 4.19.325 vs 4.19.157, build recipe, toolchain version, test results of every kernel experiment. Goal: a future kernel update can start from these notes instead of rediscovering them.

### Step 15 (P9) — New features, quality, megapixel, image/video processing, audio [owner step 15]
Candidates (each only if proven better): multi-frame SR for 2× zoom, 64 MP mode quality fixes, improved night, better video stabilisation, HDR video, LOG/Pro video, stereo/wind-reduced audio for video (audio HAL mixer paths, mic tuning, camcorder source), front camera quality, vlog mode polish. Final report with before/after sheets.

### Step 16 (P5 audit → P7 design → P8 build) — Use SoC image-processing capability that Xiaomi did not use [owner request 2026-10-28]
Idea: Xiaomi ships a fixed set of algorithms and sensor/ISP modes for this phone; the Snapdragon 870 and the OV64B40/OV8856/IMX596 sensors can do more. Where they can and Xiaomi did not, we use it.
1. **Capability audit (P5):** for each block write "what the silicon/sensor can do" vs "what the shipped software enables" → a gap list (`06b_UNUSED_CAPABILITY.md`).
   * **Spectra 480 ISP** [Known, to verify on the phone]: number of IFE/IPE/BPS instances, simultaneous streams, max pixel rate (4K60 ×2 / high-fps modes), 10-bit pipelines, staggered/multi-exposure HDR inputs, hardware MFNR/multi-frame blocks, LTM/ASF/ANR blocks and which tuning headers expose them (`com.qti.tuned.*`).
   * **Sensors** (kernel sensor tables + module bins): modes present in the sensor driver but not used by the app/HAL (full-res 64 MP remosaic quality, binned modes, high-fps modes, DOL/QCFA HDR variants, PDAF modes), OIS range and how Xiaomi limits it, UW sensor autofocus.
   * **Hexagon 698 DSP** (HVX vector unit, HTA tensor block — [Inferred] no newer HTP; verify with the SNPE/HTA runtimes on the phone) — what the shipped `.dlc` models run on, and how much DSP time is free during capture.
   * **Adreno 650 GPU compute** (OpenCL/Vulkan compute): big free capacity during capture/preview — candidate for own multi-frame align/merge, denoise, tone mapping, sharpening.
   * **CPU** (Kryo 585: NEON + dot-product; no SVE): candidate for lightweight classic algorithms.
   * **Video**: Venus encoder profiles the SoC supports but the camera does not offer (e.g. 10-bit HEVC/HLG, higher bit-rates, extra frame rates/resolutions), EIS+OIS combination, concurrent camera streams.
   * **Memory/bandwidth/thermal**: how much headroom exists before throttling (feeds the budget in N3).
2. **Design (P7):** for every gap rate: visible gain · risk (stability/thermal/battery) · effort · "needs HAL binary change?" · "can ship as app/GL/own-service layer?".
3. **Build (P8), safest first:** (a) enable existing but hidden modes/profiles by config/vendor tag; (b) own post-processing stage on GPU/DSP/CPU in our layer (post-capture "Pro" processing, GCam-style merge, AI denoise/SR) rather than patching closed ISP firmware; (c) only then HAL tuning changes, one at a time with approval.
4. **Rule:** a capability is kept only if the comparison against the reference library and the test protocol shows a measurable gain without extra crashes, lag or heat.

**Owner-approved candidates from the P5 audit (2026-10-28, `06b_UNUSED_CAPABILITY.md`)** — each goes through P7 rating and the N13 gate:
* **C1 Sensor RAW HDR** — OV64B40 sensor file has 3-exposure / zig-zag HDR; HAL `enableRawHDR=0`. Test module: enable, check pipeline + quality.
* **C2 DSP stage of Xiaomi HDR** — `miai_hdr_config.yaml` `hdsr: enabled: false`, `libMIAIHDR_skel.so` installed. Find what `hdsr` does, A/B test.
* **C3 60 fps and ISO above 877 for other apps** — HAL AE fps ranges stop at 30, main ISO capped at 877; check if the HAL can offer more.
* **C4 Own AI stage on NNAPI / DSP / GPU** — NNAPI 1.3 with Adreno/HVX/HTA, SNPE, OpenCL → AI denoise / sharpening / segmentation in our layer.
* **C5 Hidden camera modes** — 13 modes with `support()=false` (Night video, Supermoon, Fastshot, Director mode, …); check which work on SD870.

### Step 17 (P0 build → used in P7/P8) — Reference photo library and image comparison [owner request 2026-10-28]
**Where it belongs: P0**, because every later phase needs it (P7 defines the target look from it; P8 compares each build against it; gates G1–G5 show the sheets).
Three photo sets already on the pendrive (`poco_f4_munch_archive`):
| Set | What it is | Role |
|---|---|---|
| **A. Own phone photos** (`phone_photos_*`, 110 camera files + GCam folder, and every future test shot) | What *our* ROM produces today | "Before" evidence, failure cases (e.g. colour cast, softness), progress history over time |
| **B. Xiaomi 17 / 17T Pro** (`xiaomi17_reference_photos`, 124: dpreview originals, Drive folder, review-site photos) | Target look (colour, tone, contrast, sharpness, HDR rendering) | The "what good looks like" reference |
| **C. POCO F4 photos by others** (`other_people_pocof4_sample_photos`, 103 Commons CC BY-SA + 109 review-site) | What the phone produces with official/stock software | Baseline of the stock POCO F4 look: tells us whether our ROM is below, equal to or above stock, and how far stock is from set B |

Method (all scripted, results as tables + contact sheets):
1. **Index**: one CSV for all sets (source, licence, camera model, EXIF ISO/exposure/focal length, scene tag, resolution). Scene tagging by simple rules + manual check.
2. **Unpaired comparison** (photos of different scenes): compare *distributions* per scene class — Lab colour histograms and gamut, saturation and contrast curves, tone curve/mid-grey, highlight/shadow roll-off, white-balance bias, skin-tone hue cluster, noise vs ISO, sharpness/edge profile, dynamic range use.
3. **Paired comparison** (same scene shot by us): our camera vs GCam vs reference render, ΔE maps, side-by-side + difference sheets; stored per build.
4. **Look learning**: build 3D LUT / tone-curve candidates from statistics (histogram/optimal-transport matching of set A → set B per scene class), then judge visually and by metrics — copy the *look*, not the optics.
5. **Quality rules**: web-resized or re-encoded photos (review sites, Flickr) are used for tone/colour tendencies only, never for detail/noise measurements; only originals (dpreview, Drive, Commons) are used for detail and noise.
6. **Output**: `docs/camera/REFERENCE_LIBRARY.md` (method + results), scripts in `tools/camera_lab/`, large data on the pendrive `camera_project/`.
Licence note: sets B and C (review sites) are copyrighted — personal offline reference only, never published in the repo.

## 4. Steps added by Claude [NEW] — please accept or reject each

| # | Added step | Why |
|---|---|---|
| N1 | **P0 test lab and baseline** (fixed scenes, colour chart, scripts, scoring: noise/sharpness/ΔE/skin hue/clipping, video checks) | Without a baseline "better" cannot be proven; all later work is judged against it |
| N2 | **Unit calibration audit**: EEPROM/OTP data of this exact phone (AF, OIS, dual-camera calibration, lens shading), replaced parts (panel/power key were replaced — confirm camera modules are original) | Portrait/UW/AF quality depend on per-unit calibration; wrong data = permanent softness |
| N3 | **Thermal/power/performance budget** (4K60 sustained, 64 MP burst, night) with measured limits | Prevents tuning that looks good for 10 s then throttles |
| N4 | **Video pipeline deep-dive**: EIS+OIS, rolling shutter, HEVC/10-bit, bitrate, HDR video, frame-rate/flicker (50 Hz mains), audio-video sync | Video is half of the goal and has its own algorithms |
| N5 | **Anti-banding/flicker and local lighting** profile (50 Hz, LED/CFL/tube), South-Asian skin-tone targets | Real-world quality in your country; Xiaomi's defaults are global |
| N6 | **Third-party compatibility matrix** (named list of apps, Camera2 level checks, pass/fail table) | Step 10 needs an objective definition of "other apps get the best output" |
| N7 | **Licensing/IP check**: Leica/Xiaomi assets stay local; the public repo ships only our patch scripts and configs; reference photos stay on the pendrive | Repo rule + legal safety |
| N8 | **Release engineering**: how each improvement ships (KSU module while testing → baked into `payload_tele` → image build checks → installer), A/B regression run before every release, rollback plan | Today the camera lives in a test module; it must become part of the ROM safely |
| N9 | **Stability monitoring**: crash/ANR/tombstone collection routine (logs already collected for 27–28 Oct) and a "no new crash" gate | Quality gate for every build |
| N10 | **Front camera and selfie** as its own track (IMX596, beauty/skin, wide-selfie, portrait single-camera path which already works) | Owner asked for selfie quality explicitly |
| N11 | **Macro/UW policy**: GC02M1 is 2 MP fixed focus — decide whether macro should use the UW sensor's autofocus crop instead (UW OV8856 AF?) | Probably a bigger real-world gain than tuning the 2 MP sensor |
| N12 | **Audio track** in its own step (video audio, mic selection, zoom-follow audio) | Owner listed audio drivers in step 15 |
| N13 | **Dynamic quality gate on unused-capability work** (Step 16): every extra stage must beat the reference/test results and not raise crashes, lag or temperature | Prevents "more processing" that makes photos worse or the phone hot |
| N14 | **Photo-library hygiene**: keep own photos separate from downloaded ones, record licences, never mix copyrighted sets into the repo, keep EXIF/location of own photos out of any shared output | Privacy and legal safety for Step 17 |

## 5. Tools and skills

| Need | Have | To install / use |
|---|---|---|
| Java/Android reverse engineering | JADX (library + headless jar), dexlib2 smali/baksmali wrappers, Ghidra 12.1.4 headless, `llvm-objdump` (NDK), `dtc`, erofsfuse, Android SDK tools | — |
| Native tracing/profiling | NDK `simpleperf`, adb/logcat/`dumpsys`, tombstones | Perfetto (optional), Snapdragon Profiler not available (NDA) |
| Image/video measurement and comparison | Python3 + PIL, `ffmpeg/ffprobe` | numpy, OpenCV, scikit-image, colour-science, ImageMagick, exiftool (install for P0 / Step 17 scripts) |
| Mapping/graphs | Claude skills `graphify` (knowledge graph), `drawio-skill`, `artifact-diagramming`, `dataviz` | Graphviz `dot` / Mermaid CLI (optional) |
| Process help | Claude skills such as `debugger`, `performance-profiler`, `android-profiler`, `systematic-debugging`, `performing-firmware-extraction-with-binwalk`, `writing-plans`, `verification-before-completion`, `dispatching-parallel-agents` | used per step |
| Data stores | Pendrive archive (ROMs, firmware, kernels, photos, logs, docs) | — |

Parallel work: P2–P5 reading tasks are independent — one sub-agent per layer, each writing its own md file; results merged in P6.

## 6. Test and measurement protocol (P0)
* Scenes: daylight outdoor (colour chart + grey card), mixed indoor LED/CFL, low light (3 lux / 20 lux), backlit portrait, skin tones, text/resolution chart, moving subject, macro, UW edges, night skyline; video: walking, panning, low light, 4K60 10-minute thermal run, audio clap/voice/wind.
* Each scene captured on: native camera, GCam (LMC), and (for comparison) the Xiaomi 17 reference look.
* Metrics: SNR per ISO, sharpness (Laplacian/MTF50 from chart), clipped highlights %, ΔE on colour patches, skin-hue offset, white-balance error, shutter lag, night capture time, frame drops, temperature, battery %/10 min.
* One comparison sheet + recommendation per round; every build/profile is a git-tracked named profile.

## 7. Storage layout
* Repo (`docs/camera/`): `MASTER_PLAN.md` (this), `CAMERA_PROJECT.md` (running log), `01…07_*.md` layer documents, diagrams, tuning profiles, scripts. One index `docs/camera/INDEX.md`.
* Pendrive (`poco_f4_munch_archive/`): `camera_project/` (large data: traces, dumps, decompiled outputs, graph exports, test captures), `kernel_for_future/`, existing ROM/firmware/photo/log archives.

## 8. Risks and decision gates
| Risk | Mitigation |
|---|---|
| Closed binaries limit what can be changed | Prefer config/tuning/app/GL layers first; HAL binary patches only with per-change approval |
| Portrait root cause may be kernel-level | RAM-only stock-kernel test (`fastboot boot`, nothing written) before any kernel work |
| Xiaomi 17 algorithms need hardware we do not have | Classification step; re-implement with open algorithms or drop |
| Tuning that looks good in one scene hurts others | Fixed multi-scene protocol, regression sheet before keeping any change |
| Thermal/battery regressions | Step N3 budget, 10-minute runs |
| Public repo leak (IMEI incident found 2026-10-27) | Pre-commit scan, deny rules in `.gitignore`, owner decision on history clean-up |
**Gates (owner review points):** G1 after P0+P1 (baseline + stable camera) · G2 after P6 (maps complete) · G3 after P7 (improvement list ranked) · G4 before each flash/release · G5 final report.

## 9. Proposed order
1. **Now:** owner reviews this plan (accept/reject N1–N12, reorder).
2. **P0 + P1 in parallel:** baseline lab; Portrait diagnosis (needs the owner's "yes" for one more permissive run) and mode checks.
3. **P2–P5 in parallel** (documentation of layers).
4. **P6** graph + index → **G2**.
5. **P7** ranked improvement list → **G3**.
6. **P8** implementation rounds (colour/tuning first, then AI, then Xiaomi 17 portable parts, then GCam single xml).
7. **P9** release candidate, report.

## 10. Questions for the owner — all answered 2026-10-28 (see "Owner decisions" at the top)
1. Accept N1–N12? Which to drop?
2. Is the main goal ranking correct: photo colour/detail > video > selfie > portrait > macro? (affects order of P8 rounds)
3. Which third-party apps matter most (top 5)?
4. OK to install the measurement tools (numpy, OpenCV, scikit-image, ImageMagick, exiftool, Graphviz) on the laptop? (disk is almost full — needs space first)
5. Portrait: should I continue with the permissive diagnostic, or accept "Portrait disabled cleanly" if the root cause turns out to be in the kernel?
6. Step 16 (unused SoC capability): is it OK to build our own post-processing stage (GPU/DSP/CPU) *beside* Xiaomi's pipeline, instead of only tuning inside it? That is the realistic way to use capability Xiaomi left unused.
7. Step 17: should every future test photo you take be added automatically to the reference library (set A) with a build tag, so before/after history is kept?
