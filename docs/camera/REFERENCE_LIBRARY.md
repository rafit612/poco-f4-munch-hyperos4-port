# Reference photo library (MASTER_PLAN Step 17, phase P0)

The photos themselves stay on the pendrive archive (`poco_f4_munch_archive/`); this file holds the method and results.
Index: `camera_project/reference_library/index.csv` (built by `tools/camera_lab/build_reference_index.py`).

## Sets
| Set | Meaning | Folder on the pendrive | Role |
|---|---|---|---|
| A | Own phone photos = what our ROM produces | `phone_photos_*` (+ every future test shot, tagged with the build) | "before" evidence, failure cases, progress history |
| B | Xiaomi 17 / 17T Pro | `xiaomi17_reference_photos` | target look (colour, tone, HDR rendering) |
| C | POCO F4 by other people (stock software) | `other_people_pocof4_sample_photos` | stock POCO F4 baseline |

## First index (2026-10-28, Commons download still running: 26 of 103)
| Set | Source | Photos | Detail-grade | Camera models (EXIF) |
|---|---|---|---|---|
| A | Camera (own) | 92 + 19 videos | 92 | "POCO F4 5G" (49), 22021211RG (25), unknown (20) |
| B | dpreview | 47 | 47 | Xiaomi 17T Pro |
| B | Drive folder | 11 | 11 | Xiaomi 17 (10) |
| B | photobohemian | 64 | 0 (web-sized) | — |
| B | Flickr | 1 | 0 (web-sized) | — |
| C | Wikimedia Commons | 103 | 103 | 22021211RG (102), 22021211RI (1) (re-indexed 2026-10-30) |
| C | review sites | 101 | 0 (web-sized) | 22021211RI (32 still have EXIF), unknown (69) |

ISO medians: **A 448** (max 4358) · **B 50** (max 500) · **C 66** (max 907, 135 photos with ISO).

## Consequences for the method [Observed]
1. Set A is mostly indoor / low-light, sets B and C mostly daylight → every comparison is done **per scene class and ISO band** (daylight ≤ ISO 100, indoor 100–800, low light > 800). A global comparison would wrongly blame the ROM for what is only lighting.
2. Detail and noise are measured only on `detail_ok=yes` files (originals). Web-sized photos (photobohemian, Flickr, review sites) are used for colour/tone tendencies only.
3. Set A needs **daylight shots of the same kind of scenes** as B/C (outdoor, buildings, sky, greenery, people) — part of the P0 test-scene capture.
4. EXIF Model "POCO F4 5G" in set A comes from our patched camera profile (watermark fix); "22021211RG" files are from GCam/LMC or older builds — the index keeps the app/build per photo so before/after can be separated.

## First measured baseline — indoor, ISO 100–800 (2026-10-28) [Observed]
Script: `tools/camera_lab/measure_photos.py` (centre-crop sharpness = Laplacian variance, noise sigma, clipped %, CIE L*/C*, a*/b* of
near-neutral pixels). Medians per set (originals only):
| Set | Photos | Sharpness | Noise | Highlights clipped | Shadows clipped | L* | L* std | Chroma C* | wb a* | wb b* |
|---|---|---|---|---|---|---|---|---|---|---|
| A own (older builds / GCam) | 66 | 38.9 | 0.65 | 0.18 % | 0 % | 46.3 | 21.9 | 11.9 | +0.28 | +2.37 |
| B Xiaomi 17 / 17T Pro | 12 | **71.8** | 0.59 | **0.03 %** | 0 % | 46.1 | 21.1 | **17.4** | +1.16 | +3.12 |
| A new: camera v7, office LED, 2026-10-28 | 3 | 38.2 | 0.56 | 1.41 % | 0 % | 50.0 | 20.5 | 15.8 | +0.21 | +2.42 |
Reading [Inferred, small samples, different scenes]:
* At the same noise level the Xiaomi 17 keeps about **2× the fine detail** → our noise reduction / sharpening balance is the first target
  (IPE `anr10`/`tf20` vs `asf30` in Chromatix, or our own L3 detail stage).
