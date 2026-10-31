# Owner shots, batch 1 (2026-10-31, 16:39 to 17:22)

Read-only analysis of what the owner shot in the evening with the native camera (v15 in the ROM), LMC (`POCO-F4-ONE.xml`) and PhotoStage. Files were copied from the phone to the laptop; nothing on the phone was changed or deleted. Metrics: `tools/camera_lab/measure_photos.py`, saved in `docs/camera/shots_2026-10-31/`.

## What was shot
| Kind | Count | Notes |
|---|---:|---|
| Native photos | 26 | 22 normal back, 1 back with night/low light, 2 front (3904x5184), **3 Portrait stubs** (below) |
| LMC photos | 33 | 3472x4624 back, 1952x2592 front, plus LMC Portrait files |
| Native videos | 6 | All 4K HEVC with AAC 48 kHz audio, 4 to 7 s each |
| PhotoStage copies | 26 | One per native photo, including the stubs |
Scenes were shot in pairs with both cameras (street, flowers, white SUV, pink tree, pond at sunset, alley at dusk, selfies).

## 1. Native back Portrait: crash plus a leftover stub (known limit, new detail)
Three native photos are **1440x1080, exactly 16,777,216 bytes**, zero-padded (`IMG_..164034`, `..164133`, `..164255`). All three have mode code `OpMode 36864` (0x9000), which `CAMERA_PROJECT.md` lists as back Portrait (dual bokeh), and no exposure or ISO data.
The camera app crashed four times in the same minutes (SIGABRT in thread `ParallelDataZip`, library `libwa_depth.so`, `base_exceptions::DNNError`) at 16:40:35, 16:41:32, 16:42:45 and 16:42:58. Each stub was saved within about two seconds of a crash. This is the known back-Portrait depth-engine crash (`MODE_TEST_RESULTS.md`, `FINAL_REPORT.md`), not the v8 "fast shot" bug.
* **Behaviour now:** the app dies about 2 s after the shutter, restarts, and leaves a low-resolution stub with no background blur. The 16:40:35 crash shows a different message (`bad input shape for polyadic operator: {2}, {4}`) from the other three (`layout.shape[i] ... stride`): the same engine, so no new cause is implied.
* **Not a regression:** nothing else crashed. All other 23 native photos are full size.
* **Fix still open:** use LMC Portrait (works). Candidate for the next PhotoStage update: skip files with `OpMode 36864` and exactly 16 MiB, so stubs aren't processed.

## 2. Native versus LMC
Whole-image metrics (centre 1024 crop, higher sharpness = more fine detail; scene content changes the numbers, so only compare the same scene):
| Set | Median sharpness | Median noise | Median chroma |
|---|---:|---:|---:|
| Native (23 full-size) | 58.7 | 0.62 | 7.1 |
| PhotoStage copies | 158.2 | 0.83 | 8.3 |
| LMC (33) | 230.9 | 1.95 | 10.7 |
Medians cover different scenes, so they only show a trend: LMC is sharper, noisier and more colourful than native.
* **100 % crops of the pink tree and the pond** (not pixel-aligned, so only a rough look): native foliage and flowers are smeared into blobs ("watercolour"); LMC shows individual leaves, wires and branches. In the dark treeline at sunset LMC lifts shadows and shows detail where native is a dark mass. This matches the earlier daylight finding (native about 2x softer, caused by the HAL noise reduction).
* **Not yet established:** a fair like-for-like crop. The street pair did not line up (LMC framed a different part of the scene), so I make no claim there.

## 3. PhotoStage (gentler colour build)
Per pair (23 full-size photos): sharpness median **x2.70**, noise **x1.37**, chroma **+1.1** (about 7.1 to 8.3), brightness change median 0.0.
* Colour: the gentle setting does what it should; nothing is oversaturated in the crops.
* Detail: edges get crisper, but the smeared texture stays and some areas show a painted, slightly crunchy look. It adds contrast, not real detail, as before.
* The three flat-sky shots rise only x1.27 (nothing to sharpen), which is fine.
* **Owner verdict still needed** (`OWNER_HELP_NEEDED.md` #7): better, same or too strong.

## 4. Videos
| Clip | Resolution | Frame rate | Bitrate | Length | Dropped frames | Audio |
|---|---|---:|---:|---:|---|---|
| 164004 | 3840x2160 | 59.4 | 100 Mbps | 6.3 s | one 50 ms gap in 376 frames | -20 dB mean, peak -0.3 dB |
| 164020 | 3840x2160 | 30 | 60 Mbps | 5.7 s | none | -20 dB, peak -0.1 dB |
| 164348 | 3840x2160 | 30 | 61 Mbps | 6.8 s | none | -19 dB |
| 164715 | 3840x2160 | 30 | 60 Mbps | 3.9 s | none | -14 dB |
| 170023 | 3840x2160 | 30 | 60 Mbps | 5.7 s | none | -23 dB, peak -8 dB |
| 172053 | 3840x2160 | 30 | 60 Mbps | 4.9 s | one 43 ms gap | -12 dB, peak 0.0 dB |
* All six were **kept**: the v15 safety net for the earlier deleted-clips bug held.
* Frame timing is steady at 30 fps and 60 fps. Stabilisation and OIS can't be judged from numbers (owner row 6).
* Audio is present in all; two clips touch 0 dB, so loud sounds clip. Not checked by ear.
* Clips are short (4 to 7 s). The earlier long-clip bug (clips of about 10 min) is still untested in this batch.

## 5. Left on the phone
Eight tombstone files in `/data/tombstones` from the four Portrait crashes, 209 lines in the crash buffer. They are kept until the end of the camera week so any new crash can be compared, then cleared (owner preference: no leftovers).

## Next for this batch
1. Owner: judge PhotoStage pairs, and say if Portrait was tried on purpose.
2. Aligned crops for the pairs that match (pink tree, SUV, pond) if a fair statement on softness is needed.
3. More shots over the week, especially daylight, a long 4K clip, and handheld walking video for stabilisation.
