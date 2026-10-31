# Display, GPU and touch (Phase 1, 2026-10-31)

Read-only. One passive reading on the phone (launcher in focus, charging, about 9 hours since boot). No taps, no tests.

## Stack
```
Apps                  HWUI (OpenGL), Xiaomi blur and glass effects
Framework             SurfaceFlinger (HyperOS 4), DisplayManager, input (fts_ts)
HALs                  composer 3.0 (Qualcomm) + allocator 4.0, display.color 1.5, displayfeature 1.0, touchfeature 1.0, lights
Kernel                msm_drm / SDE, DSI panel driver, KGSL (Adreno 650), Focaltech touch over SPI
Hardware              6.67 in OLED 1080x2400, panel mdss_dsi_l11r_38_08_0a_dsc_cmd (replacement, 60 Hz)
```

## Display
| Item | Value |
|---|---|
| Panel node | `l11r_38_08_0a_dsc_cmd`, command mode, DSC; same name in the device tree of every kernel compared |
| Modes the kernel lists | 60, 90 and 120 Hz |
| Modes Android sees | **60 Hz only**, render range 0 to 60 Hz |
| Hardware vsync | 59.62 Hz (16.77 ms period) against the nominal 60.00 Hz |
| Backlight | `panel0-backlight`, 0 to 2047 steps; DC-style dimming flag on (`debug.secret_dc_backlight.enable`) |
| Colour | sRGB mode (`native_mode` 258), wide colour gamut, HDR10, HDR10+ and HLG reported supported |
| Density | 440 (the Xiaomi 17 uses 520 for its own panel) |
| Services | `displayfeature`, `display-color`, `fps_hal` all running; `panel-info-sh` and `qti_display_boot` are one-shot and stopped |

* **The 90 and 120 Hz modes listed by the kernel stay unused.** The replacement panel is 60 Hz hardware, so this is expected. Don't unlock them.
* The 0.6 % gap between 59.62 and 60.00 Hz is a normal clock offset; SurfaceFlinger follows the hardware period.
* `oled_pmic_id` returns empty and `wp_info` shows `0d000000000`. Both are optional panel readouts; nothing visible depends on them as far as checked.

## GPU
Adreno 650: 305 to 670 MHz (seven steps), governor `msm-adreno-tz`, 14 % busy at the reading, thermal level 0. The 670 MHz maximum is the SD870 value. Nothing to change.

## Rendering and smoothness
* **HWUI uses OpenGL.** `ro.hwui.use_vulkan` is empty and no app has loaded Vulkan, though `ro.hardware.vulkan=adreno` exists. Skia on Vulkan is a measured Phase 2 test through the non-persistent `debug.hwui.renderer` property, so a reboot undoes it. Risk: the Android 11 vendor Vulkan driver may not meet what Android 17 HWUI needs.
* **SystemUI frames since its start:** 117,586 frames, 3.14 % janky (modern count), median 10 ms, 90th percentile 18 ms, 95th 25 ms, 99th 65 ms. At 60 Hz the budget is 16.7 ms, so the 90th percentile sits just over it. This is the baseline for any rendering change. The launcher and Photos returned no data, so they are not yet measured.
* `HWC missed frame count` is 63,889 since boot. It has no baseline yet, so it says nothing until compared after a change.
* Frame timing is set by `debug.sf.*phase_offset` values and `persist.sf.force_setaffinity.bigcore`. Same family as official; not touched.

## SELinux denials seen in the display path
| Denial | Meaning |
|---|---|
| `surfaceflinger` cannot read `vendor_frc_prop` | HyperOS 4 SurfaceFlinger wants a frame-rate-control property that the vendor side defines. Harmless at 60 Hz |
| `surfaceflinger` cannot find service `vendor.perfservice` | SurfaceFlinger tries to ask the Xiaomi performance service for boosts and is refused. Only 2 seen in the short log window. A narrow rule could be tested in Phase 2, with a before and after frame-time comparison |

## Touch
| Item | Value |
|---|---|
| Controller | Focaltech family, input name `fts_ts`, on SPI (`990000.spi`, `spi1.0`) |
| Input | 10 slots; coordinates 0 to 10799 by 0 to 23999 (screen size times 10, `resolution_factor` 10) |
| Extras | Double-tap and letter gestures (W, E, U, O, S, L, Z, C, V, M, arrows) for wake; palm sensor flag off |
| Services | `touchfeature` HAL running; `xiaomi-touch` input node present; game mode off |
| Fingerprint | `uinput-goodix` node exists but the sensor flex is dead (hardware) |

Kernel side: `fts_ts_probe` and 127 `fts_` functions run in the porter's kernel, and `liyafe` builds `CONFIG_TOUCHSCREEN_FOCALTECH_3658U` for munch, the same as LineageOS. The driver family matches, but the input name `fts_ts` isn't proven for that driver, so at the first RAM boot check that `fts_ts` appears and touch works.

## Compared with the Xiaomi 17 HyperOS 4 reference
The display properties are almost identical. The reference has only three extra items: `ro.display.enable_pwm_switch` (PWM dimming switch for its panel), `ro.display.move_frame_rate_strategy_up` (a refresh-rate rule that only matters above 60 Hz) and `persist.sys.miui.damon.enable` (unknown, not display-specific). Density differs because the panel does. **So HyperOS 4 isn't missing display configuration here.** What it expects is kernel side: `liyafe`'s MIUI display driver provides the `disp_param`, `disp_pcc`, `doze_brightness` and `panel_info` nodes that the display services read.

## Candidates, in order (Phase 2, measured)
| # | Change | Gain | Risk |
|---|---|---|---|
| 1 | Skia Vulkan test with `debug.hwui.renderer=skiavk`, reboot undoes it | Possibly lower CPU use and fewer slow frames | Medium: crashes if the driver is too old |
| 2 | Allow `surfaceflinger` to find `vendor.perfservice` | Frame boosts from the Xiaomi service | Low to medium: compare frame times |
| 3 | Frame baseline for launcher and 3 apps with `gfxinfo` before and after each change | Needed for the two above | None |

## Not worth doing
* Unlocking 90 or 120 Hz: hardware is 60 Hz.
* Colour tuning: the panel is a replacement, so factory calibration doesn't apply. Judge by eye if wanted, not by number.

## Next
Wi-Fi and modem, then audio.
