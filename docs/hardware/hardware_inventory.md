# POCO F4 5G (munch) — hardware inventory

Generated 2026-10-27 from the live phone (`/sys/bus/*/devices`, `/sys/firmware/devicetree`) and the port kernel source (`rohmanurip/kernel_munch`, Linux 4.19.325-zyndong-perf). 1152 devices.

Columns: **bus** = Linux bus, **driver** = bound kernel driver (live), **compatible** = device-tree id, **source** = driver file in the kernel tree, **Kconfig** = build symbol and its state in the running kernel (`y` built-in, `m` module).

## Summary

| Category | Devices |
|---|---|
| Audio (codec, amps, ADSP audio) | 165 |
| Battery / charger / fuel gauge / PMIC power | 40 |
| CPU / cpufreq / idle / PMU / coresight | 149 |
| Camera (CAM-SS, sensors, ISP) | 51 |
| Clocks / pins / GPIO / interconnect / bus voting | 224 |
| Display / panel / backlight | 16 |
| GPU (Adreno KGSL) | 8 |
| Leds / vibrator / misc board parts | 1 |
| Memory / IOMMU / DMA / cache | 58 |
| Modem / IPA / telephony links | 64 |
| NFC / IR / near-field | 2 |
| Other / unclassified | 89 |
| Platform core / timers / irq / watchdog / reset | 11 |
| Regulators / PMIC | 106 |
| Remote processors / DSP / glink / SMEM / PIL | 97 |
| Security / crypto / TrustZone | 7 |
| Sensors (IIO / SLPI) | 9 |
| Storage (UFS / eMMC / SD) | 19 |
| Thermal / cooling / sensors of temperature | 5 |
| Touch / input / keys / haptics | 14 |
| USB / Type-C / DisplayPort | 10 |
| Wi-Fi / Bluetooth / connectivity | 7 |

## Audio (codec, amps, ADSP audio)

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| gpio | `gpiochip5` |  | qcom | techpack/audio/soc/pinctrl-lpi.c:878 |  |
| i2c | `1-0034` | tfa98xx | nxp | techpack/audio/asoc/codecs/tfa9874/src/tfa98xx.c:4438 |  |
| i2c | `1-0035` | tfa98xx | nxp | techpack/audio/asoc/codecs/tfa9874/src/tfa98xx.c:4438 |  |
| mhi | `0306_02.01.00_AUDIO_VOICE_0` | voice_mhi_audio |  |  |  |
| platform | `39f000c.qcom,avtimer` | dev_avtimer | qcom | techpack/audio/dsp/avtimer.c:598 |  |
| platform | `bolero-clk-rsc-mngr` | bolero-clk-rsc-mngr | qcom | techpack/audio/asoc/codecs/bolero/bolero-clk-rsc.c:734 |  |
| platform | `rx-macro` | rx_macro | qcom | techpack/audio/asoc/codecs/bolero/rx-macro.c:4215 |  |
| platform | `rx_swr_ctrl` | swr-wcd | qcom | techpack/audio/soc/swr-mstr-ctrl.c:3839 |  |
| platform | `soc:audio_etm0` |  | qcom | drivers/hwtracing/coresight/coresight-remote-etm.c:310 | CONFIG_CORESIGHT_REMOTE_ETM=y |
| platform | `soc:msm_cdc_pinctrl@159` | msm-cdc-pinctrl | qcom | techpack/audio/asoc/codecs/msm-cdc-pinctrl.c:368 |  |
| platform | `soc:msm_cdc_pinctrl@32` | msm-cdc-pinctrl | qcom | techpack/audio/asoc/codecs/msm-cdc-pinctrl.c:368 |  |
| platform | `soc:qcom,msm-adsp-loader` | adsp-loader | qcom | techpack/audio/dsp/adsp-loader.c:469 |  |
| platform | `soc:qcom,msm-audio-apr` | audio_apr | qcom | techpack/audio/ipc/apr.c:1235 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,msm-audio-ion` | msm-audio-ion | qcom | techpack/audio/dsp/msm_audio_ion.c:707 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio` | q6core_audio | qcom | techpack/audio/dsp/q6core.c:2118 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:bolero-cdc` | bolero-codec | qcom | techpack/audio/asoc/codecs/bolero/bolero-cdc.c:1516 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:cdc_dmic01_pinctrl` | msm-cdc-pinctrl | qcom | techpack/audio/asoc/codecs/msm-cdc-pinctrl.c:368 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:cdc_dmic23_pinctrl` | msm-cdc-pinctrl | qcom | techpack/audio/asoc/codecs/msm-cdc-pinctrl.c:368 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:lpi_pinctrl@33c0000` | qcom-lpi-pinctrl | qcom | techpack/audio/soc/pinctrl-lpi.c:878 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:rx_swr_clk_data_pinctrl` | msm-cdc-pinctrl | qcom | techpack/audio/asoc/codecs/msm-cdc-pinctrl.c:368 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:sound` | kona-asoc-snd | qcom | techpack/audio/asoc/kona.c:8355 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:tx_swr_clk_data_pinctrl` | msm-cdc-pinctrl | qcom | techpack/audio/asoc/codecs/msm-cdc-pinctrl.c:368 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:vote_lpass_audio_hw` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,q6core-audio:vote_lpass_core_hw` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:qcom,msm-audio-apr:qcom,voice-mhi-audio` | voice_mhi_audio | qcom | techpack/audio/dsp/voice_mhi.c:584 |  |
| platform | `soc:qcom,msm-compress-dsp` | msm-compress-dsp | qcom | techpack/audio/asoc/msm-compress-q6-v2.c:5582 |  |
| platform | `soc:qcom,msm-dai-cdc-dma` | msm-dai-cdc-dma | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13210 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-0-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-1-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-2-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-3-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-4-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-5-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-6-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-rx-cdc-dma-7-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-tx-cdc-dma-0-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-tx-cdc-dma-1-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-tx-cdc-dma-2-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-tx-cdc-dma-3-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-tx-cdc-dma-4-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-tx-cdc-dma-5-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-va-cdc-dma-0-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-va-cdc-dma-1-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-va-cdc-dma-2-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-wsa-cdc-dma-0-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-wsa-cdc-dma-0-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-wsa-cdc-dma-1-rx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-wsa-cdc-dma-1-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-cdc-dma:qcom,msm-dai-wsa-cdc-dma-2-tx` | msm-dai-cdc-dma-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:13172 |  |
| platform | `soc:qcom,msm-dai-fe` | msm-dai-fe | qcom | techpack/audio/asoc/msm-dai-fe.c:2958 |  |
| platform | `soc:qcom,msm-dai-mi2s` | msm-dai-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7591 |  |
| platform | `soc:qcom,msm-dai-mi2s:qcom,msm-dai-q6-mi2s-prim` | msm-dai-q6-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7609 |  |
| platform | `soc:qcom,msm-dai-mi2s:qcom,msm-dai-q6-mi2s-quat` | msm-dai-q6-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7609 |  |
| platform | `soc:qcom,msm-dai-mi2s:qcom,msm-dai-q6-mi2s-quin` | msm-dai-q6-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7609 |  |
| platform | `soc:qcom,msm-dai-mi2s:qcom,msm-dai-q6-mi2s-sec` | msm-dai-q6-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7609 |  |
| platform | `soc:qcom,msm-dai-mi2s:qcom,msm-dai-q6-mi2s-senary` | msm-dai-q6-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7609 |  |
| platform | `soc:qcom,msm-dai-mi2s:qcom,msm-dai-q6-mi2s-tert` | msm-dai-q6-mi2s | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7609 |  |
| platform | `soc:qcom,msm-dai-q6` | msm-dai-q6 | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7556 |  |
| platform | `soc:qcom,msm-dai-q6-afe-loopback-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6-dp` | msm-dai-q6-hdmi | qcom | techpack/audio/asoc/msm-dai-q6-hdmi-v2.c:692 |  |
| platform | `soc:qcom,msm-dai-q6-dp1` | msm-dai-q6-hdmi | qcom | techpack/audio/asoc/msm-dai-q6-hdmi-v2.c:692 |  |
| platform | `soc:qcom,msm-dai-q6-hdmi` | msm-dai-q6-hdmi | qcom | techpack/audio/asoc/msm-dai-q6-hdmi-v2.c:692 |  |
| platform | `soc:qcom,msm-dai-q6-spdif-pri-rx` | msm-dai-q6-spdif | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7698 |  |
| platform | `soc:qcom,msm-dai-q6-spdif-pri-tx` | msm-dai-q6-spdif | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7698 |  |
| platform | `soc:qcom,msm-dai-q6-spdif-sec-rx` | msm-dai-q6-spdif | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7698 |  |
| platform | `soc:qcom,msm-dai-q6-spdif-sec-tx` | msm-dai-q6-spdif | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7698 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-afe-proxy-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-afe-proxy-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-be-afe-pcm-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-be-afe-pcm-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-bt-sco-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-bt-sco-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-incall-music-2-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-incall-music-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-incall-record-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-incall-record-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-int-fm-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-int-fm-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-proxy-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-proxy-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-0-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-0-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-1-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-1-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-2-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-2-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-3-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-3-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-4-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-4-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-5-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-5-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-6-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-7-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-7-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-8-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-sb-8-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-usb-audio-rx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-q6:qcom,msm-dai-q6-usb-audio-tx` | msm-dai-q6-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7516 |  |
| platform | `soc:qcom,msm-dai-tdm-pri-rx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-pri-rx:qcom,msm-dai-q6-tdm-pri-rx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-pri-tx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-pri-tx:qcom,msm-dai-q6-tdm-pri-tx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-quat-rx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-quat-rx:qcom,msm-dai-q6-tdm-quat-rx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-quat-tx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-quat-tx:qcom,msm-dai-q6-tdm-quat-tx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-quin-rx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-quin-rx:qcom,msm-dai-q6-tdm-quin-rx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-quin-tx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-quin-tx:qcom,msm-dai-q6-tdm-quin-tx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-sec-rx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-sec-rx:qcom,msm-dai-q6-tdm-sec-rx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-sec-tx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-sec-tx:qcom,msm-dai-q6-tdm-sec-tx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-sen-rx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-sen-rx:qcom,msm-dai-q6-tdm-sen-rx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-sen-tx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-sen-tx:qcom,msm-dai-q6-tdm-sen-tx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-tert-rx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-tert-rx:qcom,msm-dai-q6-tdm-tert-rx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-tert-rx:qcom,msm-dai-q6-tdm-tert-rx-1` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-tert-tx` | msm-dai-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:7929 |  |
| platform | `soc:qcom,msm-dai-tdm-tert-tx:qcom,msm-dai-q6-tdm-tert-tx-0` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-dai-tdm-tert-tx:qcom,msm-dai-q6-tdm-tert-tx-1` | msm-dai-q6-tdm | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:12255 |  |
| platform | `soc:qcom,msm-ext-disp:qcom,msm-ext-disp-audio-codec-rx` | msm-ext-disp-audio-codec-rx | qcom | techpack/audio/asoc/codecs/msm_hdmi_codec_rx.c:891 |  |
| platform | `soc:qcom,msm-lsm-client` | msm-lsm-client | qcom | techpack/audio/asoc/msm-lsm-client.c:3844 |  |
| platform | `soc:qcom,msm-pcm` | msm-pcm-dsp | qcom | techpack/audio/asoc/msm-pcm-q6-v2.c:2959 |  |
| platform | `soc:qcom,msm-pcm-afe` | msm-pcm-afe | qcom | techpack/audio/asoc/msm-pcm-afe-v2.c:889 |  |
| platform | `soc:qcom,msm-pcm-dsp-noirq` | msm-pcm-dsp-noirq | qcom | techpack/audio/asoc/msm-pcm-q6-noirq.c:1446 |  |
| platform | `soc:qcom,msm-pcm-dtmf` | msm-pcm-dtmf | qcom | techpack/audio/asoc/msm-pcm-dtmf-v2.c:564 |  |
| platform | `soc:qcom,msm-pcm-hostless` | msm-pcm-hostless | qcom | techpack/audio/asoc/msm-pcm-hostless.c:50 |  |
| platform | `soc:qcom,msm-pcm-loopback` | msm-pcm-loopback | qcom | techpack/audio/asoc/msm-pcm-loopback-v2.c:1544 |  |
| platform | `soc:qcom,msm-pcm-loopback-low-latency` | msm-pcm-loopback | qcom | techpack/audio/asoc/msm-pcm-loopback-v2.c:1544 |  |
| platform | `soc:qcom,msm-pcm-low-latency` | msm-pcm-dsp | qcom | techpack/audio/asoc/msm-pcm-q6-v2.c:2959 |  |
| platform | `soc:qcom,msm-pcm-routing` | msm-pcm-routing | qcom | techpack/audio/asoc/msm-pcm-routing-v2.c:31788 |  |
| platform | `soc:qcom,msm-pcm-voice` | msm-pcm-voice | qcom | techpack/audio/asoc/msm-pcm-voice-v2.c:821 |  |
| platform | `soc:qcom,msm-pri-auxpcm` | msm-auxpcm-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:4763 |  |
| platform | `soc:qcom,msm-quat-auxpcm` | msm-auxpcm-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:4763 |  |
| platform | `soc:qcom,msm-quin-auxpcm` | msm-auxpcm-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:4763 |  |
| platform | `soc:qcom,msm-sec-auxpcm` | msm-auxpcm-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:4763 |  |
| platform | `soc:qcom,msm-sen-auxpcm` | msm-auxpcm-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:4763 |  |
| platform | `soc:qcom,msm-stub-codec` | msm-stub-codec | qcom | techpack/audio/asoc/codecs/msm_stub.c:57 |  |
| platform | `soc:qcom,msm-tert-auxpcm` | msm-auxpcm-dev | qcom | techpack/audio/asoc/msm-dai-q6-v2.c:4763 |  |
| platform | `soc:qcom,msm-transcode-loopback` | msm-transcode-loopback | qcom | techpack/audio/asoc/msm-transcode-loopback-q6-v2.c:1751 |  |
| platform | `soc:qcom,msm-ultra-low-latency` | msm-pcm-dsp | qcom | techpack/audio/asoc/msm-pcm-q6-v2.c:2959 |  |
| platform | `soc:qcom,msm-voip-dsp` | msm-voip-dsp | qcom | techpack/audio/asoc/msm-pcm-voip-v2.c:1692 |  |
| platform | `soc:rx_core_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:rx_npl_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:tx_core_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:tx_npl_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:usb_audio_qmi_dev` | uaudio-qmi | qcom | sound/usb/usb_audio_qmi_svc.c:1343 | CONFIG_SND_USB_AUDIO_QMI=y |
| platform | `soc:va_core_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:va_npl_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:wsa_core_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `soc:wsa_npl_clk` | audio-ref-clk | qcom | techpack/audio/asoc/codecs/audio-ext-clk.c:314 |  |
| platform | `tx-macro` | tx_macro | qcom | techpack/audio/asoc/codecs/bolero/tx-macro.c:3378 |  |
| platform | `tx_swr_ctrl` | swr-wcd | qcom | techpack/audio/soc/swr-mstr-ctrl.c:3839 |  |
| platform | `va-macro` | va_macro | qcom | techpack/audio/asoc/codecs/bolero/va-macro.c:3220 |  |
| platform | `wcd938x-codec` | wcd938x_codec | qcom |  |  |
| rpmsg | `qcom,glink:adsp.apr_audio_svc.-1.-1` | apr_tal_rpmsg |  |  |  |
| soundwire | `swr1` |  | qcom | techpack/audio/soc/swr-mstr-ctrl.c:3839 |  |
| soundwire | `swr2` |  | qcom | techpack/audio/soc/swr-mstr-ctrl.c:3839 |  |
| soundwire | `wcd938x-slave.d01170223` | wcd938x-slave | qcom | techpack/audio/asoc/codecs/wcd938x/wcd938x-slave.c:328 |  |
| soundwire | `wcd938x-slave.d01170224` | wcd938x-slave | qcom | techpack/audio/asoc/codecs/wcd938x/wcd938x-slave.c:328 |  |

## Battery / charger / fuel gauge / PMIC power

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| i2c | `2-0051` | ln8000_charger | lionsemi | drivers/power/supply/ti/ln8000_charger_munch.c:1623 |  |
| i2c | `2-0066` |  | ti | drivers/power/supply/ti/bq2597x_charger.c:2378 | CONFIG_BQ2597X_CHARGE_PUMP= |
| i2c | `3-0018` | i2c_pmic | qcom | drivers/mfd/qcom-i2c-pmic.c:792 | CONFIG_MFD_I2C_PMIC=y |
| i2c | `3-0051` | ln8000_charger | lionsemi | drivers/power/supply/ti/ln8000_charger_munch.c:1619 |  |
| i2c | `3-0066` |  | ti | drivers/power/supply/ti/bq2597x_charger.c:2373 | CONFIG_BQ2597X_CHARGE_PUMP= |
| i2c | `4-0008` | i2c_pmic | qcom | drivers/mfd/qcom-i2c-pmic.c:792 | CONFIG_MFD_I2C_PMIC=y |
| i2c | `4-0009` | i2c_pmic | qcom | drivers/mfd/qcom-i2c-pmic.c:792 | CONFIG_MFD_I2C_PMIC=y |
| i2c | `4-0055` | bq_fg | ti | drivers/power/supply/qcom/bq27z561_fg_munch.c:3072 | CONFIG_FUEL_GAUGE_BQ27Z561_MUNCH=y |
| platform | `6b0f000.qcom,spmi-debug` |  | qcom | drivers/spmi/spmi-pmic-arb-debug.c:345 | CONFIG_SPMI_MSM_PMIC_ARB_DEBUG=y |
| platform | `884000.i2c:qcom,smb1390_slave@18:qcom,charge_pump_slave` |  | qcom | drivers/power/supply/qcom/smb1390-charger-psy.c:1862 | CONFIG_SMB1390_CHARGE_PUMP_PSY= |
| platform | `888000.i2c:qcom,pm8008@8:qcom,revid@100` | qcom,qpnp-revid | qcom |  |  |
| platform | `c264000.restart` | msm-restart | qcom | drivers/power/reset/msm-poweroff.c:692 | CONFIG_POWER_RESET_MSM= |
| platform | `c440000.qcom,spmi` | spmi_pmic_arb | qcom | drivers/spmi/spmi-pmic-arb.c:1360 | CONFIG_SPMI_MSM_PMIC_ARB=y |
| platform | `c440000.qcom,spmi:qcom,pm8009@a:qcom,revid@100` |  | qcom |  |  |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:clock-controller@5b00` | qcom,spmi-pmic-clkdiv | qcom | drivers/clk/qcom/clk-spmi-pmic-div.c:295 | CONFIG_SPMI_PMIC_CLKDIV=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:bcl@1d00` | bcl_pmic5 | qcom | drivers/thermal/qcom/bcl_pmic5.c:670 | CONFIG_QTI_BCL_PMIC5=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:clock-controller@6000` | qcom,spmi-pmic-clkdiv | qcom | drivers/clk/qcom/clk-spmi-pmic-div.c:295 | CONFIG_SPMI_PMIC_CLKDIV=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,pbs@7200` | qcom,qpnp-pbs | qcom |  |  |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,qpnp-smb5` | qcom,qpnp-smb5 | qcom | drivers/power/supply/qcom/qpnp-smb5-munch.c:5009 | CONFIG_QPNP_SMB5_MUNCH=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,revid@100` | qcom,qpnp-revid | qcom |  |  |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,sdam-qnovo@b000` | qcom,qnovo5-driver | qcom | drivers/power/supply/qcom/qpnp-qnovo5.c:1493 | CONFIG_QPNP_QNOVO5=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,usb-pdphy@1700` | qpnp-pdphy | qcom | drivers/usb/pd/qpnp-pdphy.c:909 | CONFIG_QPNP_USB_PDPHY=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:bcl@3d00` | bcl_pmic5 | qcom | drivers/thermal/qcom/bcl_pmic5.c:670 | CONFIG_QTI_BCL_PMIC5=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:clock-controller@5b00` | qcom,spmi-pmic-clkdiv | qcom | drivers/clk/qcom/clk-spmi-pmic-div.c:295 | CONFIG_SPMI_PMIC_CLKDIV=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:qcom,revid@100` | qcom,qpnp-revid | qcom |  |  |
| platform | `c440000.qcom,spmi:qcom,pm8150l@5:qcom,amoled` | qcom,qpnp-amoled-regulator | qcom |  |  |
| platform | `c440000.qcom,spmi:qcom,pm8150l@5:qcom,leds@d300` | qcom,qpnp-flash-led-v2 | qcom | drivers/leds/leds-qpnp-flash-v2.c:3313 | CONFIG_LEDS_QPNP_FLASH_V2=y |
| platform | `soc:cp_qc30` | cp-qc30 | xiaomi | drivers/power/supply/ti/cp_qc30_munch.c:1674 | CONFIG_PD_POLICY_MANAGER_MUNCH= |
| platform | `soc:usbpd_pm` | usbpd-pm | xiaomi | drivers/power/supply/ti/pd_policy_manager_psyche.c:1986 | CONFIG_PD_POLICY_MANAGER_PSYCHE= |
| spmi | `spmi-0` |  | qcom | drivers/spmi/spmi-pmic-arb.c:1360 | CONFIG_SPMI_MSM_PMIC_ARB=y |
| spmi | `spmi0-00` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-01` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-02` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-03` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-04` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-05` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-08` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-09` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-0a` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |
| spmi | `spmi0-0b` | pmic-spmi | qcom | drivers/mfd/qcom-spmi-pmic.c:38 | CONFIG_MFD_SPMI_PMIC=y |

