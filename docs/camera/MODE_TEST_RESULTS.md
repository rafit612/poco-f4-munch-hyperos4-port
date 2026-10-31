# Camera mode test results (P1) — baseline build v3, 2026-10-28

Automated: open mode → take one shot → read crash/error logs. [Observed]

| Mode | Crash | File saved | Verdict |
|---|---|---|---|
| Photo, Pro, Video, Documents, ID photo, Time-lapse, Slow motion, Dual video, Ultra HD, Long exposure | no | yes | **work** |
| Night | no | yes (2 files) | **works**, but very noisy log (see below) |
| Movie | no | yes | **works** |
| Panorama | no | 0 by the test | opens, needs a manual sweep to save — recheck by hand |
| Xiaomi Short Video (MiLive) | no (v5+) | yes (v5+) | **fixed in v5, renamed in v6 — see below** |
| Short video (classic, 1080p) | no | yes | **works** |
| Portrait (back) | app crashes (depth engine) | no | **broken — separate investigation** |

## Short video — root cause and fix [Observed]
* Recording itself always worked: every segment is a valid H.264 720×1280 + AAC file in the app's MiLive workspace.
* The real bug: after pausing, the bottom bar had only the shutter. The **delete-segment** and **finish (✓)** buttons were missing, so a clip could never be finished and saved.
* Cause: the app runs the forced Marble (POCO F5) device profile. `Marble.H1()` = short-video engine generation = **3**. The paused-state buttons (`record_reverse_layout`, `work_space_layout` in the bottom bar fragment) are only added when it is **4**, and with 3 the app also picks the old controller although it runs the new `MiLiveMasterModule`.
* Fix (camera build **v5**): `Marble.H1()` 3 → 4 in `tools/re/camera_watermark_patch.sh`. Generations 3 and 4 load the same native libraries (`miffmpeg` + `MiShortVideoSDK`), so nothing missing gets loaded.
* Verified on the phone: pause shows ⌫ and ✓, ✓ opens the Share/Save page, Save writes `DCIM/Camera/VID_*.mp4` (H.264 720×1280, AAC). Photo and normal Video still save; 0 crashes.
* Audio HAL: the vendor `audio.primary.kona.so` has a use-after-free on the `appname=±<package>` hint (sent by audio policy on every playback start/stop, not only by Short video). GWP-ASan caught it once; 0 crashes in 7 later Short-video runs. It's a rare vendor bug, not what broke Short video. Watch it and don't patch the HAL.
* The two "Short video" entries are **two different modes with the same name**, both working: the 1st is MiLiveMaster (mode 190, 720p, segments, music, effects); the 2nd is the classic MIUI short video (`FunModule`, mode 161, one take, **1080p** H.264 + AAC). Not a bug. Camera build **v6** labels the first one with the app's existing string "Xiaomi Short Video" (string/gvp); the classic one keeps "Short video". Verified in the mode panel; the renamed entry opens MiLiveMasterModule.
* Tried and dropped: switching off the old MiLive entry (mode 183) — it was never in the list, so it changed nothing.

## VLOG — crash and fix [Observed]
* Opening VLOG (mode 209, FunModule) crashed the app: `IllegalArgumentException: Illegal config item: 172` from the top-bar factory
  `aa.j5.E()` (TopConfigItemUtil). VLOG asks for top-bar item 172, which this build does not define. Release builds throw; debug builds
  only log the warning and return a placeholder item.
* Fix (camera build **v7**): take the debug path in `aa.j5.E()` (`tools/re/camera_watermark_patch.sh`). Verified: full mode sweep on v7,
  VLOG opens, 0 camera crashes in 19 modes (`p2_mode_sweep_generated.md`).

## Night — log noise (not a crash) [Observed]
787 of ~944 error lines are one repeated line: `camxchinodewrapper.cpp ExecuteProcessRequest() Node::RealTimeFeatureSuperNightPreviewRaw_…`.
The rest are the known port issues (forced sensor mode, OIS type mismatch, AEC zone not found, offline feature wait, snapshot-stream negotiation, tintless/debug-data hints). Night still produces photos; these are quality/tuning items for later phases, not crashes.

