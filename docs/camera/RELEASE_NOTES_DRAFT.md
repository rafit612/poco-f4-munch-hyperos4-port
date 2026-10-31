# Release notes — camera v15, PhotoStage, Google Phone/Contacts (2026-10-31)

Status: **camera v15 + PhotoStage flashed 2026-10-31, tag T20261031b in the fingerprint** (`ROM_HISTORY.md` §12). Not published yet. (Older text: a tag means a new `ro.build.fingerprint` tag in `product/etc/build.prop`, which needs a product rebuild (~14 GB free, flash with owner approval). Plan: tag **together with** the next build (PhotoStage app, camera v14 if the daylight A/B says so), not for these notes alone.

## What is new
* **Native camera 6.7 (v15)** on the Marble profile: watermark "POCO F4 5G", Leica looks, Short video saves, VLOG works, 4K60 at 100 Mbit/s, 20 MP selfies, ultra-wide photos save, 2x/5x zoom photos are real crops. Table with builds: `FINAL_REPORT.md` §1.
* **Google Phone and Google Contacts are the default** (system apps, MIUI Call removed, no chooser).
* **Finished videos are no longer deleted** when the app misreads their length (v15).
* **PhotoStage app** (in the ROM, switch in the app): copies of native-camera photos with denoise/detail/tone/colour in Pictures/PhotoStage; originals untouched; see `08_PHOTO_STAGE.md`.

PhotoStage colour was made gentler after flashing: it is on the owner's phone as an app update and goes into the next image.

## Known issues (use LMC for these)
Night mode purple cast; back Portrait crashes; Mimoji, Clone and Movie effects modes are hidden (they crash on this phone); Photo mode never switches to night by itself; native photos are much softer than LMC (HAL noise reduction). Details: `OWNER_TESTS_2026-10-30.md`, `FINAL_REPORT.md` §3.
Network: Wi-Fi drops every ~85 s were traced to the router/channel, not the phone (`docs/system/PHONE_CHECKS_2026-10-30.md`).

## Install / rollback
Flash: `secure_build/flash_product_nowipe.sh` (no data erase). Rollback: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261031_v14 "rollback"`. Camera only: `pm uninstall-system-updates com.android.camera`.

## Before publishing
Owner: real call on both SIMs, look decision, daylight shots. Privacy: no IMEI/serial/PIN/personal photos in the package; APKs are not stored in git.