## CPU / cpufreq / idle / PMU / coresight

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| amba | `6002000.stm` |  | arm |  |  |
| amba | `6004000.tpda` |  | arm |  |  |
| amba | `6005000.funnel` |  | arm |  |  |
| amba | `6010000.cti` |  | arm |  |  |
| amba | `6011000.cti` |  | arm |  |  |
| amba | `6012000.cti` |  | arm |  |  |
| amba | `6013000.cti` |  | arm |  |  |
| amba | `6014000.cti` |  | arm |  |  |
| amba | `6015000.cti` |  | arm |  |  |
| amba | `6016000.cti` |  | arm |  |  |
| amba | `6017000.cti` |  | arm |  |  |
| amba | `6018000.cti` |  | arm |  |  |
| amba | `6019000.cti` |  | arm |  |  |
| amba | `601a000.cti` |  | arm |  |  |
| amba | `601b000.cti` |  | arm |  |  |
| amba | `601c000.cti` |  | arm |  |  |
| amba | `601d000.cti` |  | arm |  |  |
| amba | `601e000.cti` |  | arm |  |  |
| amba | `601f000.cti` |  | arm |  |  |
| amba | `6041000.funnel` |  | arm |  |  |
| amba | `6042000.funnel` |  | arm |  |  |
| amba | `6045000.funnel` |  | arm |  |  |
| amba | `6046000.replicator` |  | arm |  |  |
| amba | `6048000.tmc` |  | arm |  |  |
| amba | `6830000.tpdm` |  | arm |  |  |
| amba | `6831000.cti` |  | arm |  |  |
| amba | `6832000.funnel` |  | arm |  |  |
| amba | `6844000.tpdm` |  | arm |  |  |
| amba | `6845000.cti` |  | arm |  |  |
| amba | `6846000.funnel` |  | arm |  |  |
| amba | `684c000.tpdm` |  | arm |  |  |
| amba | `6850000.tpdm` |  | arm |  |  |
| amba | `6870000.tpdm` |  | arm |  |  |
| amba | `6900000.tpdm` |  | arm |  |  |
| amba | `6902000.funnel` |  | arm |  |  |
| amba | `6980000.tpdm` |  | arm |  |  |
| amba | `6982000.cti` |  | arm |  |  |
| amba | `6983000.funnel` |  | arm |  |  |
| amba | `698b000.cti` |  | arm |  |  |
| amba | `69c0000.tpdm` |  | arm |  |  |
| amba | `69c1000.tpda` |  | arm |  |  |
| amba | `69c2000.funnel` |  | arm |  |  |
| amba | `69d0000.tpdm` |  | arm |  |  |
| amba | `6ac0000.tpdm` |  | arm |  |  |
| amba | `6ac1000.tpda` |  | arm |  |  |
| amba | `6ac2000.funnel` |  | arm |  |  |
| amba | `6b00000.cti` |  | arm |  |  |
| amba | `6b01000.cti` |  | arm |  |  |
| amba | `6b02000.cti` |  | arm |  |  |
| amba | `6b03000.cti` |  | arm |  |  |
| amba | `6b04000.funnel` |  | arm |  |  |
| amba | `6b05000.tmc` |  | arm |  |  |
| amba | `6b06000.replicator` |  | arm |  |  |
| amba | `6b08000.tpda` |  | arm |  |  |
| amba | `6b09000.tpdm` |  | arm |  |  |
| amba | `6b0a000.tpdm` |  | arm |  |  |
| amba | `6b0b000.tgu` |  | arm |  |  |
| amba | `6c08000.tpdm` |  | arm |  |  |
| amba | `6c09000.cti` |  | arm |  |  |
| amba | `6c0a000.cti` |  | arm |  |  |
| amba | `6c0b000.funnel` |  | arm |  |  |
| amba | `6c28000.tpdm` |  | arm |  |  |
| amba | `6c29000.tpdm` |  | arm |  |  |
| amba | `6c2a000.cti` |  | arm |  |  |
| amba | `6c2b000.cti` |  | arm |  |  |
| amba | `6c2c000.cti` |  | arm |  |  |
| amba | `6c2d000.funnel` |  | arm |  |  |
| amba | `6c38000.cti` |  | arm |  |  |
| amba | `6c39000.funnel` |  | arm |  |  |
| amba | `6c40000.tpdm` |  | arm |  |  |
| amba | `6c41000.tpdm` |  | arm |  |  |
| amba | `6c42000.cti` |  | arm |  |  |
| amba | `6c43000.cti` |  | arm |  |  |
| amba | `6c44000.funnel` |  | arm |  |  |
| amba | `6c47000.tpdm` |  | arm |  |  |
| amba | `6c4b000.cti` |  | arm |  |  |
| amba | `6c60000.tpdm` |  | arm |  |  |
| amba | `6c61000.cti` |  | arm |  |  |
| amba | `6e01000.cti` |  | arm |  |  |
| amba | `6e02000.cti` |  | arm |  |  |
| amba | `6e03000.cti` |  | arm |  |  |
| amba | `6e04000.funnel` |  | arm |  |  |
| amba | `6e0c000.cti` |  | arm |  |  |
| amba | `6e0d000.cti` |  | arm |  |  |
| amba | `6e0e000.cti` |  | arm |  |  |
| amba | `6e10000.tpdm` |  | arm |  |  |
| amba | `6e11000.cti` |  | arm |  |  |
| amba | `6e12000.funnel` |  | arm |  |  |
| amba | `6e20000.tpdm` |  | arm |  |  |
| amba | `6e21000.cti` |  | arm |  |  |
| amba | `6e22000.funnel` |  | arm |  |  |
| amba | `7020000.cti` |  | arm |  |  |
| amba | `7040000.etm` |  | arm |  |  |
| amba | `7120000.cti` |  | arm |  |  |
| amba | `7140000.etm` |  | arm |  |  |
| amba | `7220000.cti` |  | arm |  |  |
| amba | `7240000.etm` |  | arm |  |  |
| amba | `7320000.cti` |  | arm |  |  |
| amba | `7340000.etm` |  | arm |  |  |
| amba | `7420000.cti` |  | arm |  |  |
| amba | `7440000.etm` |  | arm |  |  |
| amba | `7520000.cti` |  | arm |  |  |
| amba | `7540000.etm` |  | arm |  |  |
| amba | `7620000.cti` |  | arm |  |  |
| amba | `7640000.etm` |  | arm |  |  |
| amba | `7720000.cti` |  | arm |  |  |
| amba | `7740000.etm` |  | arm |  |  |
| amba | `7800000.funnel` |  | arm |  |  |
| amba | `7810000.funnel` |  | arm |  |  |
| amba | `7860000.tpdm` |  | arm |  |  |
| amba | `7861000.tpdm` |  | arm |  |  |
| amba | `7863000.tpda` |  | arm |  |  |
| amba | `78a0000.tpdm` |  | arm |  |  |
| amba | `78b0000.tpdm` |  | arm |  |  |
| amba | `78e0000.cti` |  | arm |  |  |
| amba | `78f0000.cti` |  | arm |  |  |
| amba | `7900000.cti` |  | arm |  |  |
| cpu | `cpu0` |  | qcom |  |  |
| cpu | `cpu1` |  | qcom |  |  |
| cpu | `cpu2` |  | qcom |  |  |
| cpu | `cpu3` |  | qcom |  |  |
| cpu | `cpu4` |  | qcom |  |  |
| cpu | `cpu5` |  | qcom |  |  |
| cpu | `cpu6` |  | qcom |  |  |
| cpu | `cpu7` |  | qcom |  |  |
| platform | `18590000.qcom,devfreq-l3:qcom,cpu0-cpu-l3-lat` | devfreq-qcom-fw | qcom | drivers/devfreq/devfreq_qcom_fw.c:353 | CONFIG_ARM_QCOM_DEVFREQ_FW=y |
| platform | `18590000.qcom,devfreq-l3:qcom,cpu4-cpu-l3-lat` | devfreq-qcom-fw | qcom | drivers/devfreq/devfreq_qcom_fw.c:353 | CONFIG_ARM_QCOM_DEVFREQ_FW=y |
| platform | `18590000.qcom,devfreq-l3:qcom,cpu7-cpu-l3-lat` | devfreq-qcom-fw | qcom | drivers/devfreq/devfreq_qcom_fw.c:353 | CONFIG_ARM_QCOM_DEVFREQ_FW=y |
| platform | `18591000.qcom,cpufreq-hw` | qcom-cpufreq-hw | qcom | drivers/cpufreq/qcom-cpufreq-hw.c:955 | CONFIG_ARM_QCOM_CPUFREQ_HW=y |
| platform | `6001000.csr` |  | qcom | drivers/hwtracing/coresight/coresight-csr.c:540 | CONFIG_CORESIGHT_CSR=y |
| platform | `6b0c000.csr` |  | qcom | drivers/hwtracing/coresight/coresight-csr.c:540 | CONFIG_CORESIGHT_CSR=y |
| platform | `cpu-pmu` | armv8-pmu | arm | arch/arm64/kernel/perf_event.c:1374 | CONFIG_HW_PERF_EVENTS=y |
| platform | `psci` |  | arm | drivers/firmware/psci.c:707 | CONFIG_ARM_PSCI_FW=y |
| platform | `soc:dsu_pmu@0` | arm_dsu_pmu | arm | drivers/perf/arm_dsu_pmu.c:763 | CONFIG_ARM_DSU_PMU= |
| platform | `soc:dummy_sink` |  | qcom | drivers/hwtracing/coresight/coresight-dummy.c:140 | CONFIG_CORESIGHT_DUMMY=y |
| platform | `soc:hwevent` |  | qcom | drivers/hwtracing/coresight/coresight-hwevent.c:324 | CONFIG_CORESIGHT_HWEVENT=y |
| platform | `soc:npu_etm0` |  | qcom | drivers/hwtracing/coresight/coresight-remote-etm.c:310 | CONFIG_CORESIGHT_REMOTE_ETM=y |
| platform | `soc:qcom,cpu0-cpugrp` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:811 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu0-cpugrp:qcom,cpu0-cpu-l3-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-cpugrp` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:811 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-cpugrp:qcom,cpu4-computemon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:813 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-cpugrp:qcom,cpu4-cpu-l3-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-cpugrp:qcom,cpu4-qoslatmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-cpugrp:qcom,cpu7-cpu-l3-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,lpm-levels` | lpm-levels | qcom | drivers/cpuidle/lpm-levels.c:817 | CONFIG_MSM_PM=y |
| platform | `soc:ssc_etm0` |  | qcom | drivers/hwtracing/coresight/coresight-remote-etm.c:310 | CONFIG_CORESIGHT_REMOTE_ETM=y |
| platform | `soc:tpdm@6b26000` |  | qcom | drivers/hwtracing/coresight/coresight-dummy.c:140 | CONFIG_CORESIGHT_DUMMY=y |
| platform | `soc:turing_etm0` |  | qcom | drivers/hwtracing/coresight/coresight-remote-etm.c:310 | CONFIG_CORESIGHT_REMOTE_ETM=y |