## Still to do by hand
* Panorama: do a real sweep and confirm a file saves.
* Portrait: clean fix (own investigation, owner wants a crash-free result).
  - 2026-10-28 stock-kernel A/B (owner approved): `fastboot boot` of stock HyperOS 1.0.9 kernel 4.19.157 + the port ramdisk
    (port header/patch level kept; nothing flashed). Android started, then init rebooted with `reboot,bpfloader-failed`: Android 17's
    bpfloader needs kernel BPF/tracing features the 2022 kernel lacks. The phone returned to the port kernel by itself.
    So the kernel cannot be A/B-tested on Android 17; the kernel stays a suspect, not proven.
  - 2026-10-28 how stock did it: back Portrait = vendor `libmialgoengine.so` node `MiaNodeJiiGANCapBokeh` (camera_mode 0x301) →
    `libwa_depth.so` (depth 2.5.3 / refocus 2.6.4) → `libanc_dc_base.so` network. All three are byte-identical to stock HyperOS 1.0.9,
    so the engine is the same one MIUI 13/14/HyperOS 1 used; what changed is the caller (camera 6.7 + Marble profile, Android 17).
  - Leftover found and fixed: `persist.vendor.camera.forcenoncalib` was still 1 from the 27 Oct test (stock does not set it) → set to 0.
    With real calibration (419-byte caldata from /persist) the crash is unchanged.
  - Not the cause: 0-byte `/data/vendor/camera/mibokeh.bin` (HAL cache, not re-created), OpenCL loading in the app (works),
    main-camera + single-bokeh routing (v7exp/v8exp: the app still starts the stereo engine).
  - Session sizes: main 4624x3472, sub (ultra-wide) 3264x2448, depth 4624x3472; live preview depth reports
    `rtdof_rectify Jacobian ransac1 < 9` (too few matching points between main and ultra-wide).
  - Sizes compared with camera 5.1 (Munch): same rule (`bokehVendorID` 3 → depth = main size), and the HAL calibration was made at
    main 4624x3472 + sub 3264x2448 (`xiaomi.dualcal.streamsize`) = what 6.7 configures. Sizes are NOT the difference.
  - Crash timing: on Portrait open, before any shot. The depth node (`MiaNodeJiiGANCapBokeh`) is created with the session, its worker
    builds the network on OpenCL and aborts ~1 s later. 5.1 only feeds the engine on a capture with valid main+sub images.
  - Remaining difference is inside the native engine's input contract (what the 6.7 session/graph gives the 2022 node at start),
    or Android 17 / port kernel behaviour under OpenCL. Needs native-level tracing of the vendor engine.
  - Native trace (2026-10-28, engine verbose log `debug.wa.log.level=verbose`, reset afterwards): the capture engine reads the real
    calibration (419 B, board type 1), loads `/vendor/etc/camera/model/cap_model/capture_model` (59 MB, md5 OK, 3 networks, input 1024x768),
    inits OpenCL with `capture_cache`/`capture_policy`, then aborts while building the graph. Frames: `Segment LoadModel` → `seg/human2`
    (human segmentation net) → `relayout_format` (`HW44_DOT`) → layout with a zero dimension.
  - The preview network (HAL, 480x480, `/data/vendor/camera/model/rt_model`, also factory cache) loads fine. Ruled out: board/chip props
    (kona/munch/SM8250 = stock), stale writable cache (preview cache is the factory one too), CPU features (`asimddp` reported).
  - Open: why `seg/human2` gets a zero-size layout in the app process; next would be decompiling the graph loader around those frames.
  - 2026-10-29 re-check (camera v9): same abort, `DNNError: assertion layout.shape[i] && layout.stride[i] >= 0`, thread `ParallelDataZip`
    in the app process, 18 frames in `libanc_dc_base.so` called from a `libwa_depth.so` worker, about 0.6 s after `MiaNodeJiiGANCapBokeh`
    init (`dof_l11r_mecp.bin`, depth 2.5.3 / refocus 2.6.4). Ruled out this time:
    - camera 5.1 as a comparison: it does not start on Android 17 at all ("supported picture size list from hal is null"), so no A/B possible.
    - `ro.hardware.chipname` (empty, read denied): the library only compares it with `hi3751` (a HiSilicon TV chip).
    - other props it reads (`ro.board.platform` kona, `ro.product.board` munch): same as stock.
    - `capture_cache` / `capture_policy` / `capture_model` copies in the app's files dir: byte-identical to `/vendor/etc/camera/model/cap_model`.
    - CPU cache sizes: missing in sysfs (only `level`/`type`), so the engine's cpuinfo cache is mostly "unknown" — but stock is the same:
      neither stock 4.19.157 nor port 4.19.325 probes CCSIDR for cacheinfo, and neither vendor_boot device tree has `cache-size`.
  - Left: native reverse engineering of `libanc_dc_base.so` (30 MB, stripped) to find which tensor gets the zero dimension. Large job.
  - **Root-cause lead (2026-10-29): the port ships a different Adreno GPU driver.** The depth engine libraries
    (`libanc_dc_base`, `libwa_depth`, `libmialgoengine`) and model files are byte-identical to stock OS1.0.12, but the GPU stack is not:
    `libOpenCL.so`, `libCB.so`, `libllvm-qcom.so`, `libgsl.so`, `libadreno_utils.so` all differ, and the port adds `libOpenCL_adreno.so`
    (stock has none). The port driver reports "OpenCL 3.0 QUALCOMM build 0805.0" and `CL_DEVICE_MAX_CLOCK_FREQUENCY = 1`
    (`camera_builds/re_portrait/clquery`). The engine's `capture_policy` / `capture_cache` were tuned for the stock driver.
  - Verbose engine log: the segmentation net (1024x768, md5 OK) loads, `Initplatform run_mode=1` with the vendor cache + policy,
    `Init opencl ... clLen(85564)` (= policy size), then the abort as soon as OpenCL deploy starts.
  - Tests with a removable module `cam_cl_test` (bind mounts, one change each, now disabled):
    | Test | Result |
    |---|---|
    | empty `capture_cache` + empty `capture_policy` | **no crash**; Portrait opens and shoots, but "read algo_policy failed → Init platform failed → nn model not init → depth failed": the photo saves **without blur** |
    | empty `capture_cache` only | different abort: `assertion 'fp'` (the engine profiles and wants to write a new cache to the read-only vendor path) |
    | writable empty cache (app-owned file bound over the vendor path) | engine writes a 1 KB cache header, then the original `layout.shape` abort |
  - So the trigger is the stock **policy** (or graph setup) on the new driver, not the cache. Options: (a) Portrait without the
    NN depth (no crash, no blur — not useful), (b) find the engine's policy-free / tuning path (needs RE of `libanc_dc_base.so`
    around `Initplatform`), (c) use the stock GPU driver stack (system-wide change, affects games/UI; would need its own test).
  - Model-header tests (2026-10-29, Ghidra light analysis of `libanc_dc_base.so`; header layout from its ModelParse code):
    `runtime` (u16 at 0x2E) is Initplatform's run_mode (1 = OpenCL + cache + policy, 0/3 = no OpenCL setup), `nhwcd4` is the byte at 0x39;
    the md5 at offset 4 covers bytes 40..end (tool: `camera_builds/re_portrait/scripts/model_patch.py`). Patched models mounted at runtime:
    | Model | Result |
    |---|---|
    | A: runtime=0 | CPU path: abort "Only naive and opencl handle support Image2DPack4TensorFormat" |
    | B: runtime=0, nhwcd4=0 | same abort - the GPU image format is stored in the graph itself |
    | C: runtime=1, nhwcd4=0 | original `layout.shape` abort |
  - So header flags cannot fix it. The policy is a hash table keyed by a device id; without an exact match the engine uses a
    "nearest" entry (FUN_00752bec). Next layer: how that key is derived from the GPU, and which entry the new driver lands on.
  - Policy key (2026-10-29): GPU type from `CL_DEVICE_VENDOR` "QUALCOMM" -> parse `CL_DEVICE_VERSION` "OpenCL 2.0 Adreno(TM) 650"
    -> key (6, 50, family 4). Both drivers report the same string, so the key and policy match are the same. **Ruled out.**
  - OpenCL call trace inside the camera (own shim `camera_builds/re_portrait/clshim`, runtime bind mount over
    `/vendor/lib64/libOpenCL.so`, real loader parked over an unused automotive HAL library, both unmounted after each run):
    the engine only queries device info and creates small buffers before the abort - no image, program or kernel.
    The crash is inside the **model loader** (graph deserialiser frames, "Load model"), not in a driver call.
  - The 9 extensions the engine checks are identical on both drivers. Overriding answers one at a time:
    | Override | Result |
    |---|---|
    | IMAGE_PITCH_ALIGNMENT 16/32/64/128 (8-byte) | same `layout.shape` abort |
    | IMAGE2D_MAX_WIDTH 32768 | "bad input shape for polyadic operator: {2}, {4}" |
    | IMAGE2D_MAX_WIDTH 4096/8192/65536, MAX_HEIGHT, WORK_GROUP, LOCAL_MEM | same `layout.shape` abort |
    | MAX_MEM_ALLOC 256/512 MB | "{2}, {4}" error; 2 GB: warp-perspective shape assertion; 1.5/4 GB: `layout.shape` |
    These limits only move where a bad shape surfaces; the cause is upstream (shape data computed/read wrongly at load).

