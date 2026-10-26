# Vendor restore plan: official HyperOS 1 camera, audio and misc files

Date: 2026-10-23. This step only prepared files: no image was built and nothing was flashed. The staged files are in `secure_build/staging_vendor_official/{camera,audio,misc}/`, and the manifest is `MANIFEST.tsv` (columns: group, relpath, sha256, mode, uid, gid, selinux).

What was compared:
- **Official:** HyperOS 1 V816.0.9.0.ULMMIXM vendor (`h1v`).
- **Ours:** current vendor (`ourv`).
- **Also checked:** MIUI 14 vendor (`m14`) and the original port vendor (`opv`).

## 1. Camera stack (47 files to restore)

- Camera-related files compared: 406 official, 408 ours. 49 differ:
  - **46 porter replacements.** Each is identical to the original port vendor and matches **neither official HyperOS 1 nor MIUI 14**, so they come from an unknown or other build.
  - **1 our edit:** `etc/camera/camxoverridesettings.txt`.
  - **2 porter-only files:** `lib{,64}/camera/com.qti.sensormodule.munch_ofilm_imx582_wide.bin`. These stay; they're unused on this phone, which has the OV64B40 main sensor.
- **Restored by this plan:**
  - the camera HAL `lib{,64}/hw/camera.qcom.so`;
  - the 3A libraries: `com.qtistatic.stats.{aec,af,awb,pdlib}` and `com.qti.stats.{aec,af,awb}wrapper` (lib and lib64);
  - the EIS nodes `com.qti.node.eisv2/eisv3` (lib and lib64);
  - `com.vidhance.stats.aec_dmbr`;
  - the Xiaomi nodes `AIIE`, `aiasd`, `mimovie`, `rearvideo`, `watermark` and `misegment`, plus `com.facepp.node.siq`;
  - the tuning files `com.qti.tuned.{default, munch_sunny_ov64b40_wide, munch_aac_ov8856_ultra, munch_sunny_ov8856_ultra, munch_sunny_gc02m1_macro, munch_ofilm_gc02m1_macro, munch_sunny_imx596_front, munch_ofilm_imx582_wide}.bin` (lib and lib64);
  - `com.qti.sensormodule.munch_sunny_ov8856_ultra.bin` (lib and lib64);
  - and `camxoverridesettings.txt`.
- **Porter tuning swap:** in the porter's set, `com.qti.tuned.default.bin` is the same file as the porter's `imx582` tuning (1f04…). Official `default` matches official OV64B40 tuning (1574c378…), so the porter's tuning mismatches this phone's OV64B40 main sensor.
- **camxoverridesettings.txt (optional):** the staged file is the official one. Ours removes the debug lines (`enable3ADebugData`, `enableTuningMetadata`, `offlineLoggerEnableBackupLog`, all FALSE anyway) and adds `HighQualityQuickShotSupportMask=0x000000`. Use the official file with the official 5.1 app, unless the quick-shot mask is wanted.

## 2. Audio (4 files)

`lib{,64}/hw/audio.primary.kona.so` and `lib{,64}/hw/sound_trigger.primary.kona.so`. All four are the porter's versions; official is `e4b29429` (64-bit audio) and `b609af26` (64-bit sound trigger).

## 3. Misc (6 files)

- **Fingerprint driver:** `lib{,64}/libgf_hal.so`, Goodix; official is `820bdfc0` for 64-bit.
- **`etc/permissions/android.hardware.fingerprint.xml`:** **our vendor hides the fingerprint feature.** The file is `<permissions/>` with the comment "hidden until the sensor flex cable is repaired", left over from the earlier secure build. The staged official file declares `android.hardware.fingerprint` again.
  - Check on the phone first: `pm has-feature android.hardware.fingerprint`. adb was unavailable during this audit because the phone was rebooting.
  - If it returns false, the "weak fingerprint" may really be a framework or feature mismatch.
- **Thermal profiles:** `etc/thermal-hp-mgame.conf` and `etc/thermal-hp-normal.conf` are missing in ours and present in official.
- **`etc/permissions/com.google.android.feature.PREMIER_TIER.xml`:** missing in ours, present in official.

## 4. Dependency and interface checks

| Group | ELF files | Unresolved DT_NEEDED | Linked vendor libs that differ from official | Ready |
|---|---|---|---|---|
| camera | 28 | 0 | none | **yes** |
| audio | 4 | 0 | none | **yes** |
| misc | 2 | 0 | none | **yes** |

- Libraries are resolved against vendor `lib*`, `hw`, `camera`, `components` and `egl`, the VNDK v30 apex (`system_ext/apex/com.android.vndk.v30.apex`, 287 libraries per ABI), and LLNDK names.
- **No staged official ELF needs a library that the porter's version did not already need.**
- **Interfaces:**
  - These are byte-identical to official: `bin/hw/android.hardware.camera.provider@2.4-service_64`, `android.hardware.audio.service`, `android.hardware.biometrics.fingerprint@2.1-service`, and their `.rc` files.
  - The only difference in `etc/vintf/manifest.xml` is one extra `vendor.qti.sla.service@1.0` entry, which is unrelated.
  - `init.qcom.rc` has no camera, audio or fingerprint differences.
- **So the camera, audio and fingerprint interfaces stay the same.**
- **SELinux labels** come from the official files: `vendor_file`, and `vendor_configs_file` for the `etc/` files. They're the same contexts our image uses for those paths.

## 5. Risks and recommended order

1. **camera:** apply together with the official MiuiCamera 5.1 already flashed. It turns the whole camera stack back into the official, consistent set.
   - Expected effect: fixes the purple night photos and magenta cast, and fixes portrait mode, because the depth and AI nodes are the official versions now.
   - Risk: low to medium. Only the porter's HyperOS 4 camera app relied on the porter's set, and it has been replaced.
   - Check after applying: all four cameras open, and night, portrait and video work.
2. **misc:** the thermal profiles and the premier XML are low risk.
   - For fingerprint, apply `libgf_hal.so` and the official feature file together, then re-enrol your fingerprint.
   - If the flex cable really is still damaged, keep our hidden XML. The user reports fingerprint works, but weakly.
3. **audio:** medium risk. It fixes the ultrasound speaker failures, but the porter may have patched it for something.
   - Check after applying: speaker, earpiece calls, Bluetooth audio, proximity during calls.
   - If anything regresses, roll back by reflashing the current vendor.

All three groups can go into one vendor rebuild, with vendor UUID `-Ue0addc37-d7ae-453a-aa9d-c65f5856dc4d`. Keep the current `out_global/vendor.img` as the rollback image.