## Camera (CAM-SS, sensors, ISP)

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `ac00000.qcom,a5` | cam-a5 | qcom | techpack/camera/drivers/cam_icp/icp_hw/a5_hw/a5_dev.c:198 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac40000.qcom,cam-cpas` | cam-cpas | qcom | techpack/camera-cas/drivers/cam_cpas/cam_cpas_intf.c:724 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac4f000.qcom,cci` | cam-cci-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/cci/msm_cci.c:2214 | CONFIG_MSM_CCI= |
| platform | `ac4f000.qcom,cci:qcom,actuator@0` | qcom,actuator | qcom | drivers/media/platform/msm/camera_v2/sensor/actuator/msm_actuator.c:2053 | CONFIG_MSMB_CAMERA= |
| platform | `ac4f000.qcom,cci:qcom,cam-res-mgr` | cam_res_mgr | qcom | techpack/camera/drivers/cam_sensor_module/cam_res_mgr/cam_res_mgr.c:710 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac4f000.qcom,cci:qcom,cam-sensor@0` | qcom,camera | qcom | techpack/camera-cas/drivers/cam_sensor_module/cam_sensor/cam_sensor_dev.c:260 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac4f000.qcom,cci:qcom,cam-sensor@3` | qcom,camera | qcom | techpack/camera-cas/drivers/cam_sensor_module/cam_sensor/cam_sensor_dev.c:260 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac4f000.qcom,cci:qcom,eeprom0` | qcom,eeprom | qcom | drivers/media/platform/msm/camera_v2/sensor/eeprom/msm_eeprom.c:1930 | CONFIG_MSM_EEPROM= |
| platform | `ac4f000.qcom,cci:qcom,eeprom3` | qcom,eeprom | qcom | drivers/media/platform/msm/camera_v2/sensor/eeprom/msm_eeprom.c:1930 | CONFIG_MSM_EEPROM= |
| platform | `ac50000.qcom,cci` | cam-cci-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/cci/msm_cci.c:2214 | CONFIG_MSM_CCI= |
| platform | `ac50000.qcom,cci:qcom,cam-sensor@1` | qcom,camera | qcom | techpack/camera-cas/drivers/cam_sensor_module/cam_sensor/cam_sensor_dev.c:260 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac50000.qcom,cci:qcom,cam-sensor@2` | qcom,camera | qcom | techpack/camera-cas/drivers/cam_sensor_module/cam_sensor/cam_sensor_dev.c:260 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac50000.qcom,cci:qcom,eeprom1` | qcom,eeprom | qcom | drivers/media/platform/msm/camera_v2/sensor/eeprom/msm_eeprom.c:1930 | CONFIG_MSM_EEPROM= |
| platform | `ac50000.qcom,cci:qcom,eeprom2` | qcom,eeprom | qcom | drivers/media/platform/msm/camera_v2/sensor/eeprom/msm_eeprom.c:1930 | CONFIG_MSM_EEPROM= |
| platform | `ac53000.qcom,jpegenc` | cam-jpeg-enc | qcom | techpack/camera/drivers/cam_jpeg/jpeg_hw/jpeg_enc_hw/jpeg_enc_dev.c:200 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac57000.qcom,jpegdma` | cam-jpeg-dma | qcom | techpack/camera-cas/drivers/cam_jpeg/jpeg_hw/jpeg_dma_hw/jpeg_dma_dev.c:202 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac5f000.qcom,fd` | cam_fd_hw | qcom | techpack/camera/drivers/cam_fd/fd_hw_mgr/fd_hw/cam_fd_hw_dev.c:205 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac6a000.qcom,csiphy` | cam-csiphy-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/csiphy/msm_csiphy.c:2599 | CONFIG_MSM_CSIPHY= |
| platform | `ac6c000.qcom,csiphy` | cam-csiphy-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/csiphy/msm_csiphy.c:2599 | CONFIG_MSM_CSIPHY= |
| platform | `ac6e000.qcom,csiphy` | cam-csiphy-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/csiphy/msm_csiphy.c:2599 | CONFIG_MSM_CSIPHY= |
| platform | `ac70000.qcom,csiphy` | cam-csiphy-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/csiphy/msm_csiphy.c:2599 | CONFIG_MSM_CSIPHY= |
| platform | `ac72000.qcom,csiphy` | cam-csiphy-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/csiphy/msm_csiphy.c:2599 | CONFIG_MSM_CSIPHY= |
| platform | `ac74000.qcom,csiphy` | cam-csiphy-driver | qcom | drivers/media/platform/msm/camera_v2/sensor/csiphy/msm_csiphy.c:2599 | CONFIG_MSM_CSIPHY= |
| platform | `ac7a000.qcom,bps` | cam-bps | qcom | techpack/camera/drivers/cam_icp/icp_hw/bps_hw/bps_dev.c:177 | CONFIG_SPECTRA_CAMERA= |
| platform | `ac9a000.qcom,ipe0` | cam-ipe | qcom | techpack/camera/drivers/cam_icp/icp_hw/ipe_hw/ipe_dev.c:169 | CONFIG_SPECTRA_CAMERA= |
| platform | `acb4000.qcom,ife0` | cam_vfe | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe.c:36 | CONFIG_SPECTRA_CAMERA= |
| platform | `acb5200.qcom,csid0` | csid_17x | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw/cam_ife_csid17x.c:64 | CONFIG_SPECTRA_CAMERA= |
| platform | `acc3000.qcom,ife1` | cam_vfe | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe.c:36 | CONFIG_SPECTRA_CAMERA= |
| platform | `acc4200.qcom,csid1` | csid_17x | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw/cam_ife_csid17x.c:64 | CONFIG_SPECTRA_CAMERA= |
| platform | `acd9000.qcom,ife-lite0` | cam_vfe | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe.c:48 | CONFIG_SPECTRA_CAMERA= |
| platform | `acd9200.qcom,csid-lite0` | csid_lite | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw/cam_ife_csid_lite17x.c:32 | CONFIG_SPECTRA_CAMERA= |
| platform | `acdb200.qcom,ife-lite1` | cam_vfe | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe.c:48 | CONFIG_SPECTRA_CAMERA= |
| platform | `acdb400.qcom,csid-lite1` | csid_lite | qcom | techpack/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw/cam_ife_csid_lite17x.c:32 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam-cdm-intf` | msm_cam_cdm_intf | qcom | techpack/camera/drivers/cam_cdm/cam_cdm_intf.c:23 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam-fd` | cam_fd | qcom | techpack/camera-cas/drivers/cam_fd/cam_fd_dev.c:178 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam-icp` | cam_icp | qcom | techpack/camera-cas/drivers/cam_icp/cam_icp_subdev.c:48 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam-isp` | cam_isp | qcom | techpack/camera-cas/drivers/cam_isp/cam_isp_dev.c:45 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam-jpeg` | cam_jpeg | qcom | techpack/camera/drivers/cam_jpeg/cam_jpeg_dev.c:44 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam-req-mgr` | cam_req_mgr | qcom | techpack/camera-cas/drivers/cam_req_mgr/cam_req_mgr_dev.c:754 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam_smmu` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:132 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_icp_fw` | msm_cam_smmu | qcom | techpack/camera-cas/drivers/cam_smmu/cam_smmu_api.c:160 | CONFIG_SPECTRA_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_smmu_cpas_cdm` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:133 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_smmu_fd` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:133 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_smmu_icp` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:133 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_smmu_ife` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:133 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_smmu_jpeg` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:133 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,cam_smmu:msm_cam_smmu_secure` | msm_cam_smmu | qcom | drivers/media/platform/msm/camera_v2/common/cam_smmu_api.c:133 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,camera-flash@0` | CAM-FLASH-DRIVER | qcom | drivers/media/platform/msm/camera_v2/sensor/flash/msm_flash.c:34 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,camera-flash@1` | CAM-FLASH-DRIVER | qcom | drivers/media/platform/msm/camera_v2/sensor/flash/msm_flash.c:34 | CONFIG_MSMB_CAMERA= |
| platform | `soc:qcom,camera-flash@2` | CAM-FLASH-DRIVER | qcom | drivers/media/platform/msm/camera_v2/sensor/flash/msm_flash.c:34 | CONFIG_MSMB_CAMERA= |

