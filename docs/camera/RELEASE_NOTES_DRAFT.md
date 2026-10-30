# Release notes (DRAFT) — camera v13 + Google Phone/Contacts, 2026-10-30

Status: flashed on the owner's phone (product partition, no wipe). Not tagged and not published: a tag means a new `ro.build.fingerprint` tag in `product/etc/build.prop`, which needs a product rebuild (~14 GB free, flash with owner approval). Plan: tag **together with** the next build (PhotoStage app, camera v14 if the daylight A/B says so), not for these notes alone.

## What is new
* **Native camera 6.7 (v13)** on the Marble profile: watermark "POCO F4 5G", Leica looks, Short video saves, VLOG works, 4K60 at 100 Mbit/s, 20 MP selfies, ultra-wide photos save, 2x/5x zoom photos are real crops. Table with builds: `FINAL_REPORT.md` §1.
* **Google Phone and Google Contacts are the default** (system apps, MIUI Call removed, no chooser).
* **PhotoStage app** (optional, next build): copies of native-camera photos with denoise/detail/tone/colour in Pictures/PhotoStage; originals untouched; see `08_PHOTO_STAGE.md`.

## Known issues (use LMC for these)
Night mode purple cast; back Portrait crashes; a movie-effects AI mode (SNPE) crashes; one mode screen crashes with a null protocol (layout class); Photo mode never switches to night by itself; native photos are much softer than LMC (HAL noise reduction). Details: `OWNER_TESTS_2026-10-30.md`, `FINAL_REPORT.md` §3.
Network: Wi-Fi drops every ~85 s were traced to the router/channel, not the phone (`docs/system/PHONE_CHECKS_2026-10-30.md`).

## Install / rollback
Flash: `secure_build/flash_product_nowipe.sh` (no data erase). Rollback: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261026_prev "rollback"`. Camera only: `pm uninstall-system-updates com.android.camera`.

## Before publishing
Owner: real call on both SIMs, look decision, daylight shots. Privacy: no IMEI/serial/PIN/personal photos in the package; APKs are not stored in git.
