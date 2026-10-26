# sound trigger fix (vendor/etc/sound_trigger_platform_info.xml)

- Original: `platform_lpi_enable="true"`. Google hotword (7038ddc8-...) LPI usecase uses one handset mic with no LPI calibration
  (ACDB -19); loading it crash-loops the ADSP (sound card offline every ~0.8 s, all audio dropped).
- Attempt 1 (2026-10-25, failed): remove only Google's LPI lsm_usecase -> ADSP stable, but when the HAL switches to LPI
  it finds no usecase (`ape_reg_sm: couldn't get lsm usecase`, err -22), retries, and the audio HAL aborts every ~8 s.
- Fix: original file with only `platform_lpi_enable="false"`. Registration with lpi_enable=false was seen working.
- Attempt 2 (failed): platform_lpi_enable=false -> no HAL crash, but the Google model still crash-loops the ADSP in
  non-LPI mode (232 card offline events in 60 s; GSA had pushed a new model).
- Fix: original file with both Google engine sections (7038ddc8-..., 9f6ad62a-..., suffix 40a8f03d3f15) removed.
  The HAL rejects Google's DSP model; Hey Google falls back to software detection. Qualcomm/Xiaomi engines unchanged.
- Attempt 3 (failed, no boot): removing android.hardware.soundtrigger from vendor/etc/vintf/manifest.xml - the QTI audio
  HAL service treats the sound trigger registration as mandatory and exits; boot never completes. Reverted.
- Root cause (2026-10-25): port kernel 4.19.325-zyndong has the audio drivers built in (q6lsm/msm_lsm in kallsyms);
  official HyperOS 1 uses kernel 4.19.157 with the vendor modules. Vendor = official V816.0.9.0.ULMMIXM.
- Final: Google engine sections removed (vendor) + system/etc/init/audioserver.rc no longer stops the audio HAL on
  sys.audio.restart.hal (Android 17 sound trigger middleware sets it after any HAL error).