## Clocks / pins / GPIO / interconnect / bus voting

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| gpio | `gpiochip0` |  | qcom | drivers/pinctrl/qcom/pinctrl-kona.c:1799 | CONFIG_PINCTRL_KONA=y |
| platform | `100000.qcom,gcc` | gcc-kona | qcom | drivers/clk/qcom/gcc-kona.c:4366 | CONFIG_MSM_GCC_KONA=y |
| platform | `16e0000.ad-hoc-bus` | msm_bus_device | qcom | drivers/soc/qcom/msm_bus/msm_bus_fabric_adhoc.c:1205 |  |
| platform | `17c20000.timer` |  | arm | drivers/clocksource/arm_arch_timer.c:1244 | CONFIG_ARM_ARCH_TIMER=y |
| platform | `18200000.rsc` | rpmh | qcom | drivers/soc/qcom/rpmh-rsc.c:938 |  |
| platform | `18200000.rsc:msm_bus_apps_rsc` | msm_bus_rsc | qcom | drivers/soc/qcom/msm_bus/msm_bus_fabric_rpmh.c:1974 |  |
| platform | `18200000.rsc:qcom,rpmhclk` | clk-rpmh | qcom | drivers/clk/qcom/clk-rpmh.c:436 | CONFIG_QCOM_CLK_RPMH=y |
| platform | `3d90000.qcom,gpucc` | gpu_cc-kona | qcom | drivers/clk/qcom/gpucc-kona.c:400 | CONFIG_MSM_GPUCC_KONA=y |
| platform | `9980000.qcom,npucc` | npu_cc-kona | qcom | drivers/clk/qcom/npucc-kona.c:1172 | CONFIG_MSM_NPUCC_KONA=y |
| platform | `abf0000.qcom,videocc` | video_cc-kona | qcom | drivers/clk/qcom/videocc-kona.c:585 | CONFIG_MSM_VIDEOCC_KONA=y |
| platform | `ad00000.qcom,camcc` | cam_cc-kona | qcom | drivers/clk/qcom/camcc-kona.c:2713 | CONFIG_MSM_CAMCC_KONA=y |
| platform | `af00000.qcom,dispcc` | disp_cc-kona | qcom | drivers/clk/qcom/dispcc-kona.c:1519 | CONFIG_MSM_DISPCC_KONA=y |
| platform | `af20000.rsc` | rpmh | qcom | drivers/soc/qcom/rpmh-rsc.c:938 |  |
| platform | `af20000.rsc:msm_bus_disp_rsc` | msm_bus_rsc | qcom | drivers/soc/qcom/msm_bus/msm_bus_fabric_rpmh.c:1974 |  |
| platform | `b221200.qcom,rpmh-master-stats` | msm_rpmh_master_stats | qcom | drivers/soc/qcom/rpmh_master_stat.c:263 | CONFIG_QTI_RPM_STATS_LOG=y |
| platform | `f000000.pinctrl` | kona-pinctrl | qcom | drivers/pinctrl/qcom/pinctrl-kona.c:1799 | CONFIG_PINCTRL_KONA=y |
| platform | `soc:qcom,aopclk` | qmp-aop-clk | qcom | drivers/clk/qcom/clk-aop-qmp.c:368 | CONFIG_MSM_CLK_AOP_QMP=y |
| platform | `soc:qcom,bus_proxy_client` | msm_bus_proxy_client_device | qcom | drivers/soc/qcom/msm_bus/msm_bus_proxy_client.c:41 |  |
| platform | `soc:qcom,cc-debug` |  | qcom | drivers/clk/qcom/debugcc-kona.c:1017 | CONFIG_MSM_DEBUGCC_KONA=y |
| platform | `soc:timer` |  | arm | drivers/clocksource/arm_arch_timer.c:1239 | CONFIG_ARM_ARCH_TIMER=y |

## Display / panel / backlight

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `3d00000.qcom,kgsl-3d0` | kgsl-3d | qcom | drivers/gpu/drm/msm/adreno/adreno_device.c:343 |  |
| platform | `ae00000.qcom,mdss_mdp` | msm_drm | qcom | techpack/display/msm/msm_drv.c:458 |  |
| platform | `ae00000.qcom,mdss_mdp:qcom,smmu_sde_sec_cb` | msmdrm_smmu | qcom | techpack/display/msm/msm_smmu.c:326 |  |
| platform | `ae00000.qcom,mdss_mdp:qcom,smmu_sde_unsec_cb` | msmdrm_smmu | qcom | techpack/display/msm/msm_smmu.c:324 |  |
| platform | `ae94000.qcom,mdss_dsi_ctrl0` | drm_dsi_ctrl | qcom | techpack/display/msm/dsi/dsi_ctrl.c:78 |  |
| platform | `ae94400.qcom,mdss_dsi_phy0` | dsi_phy | qcom | techpack/display/msm/dsi/dsi_phy.c:101 |  |
| platform | `ae94900.qcom,mdss_dsi_pll` | mdss_pll | qcom | techpack/display/pll/pll_drv.c:373 | CONFIG_QCOM_MDSS_PLL= |
| platform | `ae96000.qcom,mdss_dsi_ctrl1` | drm_dsi_ctrl | qcom | techpack/display/msm/dsi/dsi_ctrl.c:78 |  |
| platform | `ae96400.qcom,mdss_dsi_phy1` | dsi_phy | qcom | techpack/display/msm/dsi/dsi_phy.c:101 |  |
| platform | `ae96900.qcom,mdss_dsi_pll` | mdss_pll | qcom | techpack/display/pll/pll_drv.c:373 | CONFIG_QCOM_MDSS_PLL= |
| platform | `af20000.qcom,sde_rscc` | sde_rsc | qcom | techpack/display/msm/sde_rsc.c:1651 |  |
| platform | `af20000.rsc:sde_rsc_rpmh` | sde_rsc_rpmh | qcom | techpack/display/msm/sde_rsc.c:1668 |  |
| platform | `soc:qcom,dsi-display-primary` | msm-dsi-display | qcom | techpack/display/msm/dsi/dsi_display.c:55 |  |
| platform | `soc:qcom,dsi-display-secondary` | msm-dsi-display | qcom | techpack/display/msm/dsi/dsi_display.c:55 |  |
| platform | `soc:qcom,msm_notifier@0` | msm_notifier | qcom | techpack/display/msm/msm_notifier.c:187 |  |
| platform | `soc:qcom,wb-display@0` | sde_wb | qcom | techpack/display/msm/sde/sde_wb.c:812 |  |

