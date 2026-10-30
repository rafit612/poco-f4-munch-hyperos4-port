# P9 — Bake the final camera into the ROM (plan, 2026-10-29; CORRECTED 2026-10-30)

> **Correction 2026-10-30:** the shipped ROM is the *tele* build (`payload_tele` + `build_tele.sh`); `payload_g64` is the shelved pure-64-bit build (it did not
> boot). Camera v13 + Google Dialer/Contacts were built from `payload_tele` and **flashed (no wipe) on 2026-10-30**; see `ROM_HISTORY.md` §11. The steps
> below that mention `payload_g64`, `build_g64.sh` and the 9.6 GB estimate are obsolete. Still open: owner call test, post-flash heat/regression, release tag + notes.

## Done
1. **ROM payload camera = v13** (sha 3a76a1e3; v11 c8eb90f4 until 2026-10-30): `secure_build/payload_g64/product/priv-app/MiuiCamera/MiuiCamera.apk`
   (meta unchanged: `0 0 644 u:object_r:system_file:s0`). The old payload build (2026-10-24, sha fbeda85d, no camera
   fixes) is backed up on the pendrive: `camera_project/camera_builds/MiuiCamera_payload_g64_old_2026-10-24.apk`.

## Update 2026-10-30 night
* Done: camera v13 and Google Dialer/Contacts built and flashed (see header). PhotoStage release APK (sha 92b1abc4, signed with a project key kept outside the repo, not debuggable) is staged in `secure_build/payload_tele/product/app/PhotoStage/` for the **next** product build; the APK itself is git-ignored (like the other APKs), only its `.meta` is committed. It is installed on the phone as a normal app today and works there; as a ROM app it is untested until a rebuild.
* Space for the next product build: ~14 GB free needed (laptop had 17 GB after cleanup); rollback image `out_tele_T20261026_prev` must stay.
* Heat measured for the stage (6 runs, +1.2 °C); LMC regression could not be run (LMC not installed on the phone right now).
* One more product build + flash is only worth it together with camera v14 and/or other fixes; do not build for the app alone unless the owner asks.

## Still to do (in this order)
2. **Wait for the outdoor tests** ("night", "window"/HDR, Panorama) — a fix from them goes into the camera first, then the
   payload APK is replaced again with the final build.
3. **Space:** `build_g64.sh PARTS="product"` reads the Xiaomi 17 base (`stock_rom_global17`, 9.8 GB, extracted on the
   laptop), writes a product tar in `$W/g64tmp` and the image in `secure_build/out_g64`. The laptop has ~4 GB free -> move
   the extracted stock ROM folders to the pendrive first (owner decision; their zips are already on the pendrive) or run
   with `W`/`O` on the pendrive (slow but works).
   *Status 2026-10-30:* stock_rom_1.0.9 + stock_rom_miui14 moved to the pendrive (`extracted_stock_roms/`, verified),
   laptop now ~9 GB free. Measured need: product content 5.64 GB uncompressed (tar) + new image ~3.8 GB = **~9.6 GB peak**,
   so it still does not fit; the pendrive has 2.6 GB left. Needs ~1-2 GB more on the laptop (owner decision: e.g. move
   `~/kernel_build` (8.6 GB, kernel work stopped) to another disk, or clear part of `~/Downloads`).
4. **Build** only the product image (`PARTS="product"`), run the EROFS symlink check (`tools/erofs_symlink_check.py`, must
   print 0), sha256 the image.
5. **Flash — owner approval required** (partition write). Before flashing: disable/remove the `munch_cam_watermark`
   KernelSU module (it bind-mounts the same APK path; with the baked v11 it is no longer needed), keep `cam_cl_test` and
   `cam_l4_test` disabled or removed. Rollback = previous product image (keep it on the pendrive) + re-enable the module.
6. **Regression run** after flashing: mode sweep (`tools/camera_lab/mode_sweep.py`), back + front photo, 4K60/1080p video,
   LMC photo/video/Portrait, heat (see P0 heat tests), no new crashes in the crash buffer, SELinux enforcing.
7. **Release + report:** update ROM release notes (camera v11 changes: watermark, Leica filters, Short video, VLOG, bitrate,
   placeholder trim, front 20 MP fix, ultra-wide photos fixed in v12, zoom photos fixed in v13), final camera report with before/after sheets.

## Notes
* The app caches picture sizes in `shared_prefs/munch_GLOBAL_llnu_7_camera_cache.xml`; a clean install has no cache, so the
  v11 front size is computed correctly. On the owner's phone the stale key was already removed.
* Camera builds keep being produced by `tools/re/camera_watermark_patch.sh` from `apk_certs/com.android.camera.apk`.