* Xiaomi 17 **protects highlights** far better (0.03 % vs 1.4 % blown) → HDR / tone mapping (`ltm14`, `gtm10`) target.
* Colourfulness of v7 (15.8) is already close to the Xiaomi 17 (17.4) and much higher than older own photos (11.9, Leica filter set now on).
* White balance: all sets slightly warm; Xiaomi 17 a little warmer and more magenta (+1.2 a*). Skin needs the face test shots.
* Caveats: the Xiaomi 17 sensor is much larger; scenes differ; daylight band still empty for own photos (owner's daylight shots pending).

## Daylight band, first look (2026-10-28, owner's batch 2) [Observed]
Medians, ISO ≤ 100 originals: C stock POCO F4 (24, Commons) sharpness **2315**, noise 3.8, chroma 10.6, b* −2.7 · B Xiaomi 17 (37)
sharpness **517**, noise 1.0, chroma 11.1, b* +0.4 · **v7 daylight main (7)** sharpness **27** (range 10–100), noise 0.46, chroma 7.9, b* +2.1.
100 % crops confirm by eye: v7 city shots are soft and smeared; stock POCO F4 is crisp (over-sharpened grass); Xiaomi 17 clean.
**Not yet attributable** [Inferred]: all v7 daylight shots were taken from inside an office through window glass (two straight into the sun,
excluded), and sharpness varies 10× between frames → glass / reflections / focus can explain part of it, heavy noise reduction (noise
0.46 vs 1.0–3.8) the rest. Needed: paired test — same scene, same spot, Xiaomi camera vs LMC, window open or outdoors (plus one through glass).

## Paired test, same sensor and light: LMC vs Xiaomi camera v7 (2026-10-28 16:15, window open, ISO ~50, LV 10–11.7) [Observed]
| App | Photos | Sharpness (median) | Noise | Chroma C* | wb b* |
|---|---|---|---|---|---|
| LMC 8.4 (Google HDR+ processing) | 8 | **232** | 1.67 | **13.1** | +2.7 |
| Xiaomi camera 6.7 (v7, Marble profile) | 7 | **36** | 0.46 | **6.0** | +0.7 |
100 % crops (same buildings): LMC crisp (railings, AC units, tank text readable); Xiaomi soft, "watercolour" smearing, low micro-contrast.
**Conclusion:** the softness and dull colour come from the **Xiaomi camera's processing on this port**, not from window glass or the
sensor. Stock POCO F4 photos (same vendor HAL tuning, camera 5.1) are crisp (set C) → the cause is most likely what the 6.7 app with the
Marble (POCO F5) profile requests or post-processes (noise-reduction level, sharpness/denoise vendor tags, MFNR/AIIE path), not the
Chromatix tuning file. → P8 item 1 starts with the app side: dump the Photo capture request vendor tags and the MIA node chain, compare
with what camera 5.1 sent on stock.

## Soft-photo A/B lab (phone fixed on a stand, same indoor scene, ISO ~720) [Observed]
| Variant | Sharpness | Noise | Chroma |
|---|---|---|---|
| LMC 8.4 | **156** | 1.87 | 22.3 |
| Xiaomi v7 normal (×2, identical) | 13.5 | 0.41 | 20.2 |
| Xiaomi v7 Leica Vibrant | 16.1 | 0.44 | 21.8 |
| Xiaomi, HAL MFNR tag forced off (`r9.b.O`) | 20.7 | 0.49 | 15.9 |
| + AIIE bypass property | 20.0 | 0.48 | 15.9 |
* Capture chain (log): app multi-frame burst (5 frames, `ShotParallelBurst`, `doMFNR=true` even with the HAL tag off) → HAL MFNR →
  MIA HDR (bypassed) → SkinBeautifier (all 0) → AIIE (R0.4.9) → JPEG.
* MFNR tag off: +50 % detail, still ~8× below LMC. AIIE bypass: no change (log still shows `AIIECapture enabled: 1`). Leica style: no change.
* The output is already very clean (noise 0.4–0.5 vs LMC 1.9) → the main smoothing happens earlier, in the HAL snapshot noise
  reduction / multi-frame path for normal Photo, not in the app's post steps. Next: switch off the app-level 5-frame burst
  (`ShotParallelBurst` / `Camera2Module.mfnrNeeded`) to get a true single-frame capture, and compare the HAL's single-frame output.
* "Pro" in this camera opens Pro **video** (`ProRecModule`); the photo Pro module (167) is not in the mode bar.
* Single-frame test (`Camera2Module.shouldDoMultiFrameCapture` → false + MFNR tag off): the app falls back to shot type 5 and saves a
  **1440×1080** image from the preview stream → not comparable; the app has no full-resolution single-frame path in normal Photo.

## Capture settings, Xiaomi camera vs LMC (`cmd media.camera watch`, 2026-10-28) [Observed]
| | Capture | noiseReduction.mode | edge.mode |
|---|---|---|---|
| Xiaomi camera v7 photo | separate `STILL_CAPTURE` request + app 5-frame burst + HAL MFNR (HAL snapshot pipeline) | HIGH_QUALITY (template default; the app never sets it) | HIGH_QUALITY |
| LMC 8.4 photo | frames taken from the repeating `PREVIEW` stream, merged and sharpened by Google's software | HIGH_QUALITY | **FAST** |
* Test build forcing `noiseReduction.mode = FAST` on the still request: the request carried FAST, but the app saved a **1440×1080**
  frame (same preview-size fallback as the single-frame test) → the app's 64 MP path only completes with its default settings.
* **Correction (2026-10-28 evening):** the "1440×1080 fallback" of the single-frame and NR-FAST builds was most likely a measuring
  error: in parallel mode the camera first saves a preview-size placeholder and replaces it with the processed photo seconds later,
  and `ab_shot.py` pulled the file after 2 s. `ab_shot.py` now waits until the file size is stable for 5 s.
* **Correction:** the phone was moved between the morning baseline (`xiaomi_normal_*`, LMC) and the later path-2 shots, so "noi8 18.0 /
  noi8 + MFNR off 16.0 vs normal 13.5" compared different scenes. Same scene (mug, 18:00): stock v7 12.6 and 16.5 (two shots),
  `Marble.i8()` false 18.0, + MFNR off 16.0, L4 test t1b 18.1 → shot-to-shot spread is as large as every change; **no app-level or
  ANR change has a proven effect yet**. A/B tests need ≥ 2 shots per variant, alternating, with an LMC shot in the same series.
* Radial spectrum (2048² centre crop, morning scene): Xiaomi has more energy than LMC below 0.3 × Nyquist (coarse edges sharpened)
  and ~10× less above 0.4 × Nyquist; scaled to 1080p Xiaomi is not softer than LMC. Part of LMC's fine-band energy is noise
  (noise 1.9 vs 0.45), so the spectrum overstates LMC's real detail.

## L4 tuning tests (Chromatix, main camera `com.qti.tuned.munch_sunny_ov64b40_wide.bin`) [Observed]
* Format read with `tools/re/chromatix_read.py` (own reader; layout from go-chromatix2libcamera). Index section = mode tree:
  records (node id, type, value, parent); type 1 sensor mode, 2 usecase, 3 Feature1, 4 Feature2, 5 scene, 6 effect, mode value in the
  upper 16 bits; child nodes 1–10 are per-block module sets (3 = IPE). Sensor mode 1 has usecase 0 (preview) and usecase 1
  (snapshot, 6 Feature1 × several Feature2 branches). ANR10 chain: lens → zoom → post-scale → pre-scale → DRC gain → HDR/AEC regions
  (gain triggers, e.g. snapshot 1–1.5 … 300–512) → 12 208-byte parameter block.
* **t1** (snapshot `anr10_ipe` symbols pointed at the preview module's data): HAL rejects the file — `CreateTunedModeTree() Couldn't
  create Tuning Mode Tree!`, then provider abort (Scudo double free) in a loop. Rolled back by disabling the module. Rule: every symbol
  must keep its own data range.
* **t1b** (preview ANR parameter blocks copied into all 1034 snapshot blocks by nearest gain region, no ids/sizes/pointers changed):
  loads and captures normally; sharpness 18.1 vs stock 12.6/16.5 on the same scene → no clear effect. Module `cam_l4_test` left
  **disabled**; phone runs stock tuning.

## Owner's night batch (2026-10-28 18:08–19:15, street from a moving rickshaw, kept local: people + GPS) [Observed]
| | Xiaomi v7 Photo (8 full-size) | LMC 8.4 `POCO-F4-ONE` (5) |
|---|---|---|
| Exposure | ISO 640–1580, 1/33–1/20 s | ISO 47–182 at 1/21–1/15 s (one ISO 1522, 1/10 s) |
| Sharpness / noise | 13–28 / 0.4–0.56 | 66–309 / 1.5–2.9 |
| Highlight clipping | 1.0–1.6 % (signs, lamps blown) | 0.01–0.11 % |
| Chroma (colour) | 4.5–9.6 (pale) | 12–23.5 |
* Xiaomi Photo does not switch to a night/long-exposure path on its own here; motion blur from the rickshaw adds to the softness.
* Auto night in Photo mode (code, camera 6.7): `Camera2Module.isNightOn()` = module 163 && profile `t6()` (Marble: **true**) && no
  conflicting setting && `NightManager.j > 0`; `j` is the super-night capture time the HAL's AI ASD reports per frame
  (`u6.z0` → `o6.J` → `o6.I`), used only when it exceeds profile `b0()` (Marble inherits Common). HAL night tags the app asks for but
  this HAL lacks: `xiaomi.capabilities.MIVISuperNightSupportMask`, `SupernightManualEVMask`, `xiaomi.ai.asd.extremeDarkSeResult`,
  `xiaomi.supernight.aeplinechecker`, supportedfeatures `MfnrSupernight` (present: `xiaomi.supernight.checker/enabled`,
  `xiaomi.ai.misd.superNightCaptureMode/SuperNightCaptureExpTime`).
* Probe 29 Oct (Photo preview, room light, lux index ~280, ISO ~700): no "super night" app log at all; HAL logs
  `XIAOMI_AIASD: checkerStatus=2` every frame and ~900 blocked reads/min of `persist.camera.aiasd.isovalue` (no context in
  vendor_property_contexts → `default_prop`; [Inferred] debug override, HAL uses its default — log noise, not the cause).
  Dark-scene probe still to do (evening; logs kept in `~/camera_builds/logs/`).
* **Bug:** 4 Xiaomi photos taken in quick succession just before switching to LMC (18:38:33–18:38:48) were saved as **1440×1080
  placeholders padded to exactly 16 MB, without EXIF** — the processed photo never replaced them. [Inferred] Pending parallel
  processing is lost when the camera app is left/killed early. To reproduce and fix (P8).
  * File layout: valid 130–200 KB preview JPEG (with EXIF) + ~16.6 MB of zeros — the file is pre-allocated to 16 MiB for the final
    image, the preview is written first, the final write never happened. Nothing beyond the preview is recoverable.
  * Code (camera 6.7, classes11): `Up.b/Up.f.A0` drop the final image when the task is flagged abandoned
    ("onFinalImageReceived: return because the task is abandoned"); `Xp.m$b.a` (`onParallelDataAbandoned`) only logs
    "should remove record …?" and leaves the placeholder file in place.
  * Not reproduced in good indoor light (fast processing): 4 quick shots + HOME, 4 quick shots + opening LMC (camera evicted 3 s after
    the last shot), 2 quick shots + switch to Video — all photos finished at full size. [Inferred] Needs night processing (several
    seconds per photo, queue of pending shots) plus a video switch / other camera app taking the sensor. Workaround: wait until the
    thumbnail stops spinning before switching to video or another camera app.
  * Cause in code: `Camera2Module.checkCaptureStartDeparted` marks a shot abandoned (`di.A.q`) when its capture start arrives after
    the mode was left; only MediaTek profiles (Corot, Duchamp, Aristotle: `l5()` true → `Te.b.d0()`) skip this. Processing the shot
    anyway would need the output parameters that `updateParallelTaskData` sets from the live mode → not done (crash risk).
  * **Fix in camera v8** (`tools/re/PlaceholderTrim.java`, block 4 of `camera_watermark_patch.sh`): on abandon (`Up.b/Up.f.A0`,
    `Xp.m$b.a`) the placeholder is cut after its last non-zero byte (only files ≥ 8 MiB starting with FFD8 and ending in ≥ 1 MiB of
    zeros). Laptop test on copies of the 4 broken files: 16 MiB → 130–200 KB, all decode; a normal photo stays byte-identical.
    Installed 2026-10-28 (sha a0b4e02c): normal shots full size, no crash. Night re-test pending (log tag `MunchPlaceholderTrim`).
* Reading [Inferred]: the detail is lost in the HAL **snapshot** pipeline (BPS/IPE snapshot tuning + MFNR), which LMC never uses.
  Options: (a) find which of the app's still-capture parameters can change without triggering the fallback; (b) tune the
  snapshot-path noise reduction (Chromatix L4, approval needed); (c) own sharpening/detail stage (L3) on the saved JPEG — cannot restore
  detail that was removed; (d) recommend LMC for detail-critical photos until (a)/(b) succeed.

## LMC: one config `POCO-F4-ONE.xml` (2026-10-28) [Observed]
* The 12 own configs differ from `POCO-F4-FINAL.xml` only in 11–13 "look" keys (contrast, gamma preset, tone-curve preset per lens),
  plus 60 fps / zoom keys in bubnois and A2Z; ULTIMATE is a different base (~1000 differences).
* Look test on the fixed desk scene (LMC, only look keys changed): chroma FINAL 18.6, Vibrant 18.3, Authentic 20.1 (harder contrast,
  0.28 % clipped), Pixel 18.2, Zeiss 18.5 (warm/darker), **iPhone 19.8 (contrast 24.1, 0 % clipped)**, Samsung 26.3 (too punchy).
* `POCO-F4-ONE.xml` = FINAL base + iPhone look (owner's "in between" target) + `camera.60fps` / `camcorder.4k60fps` = true (defaults stay
  30 fps). Imported on the phone; config folder now holds only this file. All 20 previous phone configs backed up on the pendrive
  (`camera_project/lmc_configs_backup_2026-10-28/`).

## LMC video (2026-10-29) [Observed]
* Before: `pref_video_hevc_setting_key` 0 (H.264), `pref_bitrate_key` 0 (Auto) → walking clips 4K30 33, 4K60 50, 1080p60 20 Mbit/s.
* `POCO-F4-ONE.xml` now: HEVC 1 (switch stored as "1"), bitrate option 16 = 80 Mbit/s (LMC options 0 Auto … 18 = 120 Mbit/s; one value
  for every resolution). Applied directly in LMC's prefs file (root; backup `~/camera_builds/lmc_prefs_backup_2026-10-29.xml`; keep the
  file's MLS label `s0:c41,c257,c512,c768` — `sed -i` drops it) and in the xml on the phone. Test clip: HEVC 1920×1080@60, 80.0 Mbit/s.
* Phone LMC folder holds only `POCO-F4-ONE.xml` (owner: one config). 12 older xmls removed; all on the pendrive
  (`lmc_configs_backup_2026-10-28/`, the differing FINAL copy as `POCO-F4-FINAL.phone_copy_2026-10-29.xml`).
* Automation note: LMC draws a landscape UI while the phone lies sideways; start video with
  `am start -a android.media.action.VIDEO_CAMERA -p org.codeaurora.snapcam` and `KEYCODE_CAMERA` instead of taps.

## Owner evening set 2 (2026-10-29 18:16-20:18, 37 files: 18 native, 19 LMC) [Observed]
Copied to `~/camera_photos_private/2026-10-29_owner_evening2/` (local only: people, number plates, GPS); to be archived on the
pendrive. Phone copies untouched.
* **Native back camera at night (street):** Photo mode chose ISO 330-790 at 1/25-1/50 s; result dark, soft and smeared,
  headlights bloom into large white blobs, crushed shadows. Auto night did not trigger. LMC (ISO 44-227, 1/9-1/25 s,
  multi-frame) is clearly brighter, cleaner and more detailed, but has strong star flares and motion blur on moving people.
  -> confirms the open "Night: native Photo blown highlights" item.
* **Native front camera bug (new):** `IMG_20261029_201752.jpg` = front IMX596 (f 2.84 mm), saved at **1200x1600, 0.4 MB,
  ISO 2572, with red/blue (U/V) swapped colours** (navy shirt -> maroon, skin -> cyan). 1200x1600 is a preview size: the
  native app kept only its preview/placeholder frame and the processed selfie never arrived; the preview-to-JPEG path also
  has chroma swapped. LMC front shots at the same time (1952x2592, normal + PORTRAIT with blur) have correct colours.
  -> front-camera track: find why the native front capture drops the processed frame + the U/V swap.
* **Native back Portrait** crashed once (19:37:23, known `layout.shape` abort; parked). LMC Portrait works.
* **Native video** bitrates in real use match the v9 table: 4K30 60, 4K60 100, 1080p60 40, 1080p30 25, 720p30 12 Mbit/s HEVC,
  AAC 320 kbit/s, BT.709 tags.
* **LMC video:** HEVC ~80 Mbit/s (POCO-F4-ONE.xml); real frame rates 30/60 (some files carry a 120 fps container rate but
  contain 30 fps); **LMC 1080p is tagged smpte170m/bt470bg (SD colour) instead of bt709** -> possible slight colour shift
  in players; 4K is tagged bt709. One 2 s LMC 4K clip has no audio track.

## Owner set 3: selfies after the v11 front fix (2026-10-29 21:33, 7 native + 4 LMC, indoor low light) [Observed]
* Native front now saves **5184x3904** (20 MP, ~3.7 MB) with correct colours - the v11 fix holds in real use.
  ISO ~1550, 1/20 s (LMC: 2592x1952, ISO ~1130, 1/18 s).
* Detail (100% crop): native is soft and smoothed (skin texture gone, hair mushy, slightly washed colour); LMC is clearly
  sharper (skin texture, hair strands). Native log: `updateBeauty(): 3d beauty level ... ss: 20 | sf: 40` and the MIA
  `MiaNodeSkinBeautifier` node runs on every front shot (700-1200 ms) although the beauty switches in settings are false
  -> a base "natural" beauty level is applied. Also the 20 MP full-resolution (remosaic) mode at ISO 1500 is noisier
  than the 4-in-1 binned 2592x1952 that LMC uses.
* Options (owner choice): lower/turn off native front beauty in the app UI; or test making the native front default to
  the binned 2592x1952 (cleaner in low light) instead of 20 MP.
* Camera cache: 21 empty 0-byte `VID_*.mp4` placeholders in the app cache removed (no content, no DCIM counterpart).
* LMC 1080p video colour tag (smpte170m/bt470bg instead of bt709): LMC's config and prefs only have photo colour keys
  (WB_color_space_key, pref_color_transform_key, pref_color_key); nothing controls the video container colour tag, which
  comes from LMC's recorder/encoder path (4K is tagged bt709 correctly). Minor (slight colour difference in some players);
  closed as an LMC limitation, no change.
* Selfie A/B (2026-10-29 21:40, same room scene, native front): A = 20 MP full resolution (v11 default), B = picture size
  forced to 2592x1952 via the app's size cache -> the app processes binned and upscales to 5184x3904 (3.1 vs 4.3 MB).
  B has clearly less detail (edge variance whole frame 23.6 vs 53.9) for only slightly lower noise (flat-area std 47 vs 52).
  Decision: keep 20 MP (v11). The softer native selfies come mainly from Xiaomi's base front beauty (owner can lower/turn
  off in the front beauty menu). Cache entry removed again (app recalculates 5184x3904).

## Soft photos: clean A/B on a stand (2026-10-30 02:16-02:22, static indoor scene, v11) [Observed]
Phone fixed on its stand, same scene, alternating shots, detail = Laplacian variance per region (same crop, no rescale),
`tools/camera_lab/ab_shot.py` (LMC now triggered with the camera key - a fixed tap misses its rotated shutter):
| Region | Native #1 / #2 | L4 t1b on #1 / #2 | LMC #1 |
|---|---|---|---|
| centre (door knob) | 61.9 / 62.5 | 60.1 / 60.2 | 235.6 |
| textile (top) | 23.3 / 23.9 | 21.8 / 21.9 | 134.0 |
| wall (dark, flat) | 79.9 / 79.7 | 76.5 / 77.4 | 525.7 |
* Repeatable within ~3 % per camera - the stand removed the shot-to-shot spread that made the 2026-10-28 tests inconclusive.
* **Native main-camera photos carry 4-6x less fine detail than LMC on the same static scene** (LMC is also brighter and
  sharpens/keeps more noise: wall std 6.7 vs 3.9). The softness is real and systematic, not shake.
* **L4 t1b (snapshot ANR = preview ANR in the Chromatix file) makes no difference** (detail equal or slightly lower) ->
  the Chromatix snapshot ANR is not the cause. Module `cam_l4_test` disabled again.
* Remaining suspects for the native softness: the app's MIA graph on every photo (HDR → SkinBeautifier → AIIE) and the
  HAL MFNR merge; the earlier v8exp builds without AIIE (`i8`) / without MFNR are on the pendrive and can now be re-measured
  the same way on the stand (needs adb root, lost after the 02:24 reboot - owner re-grant in ReSukiSU).

## Soft photos path 2: v11 vs no-AIIE / no-MFNR builds on the stand (2026-10-30 02:49-02:54) [Observed, low confidence]
Builds installed as **app updates** (`adb install -r`, same debug key as the system copy) and rolled back with
`pm uninstall-system-updates com.android.camera` → no reboot, no module change; v11 hash c8eb90f4 verified afterwards. Script
`~/camera_builds/tmp/soft_ab.sh`, metric `tools/camera_lab/tile_detail.py` (Laplacian variance per 3x3 tile, mean of 9).
* Scene was **not stable**: dark room at night (ISO 1257-8500) lit by a colour-cycling RGB lamp + live monitors, and the framing
  shifted after the 3rd build → only pairs with matching light/framing are compared:

| Pair (same light) | Exposure | Mean tile detail | Noise (flat tile) |
|---|---|---|---|
| v11 #1 / #2 vs **no MFNR** #1 / #2 | 1/14 s ISO 8500 | 20.6 / 21.2 vs 22.0 / 21.9 | 0.41 / 0.42 vs 0.44 / 0.43 |
| v11 (end) #1 / #2 vs **no AIIE + no MFNR** #1 / #2 | 1/17 s ISO 1257-1458 | 23.0 / 23.3 vs 22.9 / 24.0 | 1.17 / 1.26 vs 1.15 / 1.25 |
| no AIIE #1 / #2 (different light, ISO 4978) | 1/8 s | 23.4 / 24.4 | 0.72 / 0.88 |

* Reading: switching off MFNR (+≈5 %) or AIIE+MFNR (±0) does **not** come near the 4-6x gap to LMC → the main softness is very likely
  before the app's AIIE node and the HAL MFNR merge (ISP/IPE noise reduction in the realtime path, or the HDR/beauty nodes). In this
  low light every path is noise-limited, so this is a hint, not a result.
* To repeat in steady light (daylight, or RGB lamp off): same script, ≈ 6 min, no root needed for the install method.

## Night: why Photo never switches to SuperNight on its own (2026-10-30, lead, not fixed) [Observed + code trace]
* Dark stand scene, 1/14 s ISO 8500 (camera v11): the HAL scene detector reports night (`getAsdNightResult : 1`, `XIAOMI_AIASD`
  active, `applyAiASDEnable:true`), but the app keeps `applySuperNightScene: false`, `SuperNightSePriority: false` and logs
  `super night changed: false` 58 times; `MarshalQueryableDxoAsdScene: Expected size should be 8, but got: 0` (one scene tag arrives
  empty). Same behaviour as the owner's street shots (Xiaomi Photo did not go to the night path).
* Code path (v7 dex, same in v11): `Camera2Module.prepareNormalCapture` → `o6.x.m()` (NightManager, feature key
  `isSupportedSuperNightScene`; Marble `z7()` = 0 so its first gate passes) → `updateSuperNight` → `o6.J` (SuperNightCbImageImpl)
  `a()/b()` → pref `pref_camera_super_night_mode`. None of NightManager's own log lines appear → it returns before
  `updateSuperNight`; candidates: the night-motion / scene result read from vendor tags the munch HAL does not define
  (`xiaomi.ai.misd.isMotionScene`, `CaptureExpTime` … are missing, `superNightCaptureMode`/`StateScene` exist — `p2_vendor_tags_generated.md`).
* **Resolved by trace builds (same night, 03:05-03:14)**: label/fall-through logging builds of v11 (tag `MunchNight`, installed as app
  updates, rolled back each time) showed the full chain: `SuperNightMultipleASD.acceptResult` (u6.z0) **does** see the night scene
  (type 3 entry, "super night se enable" = true) and calls `J.b(true)`, but `J.b` and `NightManager.m()` force it off because
  `o.i0(module)` is true — `o.h0()` is hard-wired `return true` in 6.7 (Xiaomi's newer design: the HAL does night inside the normal
  Photo session, needs HAL `MfnrSupernight`, which the munch HAL does not have).
* Test build **v11 + `h0()` = false** (sha 07fd6441, pendrive `camera_project/night_trace_2026-10-30/`): Photo now switches to SuperNight
  by itself (`isSuperNightSeOn:true`, 1.3 s capture, 1/4 s ISO 877). Same scene vs v11: L* 4.3 → 15.6, crushed shadows 33.8 % → 0.6 %,
  chroma 3.9 → 9.5, highlights unchanged (0.2 %) — **but 141 vertical streak artifacts** (hot-pixel-like dashes, left 1614 px only).
* Manual **Night mode** (v11, own 0x800a session) in the same scene: brighter (luma 56.8 vs 37.3) and 0 streaks — **but with a strong purple
  cast** (mean RGB 70/45/84; corrected 2026-10-30 09:50, first check only measured luma/streaks). See `MODE_TEST_RESULTS.md` "Night mode purple".
* Decision: `h0` off is **not shipped** (streaks = the Photo-session night path is not supported by this HAL). For dark scenes the
  answer on this phone is LMC for dark scenes (Night mode output is purple, see test results). Possible later improvement: on a dark scene, offer a one-tap switch to Night mode
  instead of running night inside Photo (UI work in the app, not started).

## Soft photos path 2 repeat in steady daylight (2026-10-30 08:59-09:04, same stand, window light, 1/17 s ISO 1415-1741) [Observed]
Same script and order (v11 → no-AIIE → no-MFNR → no-AIIE+no-MFNR → v11). Frames aligned within 3-7 px. Raw Laplacian detail is
inflated by brighter shadows (no-AIIE lifts shadows), so detail is measured on log-luma (central 65 % crop):

| Build | Luma | Detail (log-luma) | Noise |
|---|---|---|---|
| v11 (start) | 90.2 / 90.7 | 21.8 / 22.8 | 1.06 / 1.07 |
| no AIIE | 95.2 / 87.6 | 13.6 / 20.4 | 1.18 / 1.11 |
| no MFNR | 89.9 / 89.0 | 25.5 / 27.0 | 1.08 / 1.09 |
| no AIIE + no MFNR | 90.7 / 91.0 | 25.9 / 24.6 | 1.09 / 1.07 |
| v11 (end) | 89.6 / 90.2 | 26.2 / 24.6 | 1.08 / 1.06 |

* v11 start → end drifts ≈ 12 % (daylight change). Within that, **no build adds detail**: no-MFNR and no-AIIE+no-MFNR equal v11,
  no-AIIE only lifts shadows a little (less consistently). → **Path 2 closed: the app's AIIE node and the HAL MFNR merge are not the
  cause of the soft native photos.**
* What remains is the ISP realtime path (IPE noise reduction / ASF sharpening strength in the Chromatix file). t1b (whole snapshot
  ANR blocks = preview) changed nothing; the next step would need the meaning of individual fields (ANR/ASF strength), which our
  reader cannot map → path 1 parked. Practical answer stays: LMC for detail (path 3, done), or our own sharpening stage (L3, 07 §5).

## Autofocus check: is the soft native photo a focus problem? (2026-10-30 22:08, camera v13 flashed, stand, dim room ISO 650-800) [Observed]
6 native shots (fresh app start each) and 3 LMC 8.4 shots of the same scene within 3 minutes; Laplacian variance per 3x3 tile (`tile_detail.py`):
| Camera | Tile mean (9 tiles) per shot | Flat-area noise |
|---|---|---|
| Native v13 | 21.5, 15.5, 19.9, 20.7, 20.2, 20.6 | 0.7-1.15 |
| LMC 8.4 | 344, 323, 328 | 1.8 |
* **No random focus misses**: native shots 4-6 differ by < 3 %, LMC by < 7 %. Both are sharpest in the same tiles (bottom row, t6-t8) → both focus on the same plane.
* The gap is **~16-20x here (dim light)**, vs 4-6x in the daylight stand test: it grows as light drops → the native noise reduction, not focus, removes the detail.
* Native capture log: continuous-picture AF (`applyAfMode: focusMode=4`) on every shot; no AF errors.
* Conclusion: AF ruled out as the cause of soft native photos. Remaining lever = the realtime ISP noise reduction / sharpening (Chromatix) or our own post stage (`08_PHOTO_STAGE.md`).

## Why native photos are smooth/soft: the HAL noise-reduction lever (2026-10-30 22:00-22:35, stand, dim room ISO ~650-875) [Observed]
**1. The HAL honours Camera2 noise-reduction (NR) and edge modes** (own test app `tools/camera_lab/nr_probe/`, camera 0, 3264x2448 JPEG, same scene/exposure,
results echo the requested modes). `android.noiseReduction.availableNoiseReductionModes` = [0 off, 1 fast, 2 high quality, 3 minimal, 4 zsl], edge = [0 off, 1 fast, 2 hq, 3 zsl].
| NR / edge | JPEG size | Tile Laplacian | Flat-area noise | Look at 100 % |
|---|---|---|---|---|
| HQ / HQ | 1.17 MB | 6.7 | 0.43 | very smooth, smeared |
| fast / fast | 1.39 MB | 16.1 | 0.54 | slightly crisper, clean |
| minimal / off | 2.86 MB | 141 | 2.0 | sharp, grainy |
| off / off | 3.28 MB | 318 | 2.8 | sharp, grainier |
| minimal / HQ | 3.69 MB | 588 | 3.8 | crunchy |
| off / HQ | 4.16 MB | 1190 | 5.5 | very crunchy |
**2. The native app never sets these keys** (no reference in any dex) → it gets the HAL default for its still request, which behaves like fast/fast (tile mean ~20 at 16 MP, noise 0.72).
All app requests are built in `Eh.c.a()` (session ordinal 0 preview, **1 still capture**, 2 record, 3 video snapshot).
**3. Same lever inside the app** (`tools/re/nr_variant.sh`, 29 s per variant, installed as app update, rolled back after): same scene, same minute:
| Variant (still template) | Tile mean | Noise | JPEG | Look |
|---|---|---|---|---|
| app default (baseline, 3 shots, ±1 %) | 20.3-20.5 | 0.72 | 3.3 MB | smeared "watercolour" |
| NR fast + edge fast | 20.4-20.6 | 0.72-0.73 | 3.3 MB | identical → this is the current default |
| NR minimal + edge off | 26.0-26.2 | 1.15 | 4.8 MB | a bit cleaner/more natural, not really crisper |
| NR off + edge off (all templates) | 394 | 4.04 | 7.9 MB | LMC-level edges, strong colour speckle |
| NR minimal + edge off, preview template only | 20.3-20.8 | 0.72 | 3.3 MB | no effect (photos use the still template) |
| LMC 8.4 | 323-344 | 1.8 | ~10 MB | sharp, clean, brighter (multi-frame merge) |
**4. Post-fix test:** HAL NR off + our edge-aware denoise (`photo_stage.py --denoise 1 --detail 0.6`): tile mean 314, measured noise 1.24, **but the 100 % crops still show
luminance grain in mid-tones** (the noise number is taken in the flattest areas only). A single-frame post filter does not reach LMC's clean look.
**Conclusion:** the native softness is the HAL's high-strength noise reduction (not autofocus, not AIIE/MFNR, not Chromatix snapshot ANR). Turning it down trades smear for grain;
only "minimal + edge off" is a safe mild gain (+29 % detail, noise 0.72 → 1.15) and was NOT shipped (marginal). A real fix needs better denoising after the HAL (multi-frame or a
proper NLM/BM3D-class denoiser in the post stage) — see `08_PHOTO_STAGE.md`. AF check same day: native shots consistent, same sharp tiles as LMC.