## GPU (Adreno KGSL)

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `3da0000.kgsl-smmu` | arm-smmu | qcom | drivers/iommu/arm-smmu.c:5582 | CONFIG_ARM_SMMU=y |
| platform | `3da0000.qcom,kgsl-iommu` |  | qcom |  |  |
| platform | `3da0000.qcom,kgsl-iommu:gfx3d_secure` |  | qcom |  |  |
| platform | `3da0000.qcom,kgsl-iommu:gfx3d_user` |  | qcom |  |  |
| platform | `soc:kgsl_iommu_test_device` |  | iommu-debug-test | drivers/iommu/iommu-debug.c:2336 | CONFIG_IOMMU_DEBUG= |
| platform | `soc:qcom,kgsl-busmon` | kgsl-busmon | qcom | drivers/gpu/msm/adreno.c:4047 |  |
| platform | `soc:qcom,kgsl-hyp` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |

## Leds / vibrator / misc board parts

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `soc:qcom,msm_hdcp` | msm_hdcp | qcom | drivers/misc/msm_hdcp.c:241 | CONFIG_HDCP_QSEECOM=y |

## Memory / IOMMU / DMA / cache

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `15000000.apps-smmu` | arm-smmu | qcom | drivers/iommu/arm-smmu.c:5582 | CONFIG_ARM_SMMU=y |
| platform | `15185000.anoc_1_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `15189000.anoc_2_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `1518d000.mnoc_hf_0_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `15191000.mnoc_hf_1_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `15195000.compute_dsp_1_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `15199000.compute_dsp_0_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `151a1000.anoc_1_pcie_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `151a5000.mnoc_sf_0_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `151a9000.mnoc_sf_1_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `3dc5000.gfx_0_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `3dc9000.gfx_1_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `60400.qcom,npu-npu-llcc-bwmon` | bimc-bwmon | qcom | drivers/devfreq/bimc-bwmon.c:1085 | CONFIG_QCOM_BIMC_BWMON=y |
| platform | `70300.qcom,npudsp-npu-ddr-bwmon` | bimc-bwmon | qcom | drivers/devfreq/bimc-bwmon.c:1085 | CONFIG_QCOM_BIMC_BWMON=y |
| platform | `800000.qcom,gpi-dma` | gpi_dma | qcom | drivers/dma/qcom/gpi.c:3066 | CONFIG_QCOM_GPI_DMA=y |
| platform | `900000.qcom,gpi-dma` | gpi_dma | qcom | drivers/dma/qcom/gpi.c:3066 | CONFIG_QCOM_GPI_DMA=y |
| platform | `9091000.qcom,cpu-llcc-ddr-bwmon` | bimc-bwmon | qcom | drivers/devfreq/bimc-bwmon.c:1086 | CONFIG_QCOM_BIMC_BWMON=y |
| platform | `9093000.qcom,npu-llcc-ddr-bwmon` | bimc-bwmon | qcom | drivers/devfreq/bimc-bwmon.c:1086 | CONFIG_QCOM_BIMC_BWMON=y |
| platform | `9095000.llcc-pmu` | qcom-llcc-pmu | qcom | drivers/perf/qcom_llcc_pmu.c:300 | CONFIG_QCOM_LLCC_PMU=y |
| platform | `90b6400.qcom,cpu-cpu-llcc-bwmon` | bimc-bwmon | qcom | drivers/devfreq/bimc-bwmon.c:1085 | CONFIG_QCOM_BIMC_BWMON=y |
| platform | `a00000.qcom,gpi-dma` | gpi_dma | qcom | drivers/dma/qcom/gpi.c:3066 | CONFIG_QCOM_GPI_DMA=y |
| platform | `aa00000.qcom,vidc:venus_bus_ddr` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:466 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `aa00000.qcom,vidc:venus_bus_llcc` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:466 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `ab00000.qcom,cvp:cvp_bus_ddr` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:288 | CONFIG_MSM_CVP_V4L2=y |
| platform | `soc:apps_iommu_coherent_test_device` |  | iommu-debug-test | drivers/iommu/iommu-debug.c:2336 | CONFIG_IOMMU_DEBUG= |
| platform | `soc:apps_iommu_test_device` |  | iommu-debug-test | drivers/iommu/iommu-debug.c:2336 | CONFIG_IOMMU_DEBUG= |
| platform | `soc:kryo-erp` | kryo_cpu_cache_erp | arm | drivers/edac/kryo_arm64_edac.c:582 | CONFIG_EDAC_KRYO_ARM64=y |
| platform | `soc:qcom,cpu-cpu-llcc-bw` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:225 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,cpu-llcc-ddr-bw` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,cpu0-cpu-llcc-lat` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:225 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,cpu0-cpugrp:qcom,cpu0-cpu-llcc-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu0-cpugrp:qcom,cpu0-llcc-ddr-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu0-llcc-ddr-lat` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,cpu4-cpu-ddr-latfloor` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,cpu4-cpu-ddr-qoslat` | devfreq-qcom-qoslat | qcom | drivers/devfreq/devfreq_qcom_qoslat.c:137 | CONFIG_ARM_QCOM_DEVFREQ_QOSLAT=y |
| platform | `soc:qcom,cpu4-cpu-llcc-lat` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:225 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,cpu4-cpugrp:qcom,cpu4-cpu-llcc-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-cpugrp:qcom,cpu4-llcc-ddr-latmon` | arm-memlat-mon | qcom | drivers/devfreq/arm-memlat-mon.c:812 | CONFIG_ARM_MEMLAT_MON=y |
| platform | `soc:qcom,cpu4-llcc-ddr-lat` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,gpubw` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,ion` | ion-msm | qcom |  |  |
| platform | `soc:qcom,npu-llcc-ddr-bw` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,npu-npu-ddr-latfloor` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,npu-npu-llcc-bw` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:225 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,npudsp-npu-ddr-bw` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:224 | CONFIG_QCOM_DEVFREQ_DEVBW=y |