## Video bitrate (camera v9, 2026-10-29) [Observed]
* Code: HEVC bitrate = profile table `C0()` key `quality:fps:5:`, H.264 key `quality:fps::`, else vendor
  `media_profiles_vendor.xml` (30 fps entries only: 720p 14, 1080p 20, 4K 50 Mbit/s H.264). Marble inherited Common's table
  (30 fps HEVC only: 720p 10.8, 1080p 15.4, 4K 38.5 Mbit/s) → 60 fps used the 30 fps vendor value (4K60 = 50 Mbit/s).
  Log/true-colour paths have their own tables (4K60 log 150 Mbit/s).
* v9: `Marble.C0()` → `tools/re/VideoBitrates.java`: HEVC 720p 12/18, 1080p 25/40, 4K 60/100; H.264 720p 16/24, 1080p 32/50,
  4K 80/120 Mbit/s (30/60 fps). Venus limit 160 Mbit/s.
* Test (owner's default = 4K60 HEVC): log `setupRecorder: H265 bitrate = 100000000`, file 100 Mbit/s. 10 s right after reboot: 11
  frame gaps (Google apps ANR during boot load); 10 s settled: 60.0 fps, 0 gaps; 60 s: 60.0 fps, 0 gaps, battery 36.7 → 37.0 °C,
  747 MB/min (was ~375).

## Video: anti-banding and stabilisation (2026-10-29) [Observed]
* 4K60 video request (`cmd media.camera watch`): `aeAntibandingMode = 50HZ`, exposure 10 ms (flicker-safe on 50 Hz mains),
  fps range [60 60], `lens.opticalStabilizationMode = ON`, `control.videoStabilizationMode = OFF`.
* HAL static EIS capability (`camera.qcom.so`, original vendor): `xiaomi.capabilities.videoStabilization.quality = [5 30 6 30]`
  → EIS only for 720p30 and 1080p30; `60fpsSupported = 0`, `60fpsDynamicSupported = 0`, no 4K entry. `previewSupported = 1`.
* `eisoverridesettings.txt`: EIS margin 20 % (w/h), Super EIS 35 % × 51 % (UW 35.5 % × 51.7 %), LDC grid on, frame delay 30.
* Result: 4K30/4K60 = OIS only (same as stock vendor); 1080p30/720p30 = OIS + EIS; Super EIS (steady mode) uses the large crop.
  Enabling EIS at 4K would need a HAL binary change (not done).

## C2: DSP stage of Xiaomi HDR (`hdsr`) (2026-10-29) [Observed]
* `/vendor/etc/camera/miai_hdr_config.yaml` (`mobile_model: L11R` = munch/K40S) is read by `libxmi_high_dynamic_range_cdsp.so`
  (and `libxmi_hdr_checker.so`). `algo_params_dsp.hdsr.enabled: false`; the library's matching code is `AlgoDeghostSRProcessCdsp`
  → [Inferred] a deghost super-resolution step of the HDR merge, run on the CDSP. Only active when HDR triggers (backlit scenes).
* Wide-camera merge settings worth noting for night/highlights: `highlight_suppress.suppress_ratio 0.5, tone_node 200`,
  `dark_area_boost 0.6`; post-processing denoise and sharpen off. `hdrd_ui9_params.config`: HDR lux window 250–300, EV −12/+6.
* Test module `cam_hdr_test` (bind-mount copy with `hdsr.enabled: true`) prepared in `~/camera_builds/c2/`, not installed yet.
  Test plan: backlit scene (window), ≥ 2 shots per variant alternating, log `xmi_high_dynamic_range` to confirm HDR ran.

### C2 follow-up: what `hdsr` is (2026-10-30, static, no root) [Observed]
* **hdsr = HDR + super-resolution** on the cDSP. The HDR checker config `/vendor/etc/camera/hdrcheckerparamsettings.yml` (`product_name: L11R`,
  2022-03-24) has a rear `hdsr:` block: `zoom_min 1.0`, `zoom_max 20.0`, `sr_ev0_num 8`, `ev_short -9`, `face_restriction 0` → a burst of
  8 normal frames + 1 short frame, merged with deghost + SR (`AlgoDeghostSRProcessCdsp`); the DSP library `libMIAIHDR_skel.so` holds the
  HVX kernels (flow align, denoise residuals, dark mask, downscale).
* It is switched off in **three** places, not one: `miai_hdr_config.yaml` `algo_params_dsp.hdsr.enabled: false`, and in the checker for every
  region (cn / global / india) `hdsr.enable: 0` and `options.support_hdsr: 0`. The first kit (c2a) flipped only the first → it would most
  likely have changed nothing.
* New kit **c2b** (`~/camera_builds/c2b/mod_cam_hdr_test`, copy on the pendrive `camera_project/laptop_archive_2026-10-29/c2/c2b/`):
  bind-mounts both files with all three switches on. Files keep label `vendor_configs_file` (chcon the module copies before the first boot).
  Needs adb root to install (currently lost, see below).
* Expected effect [Inferred]: only HDR-triggered back shots (backlit / high-DRC scenes), likely most useful at 2x zoom and above; the burst gets
  longer (9 frames instead of the normal HDR set) → check shot-to-shot time and heat. Risk: the app may not request the longer burst
  (HDR checker decides the EV list) → then logs show `hdsr` off and the test is closed as "not usable on this port".
* Test plan (unchanged scene, owner "window" item): phone on the stand facing a window, 1x and 2x, ≥ 2 shots per variant alternating
  c2b on / off, log `xmi_high_dynamic_range` + `HDR_Checker` lines to confirm the hdsr path ran, compare detail in the window frame and noise
  in the dark wall.

## Walking test, owner (2026-10-29 11:25–11:27, camera v9 vs LMC 8.4, one clip each, kept local) [Observed]
Jitter = RMS of the camera path minus its 0.5 s moving average (phase correlation on 480-px frames), in % of frame width.
| Clip | Codec, bitrate | Stabilisation | Jitter x / y |
|---|---|---|---|
| Xiaomi 4K60 | HEVC 99.9 Mbit/s | OIS | 0.92 / 0.39 % |
| Xiaomi 4K30 | HEVC 60.1 Mbit/s | OIS | 1.28 / 1.17 % |
| **Xiaomi 1080p30** | HEVC 25.1 Mbit/s | **OIS + EIS** | **0.44 / 0.13 %** |
| LMC 4K30 | H.264 33.4 Mbit/s | OIS (+ LMC) | 1.00 / 0.46 % |
| LMC 4K60 | H.264 50.3 Mbit/s | OIS (+ LMC) | 1.00 / 0.62 % |
| LMC 1080p60 | H.264 20.1 Mbit/s | OIS (+ LMC) | 2.03 / 1.43 % |
* Xiaomi 1080p30 with EIS is 2–3× (x) and 3–9× (y) steadier than any 4K clip; LMC is not steadier than the Xiaomi camera at 4K.
  All v9 bitrates confirmed in real use; 4K60 0 dropped frames. One walk per clip → indicative, not a lab result.

## Security checklist (P7, 2026-10-29, camera v9)

| Check | Result |
|---|---|
| SELinux | Enforcing |
| Build | `user`, `release-keys`, `ro.debuggable=0`, `ro.secure=1`, `ro.adb.secure=1` |
| CamX logging (`camxoverridesettings.txt`) | all log masks 0, txt/ascii logging off, 3A debug data and tuning metadata off, core dumps off |
| Camera dump props | `persist.camera.capture.*.dump`, `persist.vendor.camera.*.dump*` all 0; no camera debug props left from tests |
| Camera modules | `munch_cam_watermark` only bind-mounts the APK (root:root 644, `system_file`); `cam_l4_test` disabled |
| Privacy indicator | MIUI privacy dot controller active, no `device_config` override |
| Camera app permissions | Camera, mic, location granted; phone state denied |
| Location in photos | **on** in the Xiaomi camera (`pref_camera_recordlocation_key`) and LMC; 15 of 17 owner photos from 2026-10-28 carry GPS. Owner's choice; such photos stay local only |
| Repo screenshots | 7 JPEGs, no EXIF at all |
| Repo identifiers | **real IMEIs, serial, cpuid and psno/sno in `audit/agents/annibale/scratch/audio/port_all.txt` (a getprop dump), public since commit 94a468c.** History rewritten with git-filter-repo and force-pushed 2026-10-29 (main da9b7e3, branch 12c72d9; release tag unchanged). Old commits 85c0514 / 2b4c1af stay reachable by ID until GitHub Support purges them |
| Re-check 2026-10-30 03:20 (v11, after the night/soft/C2 tests) | Enforcing; `user`/`release-keys`, `ro.debuggable=0`; camera dump props all 0; modules: `munch_cam_watermark` on, `cam_cl_test` + `cam_l4_test` disabled; only mount = the camera APK; no app update left installed (codePath `/product/priv-app`), APK sha c8eb90f4; Portrait debug tools (`lldb-server`, `clquery`) removed from `/data/local/tmp` |
| Network listeners (observation, outside camera scope) | `netmgrd` (Qualcomm vendor) and Google Play services listen on many TCP ports on all interfaces (0.0.0.0 / ::). Not from our tools; to compare with stock HyperOS before deciding anything |
  - Debugger (2026-10-29, NDK lldb-server attached as root on the phone's loopback only, adb-forwarded): catches the
    abort in `ParallelDataZip`. Frame #4 (`+0x1c31c08`) is a re-throw from a `catch(...)` block in frame #5
    (`+0x1a47c88`), so the original throw site is already unwound at abort time. Software and hardware breakpoints on
    the throw helpers, the assertion site (`+0x659c80`) and even the model-load function (`+0x5122b0`) were resolved but
    never hit; breakpoints do not reach the engine's worker thread in this attach mode. Next: fix that (attach after the
    worker thread exists, or catch the throw with a different method) before reading the bad layout.
  - Debugger results (2026-10-29): breakpoints work when set without auto-continue commands. Original throw stack
    (30 frames, all `libanc_dc_base`): layout check `+0x659c0c` (Image2DPack4 format: "invalid row pitch", align) <-
    `+0x759d64` <- operator creation <- **static shape inference** (`static_infer_value`, "infer desc for var") <- graph
    loader <- Load model <- SetModelPath. At the failing check the tensor layout is **ndim 5, shape (1, 0, 1, 0, 4)**,
    strides (0, 0, 0, 4, 1): a 4-channel image-packed tensor with height 0 and width 0.
  - The error is **not deterministic**: an unmodified run also produced "bad input shape for polyadic operator: {2}, {4}".
    So the earlier "override changed the error" results were run-to-run variation, not an effect of the override.
  - Forcing every OpenCL read/write/map to be blocking and finishing the queue after kernels/unmaps (shim -DFORCE_SYNC;
    the engine requests 8 non-blocking maps) does not help: same crash. Async transfers are ruled out.
  - Current reading: shape values computed during static inference are garbage/zero, varying per run - points to
    uninitialised input (a parameter the caller does not set in this app/OS combination) rather than a driver answer.
  - Failing operator identified (stack strings at the failing check): **`relayout_format[2530]`**, the format
    conversion MegEngine's OpenCL optimiser inserts to put a tensor into the GPU image layout. Its input is the empty
    (1, 0, 1, 0, 4) tensor. Neighbouring errors seen in other runs come from the same sub-graph (a WarpPerspective
    shape check, "polyadic {2},{4}"), so an upstream shape/size value is garbage at load time. Class names are not
    available (RTTI stripped) and the model file is encrypted (no operator names). Tools: `camera_builds/re_portrait/
    scripts/lldb_capture.sh` (one capture per run, posts a dashboard job) and `stack_strings.py` (`stackstr`, `stackobjs`).
  - More tests (2026-10-29):
    | Test | Result |
    |---|---|
    | model header multi_thread=0 (single-threaded engine), 2 runs | still crashes ("polyadic {2},{4}") - threading ruled out |
    | MegEngine internal log via debugger callback | only 3 lines (stock kernel cache read, 324 tags); no policy/GPU/algo warnings |
    | camera HAL process | loads the same `libanc_dc_base.so` (with `libwa_rtdof.so`) and its preview depth net works on the new driver |
    | zero-initialised heap in the app (shim calls mallopt(M_BIONIC_ZERO_INIT,1) before model load) | still crashes (WarpPerspective shape assertion) - uninitialised heap ruled out |
  - All three error variants (empty 0x0 image, "{2},{4}", WarpPerspective ndim check) are about tensor *dimensions* in the
    same warp sub-graph after the GPU image-format conversion: some tensors end up with the wrong number of dimensions.
    That points at the load-time graph optimisation (which tensors get converted to the 5-D GPU image layout), whose
    result varies between runs on the new driver. A stock-driver run is now the cleanest way to confirm the driver link.
  - **Stock GPU driver test (2026-10-29): not possible on the port.** KernelSU module `cam_gpu_stock` bind-mounted the
    28 stock OS1.0.12 Adreno user-space files (lib64 + lib: EGL/GLES/q3dtools/vulkan, libgsl, libCB, libllvm-glnext/-qcom,
    libadreno_utils/_app_profiles, libOpenCL; all their dependencies exist on the port). Boot never completed:
    SurfaceFlinger aborted and the camera provider segfaulted (the 2021 driver does not work with Android 17 / the port
    kernel). Module disabled over adb, rebooted (back in 20 s, port driver active), module deleted. So the GPU driver
    cannot be swapped system-wide; any fix has to work with the port's driver (build 0805).
  - Graph-guided check (2026-10-29, graphify flagged "Camera SELinux denials" and "Munch profile in camera 5.1" as
    unconnected): kernel audit log during one Portrait open = 47 denials, **none from the depth engine thread** and none on
    GPU/CPU sysfs; the camera app is only denied display/audio/frc/sensor properties (known, harmless, see 01_APP_OS_LAYER §8);
    the GPU clock denial is ThermalCollector (system_app). So SELinux denials are unrelated to the back Portrait crash.
    The Marble vs Munch profile differences known so far (watermark, bokeh width 4625 already patched, zoom, 960 fps,
    filters) cannot explain it either: the depth engine loads its network from vendor files + camera id 0x301 at node Init,
    before any app-supplied image size exists. Both topics are linked to the Back Portrait investigation as "ruled out".

## C3: 60 fps and ISO above 877 for third-party apps (2026-10-29) [Observed]
* Tool: own Camera2 probe app `camera_builds/c3probe` (plain Camera2 session, one YUV stream, TEMPLATE_RECORD; logs the
  advertised ranges, delivered frames over 5 s, result metadata and mean frame brightness). Installed with root `pm install`
  (MIUI blocks adb USB installs).
* Advertised to apps (main id 0 and logical id 4): AE fps ranges [14-15, 15, 24, 25, 14-30, 30], ISO 50-877, YUV 1080p min
  frame duration 33.3 ms -> apps only offer 30 fps.
* **The HAL already streams 60 fps to a plain Camera2 app when asked:** 1080p [60,60] = 60.03 fps, 4K [60,60] = 60.03 fps,
  result range [60,60], frame duration 16.67 ms. The Qualcomm vendor key `org.quic.camera.manualExposure.disableFPSLimits`
  is not needed. LMC's earlier 4K60/1080p60 clips are true 60.0 fps (499 frames / 8.31 s, 665 / 11.08 s).
  -> C3 60 fps only needs the *advertised* capabilities extended (fps range [60,60]/[30,60] + 60 fps min frame durations).
* `camxoverridesettings.txt` `AvailableTargetFpsRanges=12:24` (commented "bokeh fps range") does not feed the advertised
  list: set to 60:60 at runtime + provider/cameraserver restart = list unchanged. Reverted.
* **ISO above 877 is not really applied:** manual ISO 1600/3200/6400 is accepted and echoed in the result, but at a fixed
  1/2000 s exposure the frame brightness goes 5.5 / 10.1 / 18.0 (ISO 200/400/800, doubling as expected) then 13.8 / 8.4 /
  8.4 for 1600/3200/6400 - darker, not brighter. The sensor's gain limit (max analog ~796) is enforced below the HAL;
  raising it would mean changing the sensor module -> not pursued (risk), C3 ISO part closed as "not feasible safely".
* Where the advertised list comes from (camera.qcom.so has symbol names; Ghidra): `InitializeStaticMetadataPool` copies
  `android.control.aeAvailableTargetFpsRanges` (tag 0x10014) from the static-caps struct (pairs, count at +0x100). The list
  is computed, not a constant table (the int32 sequence 14,15,15,15,24,24,25,25,14,30,30,30 does not exist in the binary).
  `HwEnvironment::InitializeHwEnvironmentStaticCaps` treats sensor modes with 31-119 fps as high-speed modes and builds
  separate 60 fps (0x3c) entries for them; the normal AE range list stops at 30. Next: find the exact place the AE list is
  filled (sensor static capability / extended caps) and decide between a CamX patch and leaving C3 at "apps can request 60".
* CamX verbose init log (runtime override of the log masks, reverted; provider + cameraserver restarted):
  main sensor OV64B40 modes - res 0/1/2 up to 30 fps (min 14.29), **res 3 = 60 fps** (also 120.07), res 4 = 120, res 5 = 240.
  `InitializeScalerStaticCaps` computes `supportedFPS` per output size from the *normal* modes only (e.g. 4624x3472 -> 30,
  4624x2080 -> 25/30) -> min frame durations 33.3 ms -> apps see max 30. `Titan17xContext::GetStaticCaps` logs
  "HFR Preview FPS 60": the 60 fps mode is classed as an HFR mode, so it is left out of the normal fps list, yet a normal
  session requesting [60,60] gets it (probe: 60.03 fps at 1080p and 4K).
* Options to advertise 60 fps: (a) change the sensor mode table so mode 3 also counts as a normal mode (sensor driver
  data, test as removable bind-mount module; risk: CamX may choose mode 3 for other sessions and change Xiaomi camera
  behaviour), (b) a CamX patch in `InitializeScalerStaticCaps` / the AE list, (c) leave the HAL alone: apps that let the
  user request 60 fps (LMC/GCam, Open Camera manual fps, FreeDcam) already get real 60 fps.
* **C3 closed (owner decision 2026-10-29): option C.** Scope is the native camera and LMC only; third-party apps are out
  of scope. No HAL change. The ISO part is not feasible anyway. Probe app uninstalled; tools kept in `camera_builds/c3probe`.

## Native front camera: 1600x1200 selfies with wrong colours -> fixed in camera v11 (2026-10-29) [Observed]
* Symptom (owner photo `IMG_20261029_201752.jpg` + reproduced in room light): every native front photo 1600x1200, 0.4 MB;
  in low light the saved image had swapped red/blue (U/V) colours. Front pipeline ran at 800x600 (MIA skin beautifier,
  GPU flip on 800x600 YUV). HAL offers front YUV/JPEG up to 2592x1952 (binned) and 5184x3904 (full, mode 36865).
* Cause (Marble = POCO F5 profile rules applied to the F4's IMX596): the picture-size picker (`F1.n3.a`) only accepts
  sizes with |ratio - 4:3| < `Marble.m0()` = 0.005. The F4 front 4:3 sizes 5184x3904 and 2592x1952 have ratio 1.3279
  (0.0055 off), so it fell back to the first exact 4:3 size, 1600x1200; then front "binning" (`Marble.g9()` = true via
  `Wr.K.b`) halved the processing size to 800x600. The result is also cached in the app's shared_prefs
  (`munch_GLOBAL_llnu_7_camera_cache.xml`, key `PictureSizeForMode_163_true_1_1_...`), so a new build alone did not change it.
* Fix (camera v11, sha c8eb90f4, `tools/re/camera_watermark_patch.sh`): Marble.g9() true -> false, Marble.K4() added -> false,
  Marble.m0() 0.005 -> 0.006; plus the stale cache entry removed once on the phone (backup in
  `camera_builds/prefs_backup_2026-10-29/camera_cache_before_front_fix.xml`).
* Result: front photo 5184x3904 (20 MP), 3.8 MB, correct colours, fully processed; back camera unchanged (4624x3472).
  v10 (g9/K4 only) did not change the size (m0 + cache were the real limits); v10 deleted, v9 kept as rollback.
* Still to check with the owner: real selfies in low light (noise, skin, beauty), front Portrait/video in the native app.

## C5 hidden modes (2026-10-29) [in progress]
* The 13 hidden modes have `ModuleEntry.support()` hard-coded to `const/4 v0, 0x0` (no feature check). Tool:
  `tools/re/hidden_modes_test.sh <in.apk> <out.apk> <entry...>` flips chosen entries to true on top of a build.
* First test build `MiuiCamera_v11exp_hidden.apk` (sha e58292c1) = v11 + Night video (214, SuperNightVideoModule),
  Supermoon (188, SuperMoonModule), Fastshot (225, StreetModule). Test plan: mode appears, opens without crash
  (logcat crash buffer), takes a photo/clip, then roll back to v11 unless a mode is worth keeping.
* Results (2026-10-29 23:25-23:35, v11exp_hidden installed via the module, then rolled back to v11):
  | Mode | Appears | Opens | Result | Verdict |
  |---|---|---|---|---|
  | Fastshot (225, StreetModule) | yes (More panel) | **no**: opens camera id -1 (no camera mapped for this mode), app closes to the launcher | - | not usable without mapping work |
  | Supermoon (188, SuperMoonModule) | yes | yes, main camera, opmode 36866 (0x9002), no crash | saves a 3472x4624 photo; zoom 5x-60x is plain digital crop of the main sensor; MIA graph is the normal HDR/SkinBeautifier/AIIE, no moon algorithm | works but low value (soft digital zoom); not kept, can be added on request |
  | Night video (214, SuperNightVideoModule) | **no tile, no switch** in Night or Video | - | no entry point in the UI even with support() true | not reachable |
* Side note: Video mode shows an "aperture adjustment" panel (Marble/F5 feature; the F4 has a fixed aperture) - check what it
  does (simulated bokeh?) in a later pass.
* Second test build (v11 + the other 10 entries on, 23:35-23:45, rolled back to v11):
  | Mode | Appears | Result | Verdict |
  |---|---|---|---|
  | AI Capture Assist (168, AiModule) | yes | main camera, opmode 0x9005 like Photo, saves a normal photo; the assist part turns preview frames into small JPEGs for a helper service that does not exist on this ROM ("onPreviewPixelsRead: no found handler") | = Photo mode; not kept |
  | Live cinematography (231, MasterLiveModule) | yes | crashes at once (NullPointerException in the app) | not usable |
  | AI Watermark, Long exposure v2, Director mode, Equip street, Instant photo, Friend, Underwater photo/video | **no** (need more than support() to show a tile) | - | not reachable |
* **C5 conclusion:** of the 13 hidden modes none adds real value on the F4 (Supermoon = digital zoom only; AI Capture Assist
  = Photo; the rest crash, have no camera or no UI entry). Closed; camera stays v11. Tool kept: `tools/re/hidden_modes_test.sh`.

## P0 video heat baseline: 10 min native recording per mode (2026-10-29, camera v11, phone charging, indoors) [Observed]
Tool: `camera_builds/tmp/thermal_test.sh` / `thermal_series.sh` (temps every 30 s via root, start/stop confirmed in the
camera log, waits for the file to finalise, reads duration/size from MediaStore, deletes the test clip).

| Mode (bitrate) | Battery start → 10 min | Board start → 10 min | CPU peak | Charge on charger | File |
|---|---|---|---|---|---|
| 1080p30 (25 Mbit/s HEVC) | 37.2 → 37.0 °C (flat) | 42.6 → 41.2 °C | 71 °C | 100 % | 10:25, 1.98 GB |
| 1080p60 (40 Mbit/s) | 35.5 → 36.5 °C (+1.0) | 39.8 → 41.0 °C (+1.2) | 72 °C | stable | (file lost - see below) |
| 4K30 (60 Mbit/s) | 35.1 → 37.0 °C (+1.9) | 37.9 → 41.7 °C (+3.8) | 70 °C | 100 % | 10:23, 4.70 GB |
| 4K60 (100 Mbit/s HEVC) | 33.8 → 38.9 °C (+5.1, still rising) | 37.5 → 45.6 °C (+8.1) | 81 °C | 100 → 97 % | ~13 min, 10.2 GB |

* 4K60 is the only mode that heats the phone clearly and drains it even on the charger; no thermal throttling or
  frame-rate drop appeared within 10 minutes, but the trend is still rising -> long 4K60 takes need a check (20-30 min) later.
  4K30 and below are thermally comfortable.
* Test-method lessons: Xiaomi dims the screen during long recordings, so the first stop tap only wakes it (retap needed);
  force-stopping the camera before the file finalises leaves a `.pending-*` file (all such test leftovers deleted).
* Dropped-frame counts were not measured for these 10-min files (too big to pull); the earlier 60 s v9 4K60 test had 0 drops.

## Native video Bokeh ("aperture" button in Video mode, 2026-10-29) [Observed, effect not judged yet]
* The Video-mode button "Open aperture adjustment panel" opens a **Bokeh** slider (Marble feature; the F4 has a fixed
  aperture). Moving the slider sets `applyVideoBokehBackLevel` (0-46 seen); the recorder switches to **720p30** while it is
  on. A 6.7 s test clip recorded fine (200 frames, 30 fps), 0 crashes - unlike back Portrait photos, live video bokeh uses
  the HAL preview depth path, which works on the port.
* No visible blur on a flat scene without a person (expected: it separates a person from the background). Owner test
  with a person in frame needed. The small button left of the slider toggles off (-1) / last level; turned back off,
  Video mode is 1080p60 again.

## C1 sensor RAW HDR (2026-10-30) [Observed] - closed
* Runtime override `enableRawHDR=1` (camxoverridesettings bind mount + provider/cameraserver restart, reverted after):
  HAL starts fine, 0 crashes, but the app does not request RAW HDR on this profile (`CaptureModule:
  isMultipleRawHdrSupported: hdrType = -1`, `shouldEnableMfHdrQuickShot: no supportMfHdrQuickShot`). The test photo
  differed only by auto-exposure settling after the restart (brighter, slightly more clipping), not by more dynamic range.
* Both sensors report in-sensor HDR (IHDR) in CamX, but using it needs app-side support (hdrType) plus a HAL usecase that
  feeds it - deep work with uncertain gain for photos (Xiaomi's multi-frame HDR node already runs on every photo).
  Closed as not worth it now.

## P5 GPU/CPU load budget during camera use (2026-10-30 02:35) — aborted, no data [Observed]
* Method (no root): `/sys/class/kgsl/kgsl-3d0/gpubusy` (busy/total counters, readable by adb shell) + `/proc/stat` every 1 s through idle,
  Photo preview, one Photo shot, 20 s 1080p60 recording; script `~/camera_builds/tmp/load_budget.sh`.
* Aborted: another session was testing a different app on the phone, so the camera did not stay in front and three shutter taps landed in
  that app (no data entered, only a tab switch). No camera files were created or deleted. Both `ab_shot.py` and the script now refuse to tap
  unless the camera is in focus. To repeat when the phone is free.
* Side result: `mode_sweep.open_camera()` sends BACK keys when the camera is not in front — fine for camera pop-ups, but only safe when
  nobody else is using the phone.

### Repeat run (2026-10-30 02:55, phone free, camera in focus checked before every tap) [Observed]
Per-phase means (1 s samples; GPU = kgsl `gpubusy` busy/total, CPU = all 8 cores from `/proc/stat`). The "idle" phase also contains
the camera launch (CPU peak 80 %). The run's own photo and clip were deleted afterwards.

| Phase | GPU busy mean / max | CPU mean / max |
|---|---|---|
| Photo preview | 3.3 / 3.6 % | 28 / 31 % |
| Photo shot (MFNR + MIA graph) | 3.5 / 11.5 % | 37 / 54 % |
| Video preview (1080p60) | 4.3 / 9.9 % | 42 / 56 % |
| Video recording 1080p60 | 3.6 / 10.3 % | 45 / 50 % |

* **The Adreno 650 is almost unused by the camera** (≤ 12 % even during a shot) → a GPU stage (LUT, tone, sharpening, OpenCL/NNAPI-GPU
  model) has a large budget; the CPU is about half loaded during video, so heavy CPU work should wait until after the shot.
* cDSP/HTA load is not readable without vendor tools; their budget stays open (only matters for a DSP model).

### C2 functional check of kit c2b (2026-10-30 02:57-02:59, root, runtime bind-mount + HAL restart, reverted) [Observed]
* The HDR checker runs in the camera HAL and logs its state per preview frame: stock `sr:[0, enable:0, zmin:1.0, zmax:20 …]`;
  with c2b `sr:[0, enable:1, zmin:1.0, zmax:20.0, face:0, overexp:0.01, ev0:8, ev-:-9]` → **the switches are read and take effect.**
* Photo still works, no crash. The scene (dark room, bright monitors) gave `detect 0` on all 127 checked frames → HDR did not trigger,
  so the hdsr merge could not run. **Quality A/B needs a scene where HDR triggers** (backlit window in daylight) = owner "window" item.
* Install method for that test: push both files to `/data/adb/modules/cam_cl_test/c2b/`, `chcon vendor_configs_file`,
  `nsenter -t 1 -m -- mount --bind` over `/vendor/etc/camera/{miai_hdr_config.yaml,hdrcheckerparamsettings.yml}`, restart provider +
  cameraserver; revert = `umount -l` + restart (done, stock values verified).

### C2 closed (2026-10-30 09:30, stand with window light, kit c2b alternating off/on/off/on, reverted) [Observed]
* With c2b the HAL checker shows `sr:[0, enable:1 …]`, without it `sr:[0, enable:0 …]`; HDR itself did not trigger (`detect 0`, app
  `applyHDR:false`, `hdrEnabled = false`) because the window is only a strip at the frame edge.
* Decisive line from the app: `VTNF: xiaomi.hdr.sr.enabled, Could not find tag` (also `xiaomi.hdr.raw.enabled`). The app requests HDR-SR
  through vendor tag `xiaomi.hdr.sr.enabled`, which the munch HAL does not define; the first field of the checker's `sr:[…]` (the
  request) therefore stays 0 whatever the config says.
* **Result: hdsr cannot be requested by camera 6.7 on this HAL → C2 closed as "not usable on this port"** (would need a new HAL vendor
  tag = HAL change). Kit c2b stays on the pendrive for reference; nothing installed. A window/backlit test is still useful for the
  normal HDR look (highlights), but it is no longer a C2 test.


## Ultra-wide photos never saved — found and fixed in camera v12 (2026-10-30 09:35-09:46) [Observed]
* Baseline sheet on the stand: the 0.6x (ultra-wide, camera id 2) photo stayed a **16,777,216-byte preview placeholder** (1080x1440, no
  EXIF); repeated twice. Log: capture runs (algoType 8 → 3-frame burst), MIA graph HDR → JIIGAN LDC → AIIE, then the app process dies:
  `SIGSEGV … ParallelDataZip`, backtrace `MiaNodeJiiganLdc::doProcessImage` → `JiiganCaptureLDC::process` → `libwa_widelens_undistort`
  → **`libanc_dc_base`** (the same MegEngine/OpenCL engine that crashes back Portrait on this port's GPU driver).
* The setting **"Ultra-wide distortion correction"** (`pref_camera_ultra_wide_ldc_key`, default on) selects that capture LDC path.
  With it off: 3/3 ultra-wide shots save at 2448x3264 with EXIF, no crash, image looks normal (lines reasonably straight).
* **Camera v12** (`tools/re/camera_watermark_patch.sh` block 5, sha aca37fb5): default of that setting = off (`z.J0()` and the settings
  checkbox); users can still switch it on. Tested with clean prefs: ultra-wide 2448x3264 and Photo 4624x3472 saved, no crash.
* Installed on the owner's phone: v12 runs now as an app update; the `munch_cam_watermark` module holds v12 for the next boot
  (package cache cleared); ROM payload = v12. Rollback = v11 (pendrive / `~/camera_builds`).

## Night mode output has a purple cast — open bug (2026-10-30) [Observed]
* Native **Night mode** (NightModule, opmode 0x800a), camera v11/v12, phone on the stand:
  | Shot | Light | Exposure | Mean RGB | Look |
  |---|---|---|---|---|
  | 03:13 | dark room | 0.3 s ISO 877 | 70 / 45 / 84 | scene visible, everything under a magenta haze |
  | 09:36, 09:48 (×2) | indoor daylight | 1/14 s ISO 880 | 109-115 / 60-62 / 142-146 | whole frame purple, scene almost gone |
  Photo, Ultra HD, ultra-wide and LMC shots of the same scene minutes apart have normal colour → the fault is in the Night path.
* Logs: every preview frame `RealTimeFeatureSuperNightPreviewRaw_ChiNodeWrapper13 … Output Port/Image Buffer is Null` (also at 03:13);
  the HAL SoftISP night feature is created and destroyed during stream negotiation (`ChiFeature2SoftIspSuperNight`, "Could not extract
  snapshot stream"); in the app the MIA node `MMCP` receives the burst (1/3/5 frames) and logs `No child node to process the current
  image` → [Inferred] the night graph has no actual night-merge node on this port, and an unprocessed intermediate (wrong chroma) is saved.
  Vendor has `libarcsoft_super_night_raw.so`, `com.qti.feature2.{rawsupernight,softispsupernight}.so`.
* Earlier mode tests only checked that Night opens and saves; the colour was never checked → "Night works" in P1 was wrong.
* Until fixed: **use LMC for dark scenes** (normal colour, more detail); Photo mode in the dark is dark but correct in colour.
* Session logged from its start (09:51): MIA graph **ID 9 ("superNight mode supported") = one node, `MiaNodeMemcpy`** → the app only copies
  what the HAL delivers; the night merge is expected in the HAL, whose SuperNight realtime pipeline fails
  (`ChiNodeWrapper13 … Output Port/Image Buffer is Null` every frame, SoftISP night feature dropped in stream negotiation).
* Test 09:52 with the **stock HyperOS 1 `camxoverridesettings.txt`** (without the port's `HighQualityQuickShotSupportMask=0x000000`,
  runtime bind-mount, reverted): Night still purple (mean RGB 130/74/160), Photo normal → that port line is **not** the cause.
* Remaining causes are in the HAL / CHI SuperNight usecase as driven by camera 6.7 (request contents the 2022 HAL does not expect).
  Fix needs HAL-level work (CHI node 13 of `RealTimeFeatureSuperNightPreviewRaw`) → parked as an open bug; workaround LMC.


## Zoom photos (2x and up) were never zoomed — found and fixed in camera v13 (2026-10-30 09:54-10:08) [Observed]
* Stand test, "2.0X zoom" verified selected in the UI before the shutter: the saved photo had the **1x field of view**, heavy colour noise
  and darker tones (repeated with the stock `camxoverridesettings.txt` → not caused by the port's HighQualityQuickShot line).
* Log: at 2x+ the app shoots a **super-resolution burst** (`shouldDoSR: true`, algoType 3, 8 frames, crop region set). The MIA graph has
  no SR node (HDR bypass → SkinBeautifier → AIIE `ERROR init false`) and the HAL SR path is off → one unmerged, uncropped frame is saved.
* SR is allowed by the Marble profile (`u6()` = true, plus pref `pref_camera_sr_enable_key`). With SR off the app uses the normal
  5-frame path (algoType 7) and the HAL applies the crop → correct zoom, normal colour.
* **Camera v13** (`camera_watermark_patch.sh`, Marble `u6()` true → false; sha 3a76a1e3). First attempt appended a second `u6()`
  (the original is `public final`) and changed nothing — the script now patches the existing body and asserts there is only one.
  Tested with clean prefs: 0.6x 2448x3264, 1x/2x/5x 4624x3472, all correct framing, no crash.
* Installed: v13 runs as app update now; `munch_cam_watermark` holds v13 for the next boot (package cache cleared); ROM payload = v13.
  v12 dropped (v13 contains it). Rollback = v11.

## P0 baseline sheet, back cameras (2026-10-30 10:01-10:08, camera v13, stand, indoor window light, LMC 8.4 for comparison) [Observed]
| Shot | Size | Exposure | Detail (Laplacian) | Noise | Highlights / shadows clipped | L* | Chroma | Notes |
|---|---|---|---|---|---|---|---|---|
| Native 0.6x (UW) | 2448x3264 | 1/20 ISO 518 | 44.1 | 0.81 | 1.07 / 0.60 % | 24.0 | 5.5 | works since v12; darker, window blown |
| Native 1x | 4624x3472 | 1/20 ISO 1749 | 13.1 | 0.44 | 0.34 / 0.29 % | 33.6 | 8.6 | soft (known) |
| Native 2x | 4624x3472 | 1/20 ISO 2282 | 13.3 | 0.48 | 0.01 / 0 % | 41.3 | 8.5 | works since v13 (crop) |
| Native 5x | 4624x3472 | 1/17 ISO 2920 | 13.9 | 0.51 | 0 / 0 % | 41.7 | 6.2 | digital crop, works since v13 |
| Native Ultra HD | 9248x6944 | 1/20 ISO 1829 | 13.2 | 0.49 | 0.22 / 0.32 % | 34.8 | 9.1 | 64 MP remosaic, no extra detail at this light |
| Native Night | 4624x3472 | 1/14 ISO 880 | — | — | — | — | — | **purple output (open bug)** |
| LMC 8.4 1x | 4624x3472 | 1/10 ISO 824 | 96.6 | 1.70 | 0.03 / 0.71 % | 39.2 | 11.6 | most detail, brighter, more colour |
* Detail numbers are per full image at native size (UW and Ultra HD not rescaled), so compare within the same size only.
* Front camera and Portrait are not in this sheet (stand points the back camera at the scene; back Portrait = open crash).

## Pre-flash regression of camera v13 on the phone (2026-10-30 10:10-10:19) [Observed]
| Check | Result |
|---|---|
| Guarded sweep of all 16 visible modes (Pro, Video, Photo, Documents, Night, Ultra HD, ID photo, Slow motion, Time-lapse, Movie, Long exposure, Dual video, Panorama, Sticker avatars, Xiaomi Short Video, Short video) | all open, **0 crashes** in the crash buffer |
| Back photo 0.6x / 1x / 2x / 5x, Ultra HD | correct size and framing (baseline sheet above) |
| Front photo | 3904x5184 (20 MP, v11 fix kept) |
| Video (owner setting 1080p60) | HEVC 1920x1080, 60.02 fps, 39.8 Mbit/s, file plays |
| Known open | Night mode purple output; back Portrait crash (LMC works) |
The full P9 regression (after flashing the ROM) repeats this plus heat and LMC.

## Results after 2026-10-30
Later sweeps, the hidden modes (v14), long-video results (v15), daylight and noise-reduction tests and call results: `OWNER_TESTS_2026-10-30.md`.
