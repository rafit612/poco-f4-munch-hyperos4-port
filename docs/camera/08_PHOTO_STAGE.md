# 08 — Post-capture photo stage (P8, rank 1 of `07_IMPROVEMENT_PLAN.md`)

Prototype `tools/camera_lab/photo_stage.py` (Python / OpenCV, run on the laptop; EXIF + ICC copied). It works on the saved JPEG in CIE Lab:
1. **detail** — two-scale unsharp mask on L*, gated by the photo's own noise level (flat noisy areas get nothing), overshoot clamped to the local min/max (no halos);
2. **tone** — brightens only a dark photo, compresses highlights (shoulder), adds mid contrast only if the photo is flat;
3. **colour** — chroma gain toward a mean C* of 14 (Xiaomi 17: 11 daylight / 17 indoor), halved for skin hues, neutrals kept, very saturated pixels left alone.
Each step has a strength (`--detail/--tone/--colour`, 0 = off). Speed: ~6 s per 16 MP photo in numpy on the laptop (Lab conversion is half of it); a C++/NEON version on the SD870 should be ~1 s.

## Measured result (6 photos; local only, 3 contain people/GPS and are not published) [Observed]
Metrics: `lap` Laplacian variance of the centre crop, `noise` flat-area sigma, `edge` median slope of the strongest 1 % edges, `halo` % of pixels with overshoot, `clipHi` % of pixels ≥ 250, `L` median L*, `C` mean chroma.
| Photo | lap | noise | edge | halo % | clipHi % | L | C* |
|---|---|---|---|---|---|---|---|
| native v13 1x, stand, dim indoor | 2.5 → 6.8 | 0.26 → 0.23 | 8.0 → 9.5 | 0.22 → 0.39 | 0.42 → 0.25 | 28 → 33 | 8.6 → 11.2 |
| native v13 2x | 2.7 → 5.5 | 0.20 → 0.19 | 5.9 → 6.7 | 0.03 → 0.04 | 0.03 → 0.05 | 45.0 → 45.4 | 8.5 → 11.6 |
| banknote, in focus, fine print (v7) | 5.2 → 21.7 | 0.23 → 0.24 | 4.5 → 6.5 | 0.25 → 0.97 | 0 → 0 | 70.0 → 70.8 | 16.9 → 16.9 |
| office with window + person (v7) | 6.8 → 20.5 | 0.10 → 0.12 | 5.8 → 7.6 | 0.33 → 0.78 | **2.46 → 0.28** | 69.4 → 68.1 | 17.9 → 17.9 |
| portrait in front of window (v7) | 4.6 → 13.1 | 0.16 → 0.15 | 3.4 → 4.1 | 0.01 → 0.01 | **0.72 → 0.03** | 63.5 → 61.9 | 16.1 → 16.1 |
| *LMC 8.4, same stand scene (do not use)* | 19.7 → 29.3 | 0.64 → 0.58 | 6.6 → 8.0 | **1.3 → 3.2** | 0.12 → 0.28 | 37.6 → 42.0 | 11.6 → 13.1 |
Reading:
* **Highlights and colour are the clear win**: blown highlights drop 4–10× (white walls / windows keep detail); pale native shots reach C* ~11-12, and photos that already have colour are left alone. Skin hue unchanged (68.7° → 68.6°, 60.6° → 60.5°, 66.3° → 66.5°), warm-tone chroma unchanged.
* **Detail: real but limited.** On an in-focus subject with fine structure (banknote) the "watercolour" patches turn into visible line texture (Laplacian ×4, edge +46 %) with unchanged noise; at 2× strength it starts to look crunchy. On a blurred or out-of-focus frame nothing legible appears (laptop-screen text stays unreadable while LMC's is legible): the stage cannot recover what the native pipeline smeared away or what was out of focus. LMC keeps the real-detail advantage.
* **Do not run it on LMC photos**: LMC already sharpens (halo 1.3 % → 3.2 %).

## Update 2026-10-30 night: denoise option and the NR lever
* `photo_stage.py --denoise A` (edge-aware chroma blur + luma blur in flat areas) was added for photos taken with the HAL noise reduction off. On the "NR off" stand photo it raised
  nothing visibly: measured flat-area noise 4.0 → 1.2 but mid-tone grain stays at 100 % — **a single-frame denoise like this is not enough** to turn "NR off" into LMC quality.
* The root cause of soft native photos is the HAL's own NR (see `REFERENCE_LIBRARY.md`, "Why native photos are smooth/soft"); the stage's detail step only partly compensates.
  A better denoiser (non-local means / BM3D class, ideally multi-frame) is the missing piece before the HAL NR can be reduced for everyone.

## Update 2026-10-30 late: on-device app (built, tested on one photo)
* `tools/camera_lab/photo_stage_app/`: OpenCV 4.9 (Apache 2.0) + `StageEngine.java` (port of this script) + `StageJob` (JobScheduler content-trigger job on MediaStore images).
  It only handles photos owned by `com.android.camera` in `DCIM/Camera`, writes a copy to `Pictures/PhotoStage/<same name>` (EXIF date/make/model/exposure/GPS copied, Software = PhotoStage), never touches the original, runs only with battery not low. One switch in the app.
* Port check: mean pixel difference to the Python result 1.6/255 (JPEG level).
* NLM is only run when the measured flat-area noise is > 0.6 (HAL-NR photos 0.25-0.36, NR-off photo 1.15); h = 4.4 x noise, max 6.
* Speed on the SD870: 16 MP, NLM h~4.4 + detail/tone/colour = ~25 s; no NLM = ~15 s. Real photo test (IMG_20261030_225507, dim room): copy appeared ~30 s after the shutter; edge slope 5.0 -> 6.2, L 42.4 -> 44.2, C 8.1 -> 10.8, noise unchanged (0.25 -> 0.27, NLM skipped).
* Debug build today (Android shows a debuggable/16 KB-alignment dialog; OpenCV 4.9 libs are not 16 KB aligned). Release build + ROM priv-app packaging not done.

## Update 2026-10-31: in the ROM, and four real defects fixed
Found only by testing the copy in `/product` and by killing it on purpose:
1. **Memory:** the engine left every intermediate OpenCV image to the Java GC, which cannot see native memory: about 3.4 GB peak for one photo, so the system killed the app (SIGKILL, memory pressure level 4) when the camera was open. Now released explicitly: 0.96 GB (0.88 GB with denoise), output **pixel-identical** (max difference 0).
2. **Reboot:** a content-trigger job cannot be persisted. Added a BOOT_COMPLETED receiver; the job is back without opening the app (~40 s after unlock).
3. **After a kill the watcher never ran again.** Added a persisted 15-minute catch-up job that re-arms it and finishes missed photos.
4. **A photo was marked done before processing**, so a kill lost it. Now marked only after the copy is saved, max 3 tries.
5. **From `/product`, MediaProvider hides `owner_package_name`** (`owner=null`), so every photo was skipped. Added `<queries>` and a fallback: with no owner, `IMG_` in DCIM/Camera is native, LMC's `F4_...` names are skipped.
On the flashed ROM: native photo copied in ~30 s with the camera still open, LMC photo skipped. Over 24 MP is skipped by design (64 MP mode, panoramas). Worst case after a kill: the copy waits up to 15 minutes (forced run verified; the natural 15-minute timer was not waited for).
The earlier note that the stage stalled because of the panorama's memory was probably wrong: the process kill above fits better.

## What is not done
* (Done as a user app, see update above; C++/NDK port not needed at this speed.) Original plan: small system app, MediaStore observer on `DCIM/Camera` for `IMG_*.jpg` of the Xiaomi camera only, C++ (NDK) port of this code, writes a **copy** next to the original (originals are never overwritten in the first version), opt-in switch, runs after the shot so it cannot slow capture. Needs the owner's look decision first (target C* 14 vs more/less, detail strength).
* Heat: 6 full runs back to back, battery 34.0 -> 35.2 °C (charging), hottest zone 64 °C then ~56 °C, no throttling (22-26 s per photo); no test on night / ultra-wide / front photos (front has the base beauty; skin handling needs its own test).
* Owner comparison images: `~/camera_builds/stage_lab/compare/` (stand, office person, banknote crop) — decide whether the look is right before the app is built.