## Modem / IPA / telephony links

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| mhi | `0306_02.01.00` |  |  |  |  |
| mhi | `0306_02.01.00_ADSP_0` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_ADSP_1` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_ADSP_2` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_ADSP_3` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_BL` | MHI_BL |  |  |  |
| mhi | `0306_02.01.00_DCI` | diag_mhi_driver |  |  |  |
| mhi | `0306_02.01.00_DIAG` | diag_mhi_driver |  |  |  |
| mhi | `0306_02.01.00_DUN` | mhi_uci |  |  |  |
| mhi | `0306_02.01.00_EFS` | mhi_uci |  |  |  |
| mhi | `0306_02.01.00_IPCR` | qcom_mhi_qrtr |  |  |  |
| mhi | `0306_02.01.00_IP_CTRL` | MHI_DTR |  |  |  |
| mhi | `0306_02.01.00_IP_HW0` | mhi_netdev |  |  |  |
| mhi | `0306_02.01.00_IP_HW0_RSC` | mhi_netdev |  |  |  |
| mhi | `0306_02.01.00_IP_HW_ADPL` | ipa_mpm |  |  |  |
| mhi | `0306_02.01.00_IP_HW_MHIP_0` | ipa_mpm |  |  |  |
| mhi | `0306_02.01.00_IP_HW_MHIP_1` | ipa_mpm |  |  |  |
| mhi | `0306_02.01.00_IP_HW_QDSS` |  |  |  |  |
| mhi | `0306_02.01.00_LOOPBACK` | mhi_uci |  |  |  |
| mhi | `0306_02.01.00_QDSS` | qdss_bridge |  |  |  |
| mhi | `0306_02.01.00_QMI0` | mhi_uci |  |  |  |
| mhi | `0306_02.01.00_QMI1` | mhi_uci |  |  |  |
| mhi | `0306_02.01.00_RMNET_CTL` | rmnet_ctl |  |  |  |
| mhi | `0306_02.01.00_SAHARA` | mhi_uci |  |  |  |
| mhi | `0306_02.01.00_SLPI_0` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_SLPI_1` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_SLPI_2` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_SLPI_3` | mhi_satellite |  |  |  |
| mhi | `0306_02.01.00_TF` | mhi_uci |  |  |  |
| mhi | `1101_00.01.00` |  |  |  |  |
| mhi | `1101_00.01.00_DIAG` | diag_mhi_driver |  |  |  |
| mhi | `1101_00.01.00_IPCR` | qcom_mhi_qrtr |  |  |  |
| mhi | `1101_00.01.00_LOOPBACK` | mhi_uci |  |  |  |
| pci | `0002:01:00.0` | mhi |  |  |  |
| platform | `1e00000.qcom,ipa` | ipa | qcom | drivers/platform/msm/ipa/ipa_api.c:3150 |  |
| platform | `1e00000.qcom,ipa:ipa_smmu_11ad` | ipa | qcom | drivers/platform/msm/ipa/ipa_api.c:3154 |  |
| platform | `1e00000.qcom,ipa:ipa_smmu_ap` | ipa | qcom | drivers/platform/msm/ipa/ipa_api.c:3151 |  |
| platform | `1e00000.qcom,ipa:ipa_smmu_uc` | ipa | qcom | drivers/platform/msm/ipa/ipa_api.c:3153 |  |
| platform | `soc:md_testing_mode` | md-testing-mode | modem |  |  |
| platform | `soc:qcom,ipa-mpm` | ipa_mpm | qcom | drivers/platform/msm/ipa/ipa_v3/ipa_mpm.c:3277 | CONFIG_IPA3_MHI_PRIME_MANAGER=y |
| platform | `soc:qcom,ipa_fws` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `soc:qcom,ipa_uc` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `soc:qcom,rmnet-ipa` | rmnet_ipa3 | qcom | drivers/platform/msm/ipa/ipa_v3/rmnet_ipa.c:2694 | CONFIG_RMNET_IPA3=y |
| platform | `soc:qmi-tmd-devices` | qmi-cooling-device | qcom | drivers/thermal/qcom/qmi_cooling.c:646 | CONFIG_QTI_QMI_COOLING_DEVICE=y |
| rpmsg | `qcom,glink:adsp.mhi_sat.-1.-1` | mhi,sat_rpmsg |  |  |  |
| rpmsg | `qcom,glink:dsps.mhi_sat.-1.-1` | mhi,sat_rpmsg |  |  |  |

## NFC / IR / near-field

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| i2c | `0-0028` | nq-nci | qcom | drivers/nfc/nq-nci.c:45 | CONFIG_NFC_NQ=y |
| spi | `spi0.0` | ir-spi | ir-spi |  |  |

## Other / unclassified

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| esoc | `esoc0` | mdm-4x |  |  |  |
| i2c | `i2c-0` |  | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| i2c | `i2c-1` |  | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| i2c | `i2c-2` |  | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| i2c | `i2c-3` |  | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| i2c | `i2c-4` |  | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| nvmem | `qfprom0` |  | qcom | drivers/nvmem/qfprom.c:71 |  |
| pci | `0000:00:00.0` | pci-msm-rc |  |  |  |
| pci | `0002:00:00.0` | pci-msm-rc |  |  |  |
| platform | `146bf000.qcom,msm-imem` |  | qcom |  |  |
| platform | `17a10040.qcom,pcie0_msi` |  | qcom |  |  |
| platform | `17a10040.qcom,pcie2_msi` |  | qcom |  |  |
| platform | `182a0000.syscon` |  | syscon |  |  |
| platform | `18590000.qcom,devfreq-l3` | devfreq-qcom-fw | qcom | drivers/devfreq/devfreq_qcom_fw.c:352 | CONFIG_ARM_QCOM_DEVFREQ_FW=y |
| platform | `1880000.syscon` |  | syscon |  |  |
| platform | `1c00000.qcom,pcie` | pci-msm | qcom | drivers/pci/controller/pci-msm.c:6040 | CONFIG_PCI_MSM=y |
| platform | `1c10000.qcom,pcie` | pci-msm | qcom | drivers/pci/controller/pci-msm.c:6040 | CONFIG_PCI_MSM=y |
| platform | `1f40000.syscon` |  | syscon |  |  |
| platform | `3ac0000.slim` | ngd_msm_ctrl | qcom | drivers/slimbus/slim-msm-ngd.c:1779 | CONFIG_SLIMBUS_MSM_NGD=y |
| platform | `3d6a000.qcom,gmu` |  | qcom |  |  |
| platform | `3d6a000.qcom,gmu:gmu_kernel` |  | qcom |  |  |
| platform | `3d6a000.qcom,gmu:gmu_user` |  | qcom |  |  |
| platform | `3d91008.syscon` |  | syscon |  |  |
| platform | `3d91508.syscon` |  | syscon |  |  |
| platform | `3d91540.syscon` |  | syscon |  |  |
| platform | `780000.qfprom` | qcom,qfprom | qcom | drivers/nvmem/qfprom.c:71 |  |
| platform | `793000.qrng` | msm_rng | qcom | drivers/char/hw_random/msm_rng.c:448 | CONFIG_HW_RANDOM_MSM_LEGACY=y |
| platform | `884000.i2c` | i2c_geni | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| platform | `888000.i2c` | i2c_geni | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| platform | `88a7000.msm_tspp` |  | qcom | drivers/media/platform/msm/broadcast/tspp.c:3242 | CONFIG_TSPP= |
| platform | `88ea000.qcom,mdss_dp_pll` | mdss_pll | qcom |  |  |
| platform | `8c0000.qcom,qupv3_2_geni_se` | qupv3_geni_se | qcom | drivers/platform/msm/qcom-geni-se.c:1628 | CONFIG_QCOM_GENI_SE=y |
| platform | `90ba000.syscon` |  | syscon |  |  |
| platform | `984000.i2c` | i2c_geni | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| platform | `988000.spi` | spi_geni | qcom | drivers/spi/spi-geni-qcom.c:1910 | CONFIG_SPI_QCOM_GENI=y |
| platform | `98c000.i2c` | i2c_geni | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| platform | `990000.spi` | spi_geni | qcom | drivers/spi/spi-geni-qcom.c:1910 | CONFIG_SPI_QCOM_GENI=y |
| platform | `9900000.qcom,msm_npu` | msm_npu | qcom | drivers/media/platform/msm/npu/npu_dev.c:184 | CONFIG_MSM_NPU=y |
| platform | `998000.qcom,qup_uart` | msm_geni_serial | qcom | drivers/tty/serial/msm_geni_serial_elish.c:3130 | CONFIG_SERIAL_MSM_GENI_ELISH= |
| platform | `9c0000.qcom,qupv3_0_geni_se` | qupv3_geni_se | qcom | drivers/platform/msm/qcom-geni-se.c:1628 | CONFIG_QCOM_GENI_SE=y |
| platform | `a8c000.i2c` | i2c_geni | qcom | drivers/i2c/busses/i2c-qcom-geni.c:1248 | CONFIG_I2C_QCOM_GENI=y |
| platform | `a90000.qcom,qup_uart` |  | qcom | drivers/tty/serial/msm_geni_serial_elish.c:3127 | CONFIG_SERIAL_MSM_GENI_ELISH= |
| platform | `aa00000.qcom,vidc` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:464 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `aa00000.qcom,vidc:bus_cnoc` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:466 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `aa00000.qcom,vidc:non_secure_cb` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:465 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `aa00000.qcom,vidc:secure_bitstream_cb` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:465 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `aa00000.qcom,vidc:secure_non_pixel_cb` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:465 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `aa00000.qcom,vidc:secure_pixel_cb` | msm_vidc_v4l2 | qcom | drivers/media/platform/msm/vidc_3x/msm_v4l2_vidc.c:465 | CONFIG_MSM_VIDC_3X_V4L2= |
| platform | `ab00000.qcom,cvp` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:286 | CONFIG_MSM_CVP_V4L2=y |
| platform | `ab00000.qcom,cvp:cvp_cnoc` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:288 | CONFIG_MSM_CVP_V4L2=y |
| platform | `ab00000.qcom,cvp:cvp_non_secure_cb` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:287 | CONFIG_MSM_CVP_V4L2=y |
| platform | `ab00000.qcom,cvp:cvp_secure_nonpixel_cb` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:287 | CONFIG_MSM_CVP_V4L2=y |
| platform | `ab00000.qcom,cvp:cvp_secure_pixel_cb` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:287 | CONFIG_MSM_CVP_V4L2=y |
| platform | `ac0000.qcom,qupv3_1_geni_se` | qupv3_geni_se | qcom | drivers/platform/msm/qcom-geni-se.c:1628 | CONFIG_QCOM_GENI_SE=y |
| platform | `ac4d000.qcom,cpas-cdm0` | msm_cam_cdm | qcom |  |  |
| platform | `c221000.qcom,mpm2-sleep-counter` |  | qcom |  |  |
| platform | `cam_sync` | cam_sync |  |  |  |
| platform | `firmware:android` |  | android |  |  |
| platform | `ramoops.0` | ramoops |  |  |  |
| platform | `reg-dummy` | reg-dummy |  |  |  |
| platform | `snd-soc-dummy` | snd-soc-dummy |  |  |  |
| platform | `soc` |  | simple-bus | drivers/bus/ti-sysc.c:1701 | CONFIG_TI_SYSC= |
| platform | `soc:demux` |  | qcom | drivers/media/platform/msm/dvb/demux/mpq_dmx_plugin_sw.c:272 |  |
| platform | `soc:hwlock` | qcom_hwspinlock | qcom | drivers/hwspinlock/qcom_hwspinlock.c:69 | CONFIG_HWSPINLOCK_QCOM=y |
| platform | `soc:ipcc-self-ping-apss` |  | qcom |  |  |
| platform | `soc:ipcc-self-ping-npu` |  | qcom |  |  |
| platform | `soc:qcom,mdm0` | ext-mdm | qcom | drivers/esoc/esoc-mdm-4x.c:1248 | CONFIG_ESOC_MDM_4x=y |
| platform | `soc:qcom,msm-compr-dsp` |  | qcom |  |  |
| platform | `soc:qcom,msm-ext-disp` | msm-ext-disp | qcom | drivers/platform/msm/msm_ext_display.c:663 | CONFIG_MSM_EXT_DISPLAY=y |
| platform | `soc:qcom,msm-hdmi-dba-codec-rx` |  | qcom |  |  |
| platform | `soc:qcom,msm-rtb` |  | qcom |  |  |
| platform | `soc:qcom,msm_gsi` | gsi | qcom | drivers/platform/msm/gsi/gsi.c:47 | CONFIG_GSI=y |
| platform | `soc:qcom,smp2p_interrupt_qvrexternal_5_out` |  | qcom |  |  |
| platform | `soc:qcom,smp2p_interrupt_rdbg_2_in` |  | qcom | drivers/char/rdbg.c:1090 | CONFIG_MSM_RDBG=m |
| platform | `soc:qcom,smp2p_interrupt_rdbg_2_out` |  | qcom | drivers/char/rdbg.c:1089 | CONFIG_MSM_RDBG=m |
| platform | `soc:qcom,smp2p_interrupt_rdbg_5_in` |  | qcom | drivers/char/rdbg.c:1092 | CONFIG_MSM_RDBG=m |
| platform | `soc:qcom,smp2p_interrupt_rdbg_5_out` |  | qcom | drivers/char/rdbg.c:1091 | CONFIG_MSM_RDBG=m |
| platform | `soc:qcom,snoc_cnoc_keepalive` | devbw | qcom | drivers/devfreq/devfreq_devbw.c:225 | CONFIG_QCOM_DEVFREQ_DEVBW=y |
| platform | `soc:qcom,sps` | msm_sps | qcom | drivers/platform/msm/sps/sps.c:2820 |  |
| platform | `soc:qcom,wil6210` |  | qcom | drivers/platform/msm/msm_11ad/msm_11ad.c:1331 |  |
| platform | `us_prox.0` | us_prox |  |  |  |
| platform | `vendor` |  | simple-bus | drivers/bus/ti-sysc.c:1701 | CONFIG_TI_SYSC= |
| slimbus | `sb-1` |  |  |  |  |

## Platform core / timers / irq / watchdog / reset

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `188501c.mailbox` | qcom_apcs_ipc | qcom | drivers/mailbox/qcom-apcs-ipc-mailbox.c:138 | CONFIG_QCOM_APCS_IPC=y |
| platform | `alarmtimer.0.auto` | alarmtimer |  |  |  |
| platform | `c300000.qcom,qmp-aop` | qmp_mbox | qcom | drivers/mailbox/msm_qmp.c:783 | CONFIG_MSM_QMP=y |

## Regulators / PMIC

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| gpio | `gpiochip1` |  | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| gpio | `gpiochip2` |  | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| gpio | `gpiochip3` |  | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| gpio | `gpiochip4` |  | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| nvmem | `spmi_sdam` |  | qcom | drivers/nvmem/qcom-spmi-sdam.c:171 | CONFIG_NVMEM_SPMI_SDAM=y |
| platform | `0.gpio-regulator` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `1.gpio-regulator` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `106004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `10f004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `110004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `16b004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `175004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `177004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `17d050.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `17d054.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `17d058.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `17d06c.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `18200000.rsc:rpmh-regulator-bobc1` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-cxlvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ebilvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-gfxlvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-lcxlvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa10` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa12` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa13` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa14` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa15` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa16` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa17` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa18` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa2` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa3` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa5` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa6` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa7` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoa9` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc1` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc10` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc11` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc2` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc3` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc4` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc5` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc6` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc7` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc8` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldoc9` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof1` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof2` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof3` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof4` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof5` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof6` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-ldof7` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-lmxlvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-mmcxlvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-mxlvl` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1840 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpa4` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpa5` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpa6` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpc7` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpc8` | qcom,rpmh-regulator | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpf1` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18200000.rsc:rpmh-regulator-smpf2` |  | qcom | drivers/regulator/rpmh-regulator.c:1836 | CONFIG_REGULATOR_QCOM_RPMH=y |
| platform | `18d004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `3d9100c.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `3d9106c.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `888000.i2c:qcom,pm8008@8:pinctrl@c000` | qcom-spmi-gpio | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| platform | `888000.i2c:qcom,pm8008@8:qcom,pm8008-chip@900` | qcom,pm8008-chip | qcom | drivers/regulator/qcom_pm8008-regulator.c:1097 | CONFIG_REGULATOR_PM8008=y |
| platform | `888000.i2c:qcom,pm8008@9:qcom,pm8008-regulator` | qcom,pm8008-regulator | qcom | drivers/regulator/qcom_pm8008-regulator.c:854 | CONFIG_REGULATOR_PM8008=y |
| platform | `88e7000.refgen-regulator` | qcom,refgen-regulator | qcom | drivers/regulator/refgen.c:131 | CONFIG_REGULATOR_REFGEN=y |
| platform | `9981004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `abf0bf8.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `abf0c98.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `abf0d18.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `abf0d98.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `ad07004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `ad08004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `ad09004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `ad0a004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `ad0b004.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `ad0c144.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `af03000.qcom,gdsc` | gdsc | qcom | drivers/clk/qcom/gdsc-regulator.c:998 |  |
| platform | `c440000.qcom,spmi:qcom,pm8009@a:pinctrl@c000` |  | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:adc_tm@3500` | qcom,adc-tm | qcom | drivers/thermal/qcom/adc-tm.c:195 | CONFIG_QTI_ADC_TM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:pinctrl@c000` | qcom-spmi-gpio | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:qcom,pm8150_rtc` | rtc-pm8xxx | qcom | drivers/rtc/rtc-pm8xxx.c:479 | CONFIG_RTC_DRV_PM8XXX=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:qcom,temp-alarm@2400` | spmi-temp-alarm | qcom | drivers/thermal/qcom-spmi-temp-alarm.c:372 | CONFIG_QCOM_SPMI_TEMP_ALARM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:sdam@b100` | qcom,spmi-sdam | qcom | drivers/nvmem/qcom-spmi-sdam.c:171 | CONFIG_NVMEM_SPMI_SDAM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:adc_tm@3500` | qcom,adc-tm | qcom | drivers/thermal/qcom/adc-tm.c:195 | CONFIG_QTI_ADC_TM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:pinctrl@c000` | qcom-spmi-gpio | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,temp-alarm@2400` | spmi-temp-alarm | qcom | drivers/thermal/qcom-spmi-temp-alarm.c:372 | CONFIG_QCOM_SPMI_TEMP_ALARM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@3:qcom,leds@d000` | qcom,tri-led | qcom | drivers/leds/leds-qti-tri-led.c:627 | CONFIG_LEDS_QTI_TRI_LED=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@3:qcom,pwms@b100` | qcom,pwm-lpg | qcom | drivers/pwm/pwm-qti-lpg.c:1719 | CONFIG_PWM_QTI_LPG=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:adc_tm@3500` | qcom,adc-tm | qcom | drivers/thermal/qcom/adc-tm.c:195 | CONFIG_QTI_ADC_TM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:pinctrl@c000` | qcom-spmi-gpio | qcom | drivers/pinctrl/qcom/pinctrl-spmi-gpio.c:1203 | CONFIG_PINCTRL_QCOM_SPMI_PMIC=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:qcom,temp-alarm@2400` | spmi-temp-alarm | qcom | drivers/thermal/qcom-spmi-temp-alarm.c:372 | CONFIG_QCOM_SPMI_TEMP_ALARM=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@5:qcom,leds@d000` | qcom,tri-led | qcom | drivers/leds/leds-qti-tri-led.c:627 | CONFIG_LEDS_QTI_TRI_LED=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@5:qcom,pwms@b100` | qcom,pwm-lpg | qcom | drivers/pwm/pwm-qti-lpg.c:1719 | CONFIG_PWM_QTI_LPG=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@5:qcom,pwms@bc00` | qcom,pwm-lpg | qcom | drivers/pwm/pwm-qti-lpg.c:1719 | CONFIG_PWM_QTI_LPG=y |
| platform | `soc:display_gpio_regulator_vci` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `soc:oled-dvdd-gpio-regulator` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `soc:regulator-dbb1` |  | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `soc:touch_vddio_vreg` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `soc:vdd_boost_vreg` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |

## Remote processors / DSP / glink / SMEM / PIL

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `1023000.dcc_v2` | msm-dcc | qcom | drivers/soc/qcom/dcc_v2.c:1923 | CONFIG_QCOM_DCC_V2=y |
| platform | `1519d000.adsp_tbu` | qsmmuv500-tbu | qcom | drivers/iommu/arm-smmu.c:7149 | CONFIG_ARM_SMMU=y |
| platform | `17300000.qcom,lpass` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `17c10000.qcom,wdt` | msm_watchdog | qcom | drivers/soc/qcom/watchdog_v2.c:933 | CONFIG_QCOM_WATCHDOG_V2=y |
| platform | `18200000.rsc:system_pm` | system_pm | qcom | drivers/soc/qcom/system_pm.c:84 | CONFIG_QTI_SYSTEM_PM=y |
| platform | `18590000.qcom,devfreq-l3:qcom,cdsp-cdsp-l3-lat` | devfreq-qcom-fw | qcom | drivers/devfreq/devfreq_qcom_fw.c:353 | CONFIG_ARM_QCOM_DEVFREQ_FW=y |
| platform | `188101c.qcom,spss` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `408000.qcom,ipcc` | qcom_ipcc | qcom | drivers/soc/qcom/qcom_ipcc.c:447 | CONFIG_QCOM_IPCC=y |
| platform | `5c00000.qcom,ssc` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `7040000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7140000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7240000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7340000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7440000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7540000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7640000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `7740000.jtagmm` |  | qcom | drivers/soc/qcom/jtagv8-etm.c:1721 | CONFIG_MSM_JTAGV8= |
| platform | `80860000.reserved-memory` | cmd-db | qcom | drivers/soc/qcom/cmd-db.c:424 | CONFIG_QCOM_COMMAND_DB=y |
| platform | `8300000.qcom,turing` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `87900000.smcinvoke` | smcinvoke | qcom | drivers/soc/qcom/smcinvoke.c:2011 | CONFIG_QCOM_SMCINVOKE=y |
| platform | `88e0000.qcom,msm-eud` | msm-eud | qcom | drivers/soc/qcom/eud.c:679 | CONFIG_QCOM_EUD=y |
| platform | `9200000.cache-controller` | kona-llcc | qcom | drivers/soc/qcom/llcc-kona.c:79 | CONFIG_QCOM_KONA_LLCC=y |
| platform | `9800000.qcom,npu` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `aab0000.qcom,venus` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `ab00000.qcom,cvp:qcom,msm-cvp,mem_cdsp` | msm_cvp_v4l2 | qcom | drivers/media/platform/msm/cvp/msm_v4l2_cvp.c:289 | CONFIG_MSM_CVP_V4L2=y |
| platform | `abb0000.qcom,cvpss` | subsys-pil-tz | qcom | drivers/soc/qcom/subsys-pil-tz.c:1301 | CONFIG_MSM_PIL_SSR_GENERIC=y |
| platform | `c300000.qcom,ddr-stats` | ddr_stats | qcom | drivers/soc/qcom/ddr_stats.c:251 | CONFIG_QTI_DDR_STATS_LOG=y |
| platform | `c300000.qcom,rpm-stats` | msm_rpm_stat | qcom | drivers/soc/qcom/rpm_stats.c:297 | CONFIG_QTI_RPM_STATS_LOG=y |
| platform | `mem-offline` |  | qcom | drivers/soc/qcom/mem-offline.c:662 | CONFIG_QCOM_MEM_OFFLINE= |
| platform | `soc:aop-msg-client` |  | qcom | drivers/soc/qcom/qmp-debugfs-client.c:101 | CONFIG_QMP_DEBUGFS_CLIENT= |
| platform | `soc:ipcc-self-ping-adsp` |  | qcom |  |  |
| platform | `soc:ipcc-self-ping-cdsp` |  | qcom |  |  |
| platform | `soc:ipcc-self-ping-slpi` |  | qcom |  |  |
| platform | `soc:mem_dump` | msm_mem_dump | qcom | drivers/soc/qcom/memory_dump_v2.c:936 | CONFIG_QCOM_MEMORY_DUMP_V2=y |
| platform | `soc:qcom,chd_gold` |  | qcom | drivers/soc/qcom/core_hang_detect.c:232 | CONFIG_MSM_CORE_HANG_DETECT= |
| platform | `soc:qcom,chd_silver` |  | qcom | drivers/soc/qcom/core_hang_detect.c:232 | CONFIG_MSM_CORE_HANG_DETECT= |
| platform | `soc:qcom,glink` | msm_glink | qcom | drivers/soc/qcom/glink_probe.c:441 | CONFIG_QCOM_GLINK=y |
| platform | `soc:qcom,glink:cdsp:qcom,msm_cdsprm_rpmsg:qcom,cdsp-cdsp-l3-gov` | cdsp-l3 | qcom | drivers/devfreq/governor_cdsp_l3.c:142 | CONFIG_DEVFREQ_GOV_CDSPL3=y |
| platform | `soc:qcom,glink:cdsp:qcom,msm_cdsprm_rpmsg:qcom,msm_cdsp_rm` | msm_cdsp_rm | qcom | drivers/soc/qcom/cdsprm.c:1126 | CONFIG_QCOM_CDSP_RM=y |
| platform | `soc:qcom,glink:cdsp:qcom,msm_cdsprm_rpmsg:qcom,msm_hvx_rm` | msm_hvx_rm | qcom | drivers/soc/qcom/cdsprm.c:1139 | CONFIG_QCOM_CDSP_RM=y |
| platform | `soc:qcom,msm-adsprpc-mem` | fastrpc | qcom | drivers/char/adsprpc.c:4953 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm-cdsp-loader` | cdsp-loader | qcom | drivers/soc/qcom/qdsp6v2/cdsp-loader.c:241 | CONFIG_MSM_CDSP_LOADER=y |
| platform | `soc:qcom,msm_fastrpc` | fastrpc | qcom | drivers/char/adsprpc.c:4949 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb1` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb10` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb11` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb12` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb13` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb14` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb15` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb2` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb3` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb4` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb5` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb6` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb7` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb8` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,msm_fastrpc:qcom,msm_fastrpc_compute_cb9` | fastrpc | qcom | drivers/char/adsprpc.c:4950 | CONFIG_MSM_ADSPRPC=y |
| platform | `soc:qcom,qsee_irq` | qsee_irq | qcom | drivers/soc/qcom/qsee_ipc_irq.c:335 | CONFIG_QSEE_IPC_IRQ=y |
| platform | `soc:qcom,qsee_irq_bridge` | qsee_ipc_irq_bridge | qcom | drivers/soc/qcom/qsee_ipc_irq_bridge.c:544 | CONFIG_QSEE_IPC_IRQ_BRIDGE=y |
| platform | `soc:qcom,smem` | qcom-smem | qcom | drivers/soc/qcom/smem.c:1223 | CONFIG_QCOM_SMEM=y |
| platform | `soc:qcom,smp2p-adsp` | qcom_smp2p | qcom | drivers/soc/qcom/smp2p.c:708 | CONFIG_QCOM_SMP2P=y |
| platform | `soc:qcom,smp2p-cdsp` | qcom_smp2p | qcom | drivers/soc/qcom/smp2p.c:708 | CONFIG_QCOM_SMP2P=y |
| platform | `soc:qcom,smp2p-dsps` | qcom_smp2p | qcom | drivers/soc/qcom/smp2p.c:708 | CONFIG_QCOM_SMP2P=y |
| platform | `soc:qcom,smp2p-npu` | qcom_smp2p | qcom | drivers/soc/qcom/smp2p.c:708 | CONFIG_QCOM_SMP2P=y |
| platform | `soc:qcom,smp2p_sleepstate` | smp2p_sleepstate | qcom | drivers/soc/qcom/smp2p_sleepstate.c:105 | CONFIG_QCOM_SMP2P_SLEEPSTATE=y |
| platform | `soc:qcom,spcom` | spcom | qcom | drivers/soc/qcom/spcom.c:2581 | CONFIG_MSM_SPCOM=y |
| platform | `soc:qcom,spss_utils` | spss_utils | qcom | drivers/soc/qcom/spss_utils.c:1230 | CONFIG_MSM_SPSS_UTILS=y |
| rpmsg | `qcom,glink:adsp.IPCRTR.-1.-1` | qcom_smd_qrtr |  |  |  |
| rpmsg | `qcom,glink:adsp.LOOPBACK_CTL_LPASS.-1.-1` |  |  |  |  |
| rpmsg | `qcom,glink:adsp.fastrpcglink-apps-dsp.-1.-1` | qcom,msm_fastrpc_rpmsg | qcom | drivers/char/adsprpc.c:5382 | CONFIG_MSM_ADSPRPC=y |
| rpmsg | `qcom,glink:adsp.pcie_drv.-1.-1` | pci-msm-drv |  |  |  |
| rpmsg | `qcom,glink:adsp.rpmsg_ctrl.0.0` |  |  |  |  |
| rpmsg | `qcom,glink:cdsp.IPCRTR.-1.-1` | qcom_smd_qrtr |  |  |  |
| rpmsg | `qcom,glink:cdsp.LOOPBACK_CTL_CDSP.-1.-1` |  |  |  |  |
| rpmsg | `qcom,glink:cdsp.cdsprmglink-apps-dsp.-1.-1` | qcom,msm_cdsprm_rpmsg | qcom | drivers/soc/qcom/cdsprm.c:1109 | CONFIG_QCOM_CDSP_RM=y |
| rpmsg | `qcom,glink:cdsp.cvp-glink-apps-dsp.-1.-1` | qcom,msm_cvp_dsp_rpmsg |  |  |  |
| rpmsg | `qcom,glink:cdsp.fastrpcglink-apps-dsp.-1.-1` | qcom,msm_fastrpc_rpmsg | qcom | drivers/char/adsprpc.c:5382 | CONFIG_MSM_ADSPRPC=y |
| rpmsg | `qcom,glink:cdsp.rpmsg_ctrl.0.0` |  |  |  |  |
| rpmsg | `qcom,glink:dsps.IPCRTR.-1.-1` | qcom_smd_qrtr |  |  |  |
| rpmsg | `qcom,glink:dsps.LOOPBACK_CTL_DSPS.-1.-1` |  |  |  |  |
| rpmsg | `qcom,glink:dsps.fastrpcglink-apps-dsp.-1.-1` | qcom,msm_fastrpc_rpmsg | qcom | drivers/char/adsprpc.c:5382 | CONFIG_MSM_ADSPRPC=y |
| rpmsg | `qcom,glink:dsps.rpmsg_ctrl.0.0` |  |  |  |  |
| rpmsg | `qcom,glink:npu.IPCRTR.-1.-1` | qcom_smd_qrtr |  |  |  |
| rpmsg | `qcom,glink:npu.rpmsg_ctrl.0.0` |  |  |  |  |

## Security / crypto / TrustZone

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `146bf720.tz-log` |  | qcom | drivers/firmware/qcom/tz_log.c:1705 | CONFIG_MSM_TZ_LOG=y |
| platform | `1de0000.qcedev` | qce | qcom | drivers/crypto/msm/qcedev.c:83 | CONFIG_CRYPTO_DEV_QCEDEV=y |
| platform | `1de0000.qcedev:qcom_cedev_ns_cb` | qce | qcom | drivers/crypto/msm/qcedev.c:84 | CONFIG_CRYPTO_DEV_QCEDEV=y |
| platform | `1de0000.qcedev:qcom_cedev_s_cb` | qce | qcom | drivers/crypto/msm/qcedev.c:84 | CONFIG_CRYPTO_DEV_QCEDEV=y |
| platform | `1de0000.qcrypto` | qcrypto | qcom | drivers/crypto/msm/qcrypto.c:5448 | CONFIG_CRYPTO_DEV_QCRYPTO=y |
| platform | `82400000.qseecom` | qseecom | qcom | drivers/misc/qseecom.c:9871 | CONFIG_QSEECOM=y |

## Sensors (IIO / SLPI)

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| iio | `iio:device0` |  | qcom | drivers/iio/adc/qcom-spmi-adc5.c:1155 | CONFIG_QCOM_SPMI_ADC5=y |
| iio | `iio:device1` |  | qcom | drivers/iio/adc/qcom-spmi-adc5.c:1155 | CONFIG_QCOM_SPMI_ADC5=y |
| iio | `iio:device2` |  | qcom | drivers/iio/adc/qcom-spmi-adc5.c:1155 | CONFIG_QCOM_SPMI_ADC5=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:vadc@3100` | qcom-spmi-adc5.c | qcom | drivers/iio/adc/qcom-spmi-adc5.c:1155 | CONFIG_QCOM_SPMI_ADC5=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:vadc@3100` | qcom-spmi-adc5.c | qcom | drivers/iio/adc/qcom-spmi-adc5.c:1155 | CONFIG_QCOM_SPMI_ADC5=y |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:vadc@3100` | qcom-spmi-adc5.c | qcom | drivers/iio/adc/qcom-spmi-adc5.c:1155 | CONFIG_QCOM_SPMI_ADC5=y |
| platform | `soc:qcom,msm-ssc-sensors` | sensors-ssc | qcom | drivers/sensors/sensors_ssc.c:421 | CONFIG_SENSORS_SSC=y |
| platform | `soc:qcom,npu-staticmap-mon` | static-map | qcom | drivers/devfreq/governor_staticmap.c:309 | CONFIG_DEVFREQ_GOV_STATICMAP=y |
| platform | `soc:qmi-ts-sensors` | qmi-therm-sensors | qcom | drivers/thermal/qcom/qmi_sensors.c:730 | CONFIG_QTI_QMI_SENSOR=y |

## Storage (UFS / eMMC / SD)

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `1d84000.ufshc` | ufshcd-qcom | qcom | drivers/scsi/ufs/ufs-qcom.c:2627 | CONFIG_SCSI_UFS_QCOM=y |
| platform | `1d87000.ufsphy_mem` | ufs_qcom_phy_qmp_v4 | qcom | drivers/phy/qualcomm/phy-qcom-ufs-qmp-v4.c:263 | CONFIG_PHY_QCOM_UFS=y |
| platform | `1db0000.ufscardice` | qcom_ice | qcom | drivers/crypto/msm/ice.c:1557 | CONFIG_CRYPTO_DEV_QCOM_ICE= |
| scsi | `0:0:0:0` | sd |  |  |  |
| scsi | `0:0:0:1` | sd |  |  |  |
| scsi | `0:0:0:2` | sd |  |  |  |
| scsi | `0:0:0:3` | sd |  |  |  |
| scsi | `0:0:0:4` | sd |  |  |  |
| scsi | `0:0:0:49456` |  |  |  |  |
| scsi | `0:0:0:49476` |  |  |  |  |
| scsi | `0:0:0:49488` |  |  |  |  |
| scsi | `0:0:0:5` | sd |  |  |  |
| scsi | `host0` |  |  |  |  |
| scsi | `target0:0:0` |  |  |  |  |

## Thermal / cooling / sensors of temperature

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| platform | `18591000.qcom,cpufreq-hw:qcom,cpu-isolation` | cpu_isolate | qcom | drivers/thermal/qcom/cpu_isolate.c:345 | CONFIG_QTI_CPU_ISOLATE_COOLING_DEVICE=y |
| platform | `18591000.qcom,cpufreq-hw:qcom,limits-dcvs` | msm_lmh_dcvs | qcom | drivers/thermal/qcom/msm_lmh_dcvs.c:794 | CONFIG_QTI_THERMAL_LIMITS_DCVS=y |
| platform | `c222000.tsens` | msm-tsens | qcom | drivers/thermal/msm-tsens.c:90 | CONFIG_THERMAL_TSENS=y |
| platform | `c223000.tsens` | msm-tsens | qcom | drivers/thermal/msm-tsens.c:90 | CONFIG_THERMAL_TSENS=y |
| platform | `soc:lmh_isense_cdsp` | msm_isense_cdsp | qcom | drivers/thermal/qcom/msm_isense_cdsp.c:155 | CONFIG_QTI_LIMITS_ISENSE_CDSP=y |

## Touch / input / keys / haptics

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| i2c | `2-005a` |  | awinic | drivers/input/misc/aw8697_haptic/aw8697.c:6815 | CONFIG_INPUT_AW8697_HAPTIC=y |
| i2c | `3-005a` | awinic_haptic | awinic | drivers/input/misc/aw8697_haptic_munch/aw_haptic.c:1085 | CONFIG_INPUT_AW8697_HAPTIC_MUNCH= |
| platform | `c440000.qcom,spmi:qcom,pm8009@a:qcom,power-on@800` |  | qcom | drivers/input/misc/qpnp-power-on.c:2767 | CONFIG_INPUT_QPNP_POWER_ON=y |
| platform | `c440000.qcom,spmi:qcom,pm8150@0:qcom,power-on@800` | qcom,qpnp-power-on | qcom | drivers/input/misc/qpnp-power-on.c:2767 | CONFIG_INPUT_QPNP_POWER_ON=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@2:qcom,power-on@800` | qcom,qpnp-power-on | qcom | drivers/input/misc/qpnp-power-on.c:2767 | CONFIG_INPUT_QPNP_POWER_ON=y |
| platform | `c440000.qcom,spmi:qcom,pm8150b@3:qcom,haptics@c000` |  | qcom | drivers/input/misc/qti-haptics.c:2067 | CONFIG_INPUT_QTI_HAPTICS= |
| platform | `c440000.qcom,spmi:qcom,pm8150l@4:qcom,power-on@800` | qcom,qpnp-power-on | qcom | drivers/input/misc/qpnp-power-on.c:2767 | CONFIG_INPUT_QPNP_POWER_ON=y |
| platform | `c440000.qcom,spmi:qcom,pmxprairie@8:qcom,power-on@800` | qcom,qpnp-power-on | qcom | drivers/input/misc/qpnp-power-on.c:2767 | CONFIG_INPUT_QPNP_POWER_ON=y |
| platform | `soc:fingerprint_fpc` | fpc1020 | fpc | drivers/input/fingerprint/fpc_fod/fpc1020_platform_tee.c:1274 | CONFIG_FINGERPRINT_FPC_FOD= |
| platform | `soc:fingerprint_goodix` | goodix_fp | goodix | drivers/input/fingerprint/goodix/gf_spi.c:261 | CONFIG_FINGERPRINT_GOODIX= |
| platform | `soc:gpio_keys` | gpio-keys | gpio-keys | drivers/input/keyboard/gpio_keys.c:765 | CONFIG_KEYBOARD_GPIO=y |
| platform | `soc:regulator-haptics-boost` | reg-fixed-voltage | regulator-fixed | drivers/regulator/fixed.c:196 | CONFIG_REGULATOR_FIXED_VOLTAGE=y |
| platform | `soc:xiaomi_touch` | xiaomi-touch | xiaomi-touch | drivers/input/touchscreen/xiaomi/xiaomi_touch.c:569 | CONFIG_TOUCHSCREEN_XIAOMI_TOUCHFEATURE=y |
| spi | `spi1.0` | fts_ts | focaltech | drivers/input/touchscreen/focaltech_3658u/focaltech_core.c:2312 |  |

## USB / Type-C / DisplayPort

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| i2c | `2-0042` | fsa4480-driver | qcom | drivers/soc/qcom/fsa4480-i2c.c:456 | CONFIG_QCOM_FSA4480_I2C=y |
| platform | `88e3000.hsphy` | msm-usb-hsphy | qcom | drivers/usb/phy/phy-msm-snps-hs.c:958 | CONFIG_MSM_HSUSB_PHY=y |
| platform | `a600000.dwc3` | dwc3 | snps | drivers/usb/dwc3/core.c:1965 |  |
| platform | `a600000.ssusb` | msm-dwc3 | qcom | drivers/usb/dwc3/dwc3-msm.c:4995 | CONFIG_USB_DWC3_MSM=y |
| platform | `a704000.qcom,usbbam` | usb_bam | qcom | drivers/platform/msm/usb_bam.c:3441 | CONFIG_USB_BAM=y |
| platform | `soc:usb_nop_phy` | usb_phy_generic | usb-nop-xceiv | drivers/usb/phy/phy-generic.c:354 | CONFIG_NOP_USB_XCEIV=y |

## Wi-Fi / Bluetooth / connectivity

| Bus | Device | Driver (live) | Compatible | Kernel source | Kconfig |
|---|---|---|---|---|---|
| pci | `0000:01:00.0` | cnss_pci |  |  |  |
| platform | `1e00000.qcom,ipa:ipa_smmu_wlan` | ipa | qcom | drivers/platform/msm/ipa/ipa_api.c:3152 |  |
| platform | `3ac0000.slim:qca6390` |  | qcom |  |  |
| platform | `b0000000.qcom,cnss-qca6390` | cnss2 | qcom | drivers/net/wireless/cnss2/main.c:2655 |  |
| platform | `vendor:bt_qca6390` | bt_power | qca | drivers/bluetooth/bluetooth-power.c:48 | CONFIG_MSM_BT_POWER=y |
| slimbus | `btfmslim_slave` | btfmslim-driver | qcom |  |  |
| slimbus | `btfmslim_slave_ifd` |  |  |  |  |

