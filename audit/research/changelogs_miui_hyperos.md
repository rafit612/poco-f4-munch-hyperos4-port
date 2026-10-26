# POCO F4 / Redmi K40S (munch): official software history and HyperOS 3/4 alignment

Researched 2026-10-23. Tags used below:
- **[V-OTA]**: read directly from the official Xiaomi OTA package on bigota.d.miui.com. I fetched only `META-INF/com/android/metadata` and the payload manifest using HTTP range requests.
- **[V-local]**: read from the MD5-verified stock image in `stock_rom_1.0.9/` or `stock_rom_miui14/`.
- **[XFU]**: xmfirmwareupdater.com, or its tracker data on GitHub.
- **[MR]**: miuirom.org.
- **[unverified]**: from secondary press only, or inferred.

## 0. Key answers

1. **munch never officially received HyperOS 2.0 or HyperOS 3.** The device is HyperOS 1 only. I confirmed the hardware agent's finding:
   - No OS2.x build exists for munch in the XFU tracker data or on MR.
   - MR says outright that it "will not receive HyperOS 2".
   - XiaomiTime put the POCO F4 and K40S on its June 2025 EOL list (reported by HuaweiCentral and droid.tools).
   - The POCO F4 is missing from the global HyperOS 3 device list (FoneArena).
   - The POCO F4 **GT** (ingres, SD8 Gen 1) did get HyperOS 2.0, on an Android 14 base (OS2.0.2.0.ULJMIXM, and OS2.0.3.0 as Stable Beta in Jan 2026).
2. **The HyperOS 1 builds are Android 14, not Android 13.** The `U` in `ULMMIXM` stands for Android 14. The system fingerprint is `munch:14/UKQ1.231207.002`.
   - The *vendor* partition still carries the Android 13 GRF base `munch:13/RKQ1.211001.001` [V-local], which is why the vendor looks like Android 13.
   - Vendor props: `ro.board.first_api_level=30`, `ro.product.first_api_level=31`.
   - `V816.0.9.0.ULMMIXM` is just the internal name for OS1.0.9.0.ULMMIXM.
3. **The latest official Global build is OS1.0.12.0.ULMMIXM (V816.0.12.0.ULMMIXM).**
   - Build timestamp 2026-04-17; uploaded to the CDN 2026-04-27.
   - Recovery ROM only, no fastboot package. MD5 `6af849fdcc3ce5ba2e6cdab6bf2f21c0`, 4,722,396,170 bytes [V-OTA].
   - URL: `https://bigota.d.miui.com/OS1.0.12.0.ULMMIXM/miui_MUNCHGlobal_OS1.0.12.0.ULMMIXM_6af849fdcc_14.0.zip`
   - **Security patch is still 2025-04-01** [V-OTA], the same as 1.0.9.
   - Changelog: "Fix: Improved system stability and user experience".
   - Xiaomi pushed this post-EOL refresh in about April–June 2026 to several 2022 devices (Xiaomi 12, F4, F4 GT, Note 11 Pro+), as reported by gsmManiaK on 2026-05-12. The reason was not published.
4. **No newer official firmware exists to fix camera or touch.** I compared payload manifest hashes [V-OTA]:
   - All firmware partitions are byte-identical between Global OS1.0.9.0 (Apr 2025) and OS1.0.12.0 (Apr 2026): modem, xbl, xbl_config, tz, hyp, aop, bluetooth, dsp, keymaster, cmnlib/cmnlib64, devcfg, qupfw, uefisecapp, imagefv, featenabler.
   - They are also identical in EEA OS1.0.8.0/1.0.9.0 and China OS1.0.15.0.
   - So the **April 2025 firmware set is final for every region**.
   - Only these changed in 1.0.12: abl (new build stamp `250402…` → `450422…`), boot, vendor_boot (126 bytes), dtbo, vendor (+110 KB), odm, system, system_ext, product, mi_ext and vbmeta.
   - odm: only the build props changed [V-OTA].
   - dtbo: 26 of 27 overlays are identical. One overlay grew by about 1.1 KB; I did not decode its content.
   - vendor: I did not extract and diff the file contents; the job was cut short when the session was interrupted. **This is the one remaining check.**

## 1. Timeline

SPL = security patch level.

### Global (MIXM): launch June 2022, Android 12

| OS | Android | Build | Date (fastboot / recovery) | SPL |
|---|---|---|---|---|
| MIUI 13 | 12 | V13.0.1.0.SLMMIXM | 2022-04-28 / 2022-06-28 | ? |
| MIUI 13 | 12 | V13.0.4.0.SLMMIXM | 2022-06-23 / 06-30 | 2022-06 |
| MIUI 13 | 12 | V13.0.5.0.SLMMIXM | 2022-08-15 / 08-25 | 2022-08 |
| MIUI 13 | 12 | V13.0.6.0.SLMMIXM | 2023-01-11 / 01-16 | 2022-12 |
| MIUI 14 | 13 | V14.0.1.0.TLMMIXM | 2023-01-11 / 01-28 | 2022-12 |
| MIUI 14 | 13 | V14.0.2.0.TLMMIXM | 2023-03-12 / 03-17 | 2023-03 |
| MIUI 14 | 13 | V14.0.3.0.TLMMIXM | 2023-06-05 / 06-09 | 2023-06 |
| MIUI 14 | 13 | V14.0.4.0.TLMMIXM | 2023-09-04 / 09-11 | 2023-09-01 [V-local, vendor] |
| MIUI 14 | 13 | V14.0.5.0.TLMMIXM | 2023-12-06 / 12-14 | 2023-12 |
| MIUI 14 | 13 | V14.0.6.0.TLMMIXM | 2024-02-04 / 02-20 | 2024-02 |
| HyperOS 1 | 14 | OS1.0.1.0.ULMMIXM | 2024-04-16 / 04-26 | 2024-04-01 [V-OTA] |
| HyperOS 1 | 14 | OS1.0.2.0.ULMMIXM | 2024-06-03 / 06-18 | 2024-06 |
| HyperOS 1 | 14 | OS1.0.3.0.ULMMIXM | 2024-07-15 / 08-05 | 2024-07 |
| HyperOS 1 | 14 | OS1.0.4.0.ULMMIXM | 2024-08-05 / 08-19 | 2024-08 |
| HyperOS 1 | 14 | OS1.0.5.0.ULMMIXM | 2024-09-03 / 09-19 | 2024-09-01 [V-OTA] |
| HyperOS 1 | 14 | OS1.0.8.0.ULMMIXM | 2024-12-16 / 2025-01-06 | 2024-12-01 [V-OTA] |
| HyperOS 1 | 14 | **OS1.0.9.0.ULMMIXM** (our vendor) | 2025-04-02 / 04-12 | 2025-04-01 [V-OTA] |
| HyperOS 1 | 14 | **OS1.0.12.0.ULMMIXM** (latest) | built 2026-04-17, CDN 2026-04-27, recovery only | 2025-04-01 [V-OTA] |

Global never had builds 1.0.6, 1.0.7, 1.0.10 or 1.0.11 (no XFU pages for them).

### Other regions (latest builds)

| Region | Last MIUI 14 | Latest HyperOS 1 | Notes |
|---|---|---|---|
| EEA (EUXM) | V14.0.4.0.TLMEUXM (Jun 2023) | OS1.0.9.0.ULMEUXM: built 2026-04-26, CDN 2026-06-12, "Stable Beta" on XFU, SPL 2025-04-01 [V-OTA] | 1.0.8.0 (Apr 2025) was the last full stable |
| India (INXM) | V14.0.10.0.TLMINXM (Apr 2024) | OS1.0.7.0.ULMINXM (Apr 2025) | no 2026 build |
| Indonesia | V14.0.11.0 | OS1.0.9.0.ULMIDXM (Jun 2026 beta) | |
| Russia / Turkey | V14.0.6.0 / V14.0.5.0 | OS1.0.8.0 (Jun 2026 beta) | |
| Taiwan | V14.0.5.0 | OS1.0.9.0.ULMTWXM (Jun 2026) | |
| China K40S (CNXM) | V14.0.9.0.TLMCNXM (Dec 2023) | OS1.0.15.0.ULMCNXM, fastboot 2026-03-06, SPL 2025-03-01 [V-OTA] | see note below |

China K40S history:
- MIUI 13 launch build was 13.0.2.0.SLMCNXM (Mar 2022), up to 13.0.11.0 (Sep 2022).
- 13.2.x TLMCNXM (Nov–Dec 2022) was MIUI 13 on Android 13.
- MIUI 14 ran from 14.0.3.0 (Jan 2023) to 14.0.9.0.
- HyperOS 1 ran 1.0.1.0 (Mar 2024) → 1.0.10.0 (Apr 2025, SPL Mar 2025) → 1.0.12.0 (Dec 2025) → 1.0.15.0.

### Sibling devices worth knowing

| Device | SoC | Latest official OS |
|---|---|---|
| Xiaomi Pad 6 (pipa) | **SD870** | **HyperOS 2.0 on Android 14**: OS2.0.16.0.UMZMIXM, May 2026. EEA 2.0.14.0 has SPL April 2026 [XFU] |
| POCO F3 / K40 (alioth) | SD870 | HyperOS 1 on Android 13 (OS1.0.5.0.TKHMIXM, Jan 2026) |
| POCO F4 GT (ingres) | SD8 Gen 1 | HyperOS 2.0 on Android 14 |
| Xiaomi 12 / 12 Pro | SD8 Gen 1 | HyperOS 3 on Android 15 (OS3.0.4.0.VLCMIXM, May 2026) |

The Pad 6 is the proof that Xiaomi ships HyperOS 2 (HyperCore scheduler, new animations) on kona/SD870.

## 2. Per-version highlights (official changelogs)

Official munch changelogs are thin. Apart from the two big version jumps, they are security patches and "stability" notes. **I found no official changelog item about the camera, display refresh rate, DC dimming, touch or charging for munch.**

- **MIUI 13 (Android 12, 2022)**
  - Launch features: 120 Hz E4 AMOLED, 360 Hz touch sampling (POCO marketing), Dolby Vision/Atmos stereo, 67 W charging, side fingerprint, IR, NFC.
  - Updates 13.0.4–13.0.6 were security patches only.
- **MIUI 14 (Android 13, Jan 2023), 14.0.1.0**
  - "Uses less memory, swift and responsive", new widget formats, better Settings search.
  - Came with an Android 13 upgrade warning about "overheating and performance issues while adapting".
  - 14.0.2–14.0.6 were security patches only.
- **HyperOS 1 (Android 14, Apr 2024), 1.0.1.0**
  - New animation language, system font, Weather redesign, notifications, lock-screen art posters, upgraded multi-window.
  - China notes also list: dynamic thread priority, energy-efficient rendering, storage refresh (defrag), smart antenna and network selection, HyperConnect (cross-device camera/screen/clipboard), and a TEE security OS.
- **1.0.2 / 1.0.3**: security patches; 1.0.3 also improved calculator button sensitivity.
- **1.0.4**
  - Fix: video apps displayed wrongly when rotating in floating windows.
  - Fix: wrong size of pinned floating windows in games.
  - New: switch for long-press to edit the home screen.
- **1.0.5 / 1.0.8**: security patches and "system stability".
- **1.0.9** (Apr 2025): "System stability; fixed errors in some cases".
- **1.0.12** (Apr 2026): "Improved system stability and user experience". Firmware is unchanged; see section 0.

Hardware notes for this unit (from project memory):
- Cameras: Sunny OV64B40 main, AAC OV8856 ultrawide, OFilm IMX596 front, Sunny GC02M1 macro. Some other munch units ship an IMX582 main camera instead.
- The display is a clone replacement panel. Touch problems are therefore more likely the panel or controller than firmware, and **no official firmware after Apr 2025 exists to fix them**.

## 3. MiuiCamera versions

| Build | MiuiCamera | Source |
|---|---|---|
| HyperOS 1 OS1.0.9.0.ULMMIXM | **5.1.001140.0** (versionCode 510011400, targetSdk 33) | [V-local] product.img |
| HyperOS 1 OS1.0.12.0 | unknown; product partition changed. Could be 5.1.x [unverified] | |
| MIUI 14 / MIUI 13 | not determined (no local product image); likely 4.x–5.0.x [unverified] | |
| Port (HyperOS 4) | 6.7.000070.0 (re-signed); Xiaomi 17 Global ships 6.6.000570.5 | audit/global17 |

No official HyperOS 2 build exists for munch, so there is no "HyperOS 2 camera app for munch". The camera tuning binaries (`com.qti.tuned.*`) changed between MIUI 14 and HyperOS 1 (audit/agents/camera). HyperOS 1 1.0.9 is the latest validated set.

## 4. HyperOS 3 / 4 feature matrix for SD870

SD870 has a Hexagon 698 DSP (about 15 TOPS), Adreno 650, LPDDR5, Wi-Fi 6, BT 5.2, and no UWB, satellite or LE Audio certification.

| Feature (version) | Hardware need | On SD870 |
|---|---|---|
| New animations, HyperIsland (HOS3) | GPU/UI only; Xiaomi limits it on some mid-range models | **Yes**: keep, tune the blur level |
| Soft Light Glass with full refraction (HOS4) | Xiaomi requires SD8 Elite / D9500 / XRING for the full effect | **Partial**: use the reduced or low-blur level (`persist.sys.background_blur_*`, advanced-visual-effects off) |
| Lock screen flexible clock, stacked widgets/notifications (HOS4) | Software; flexible clock is flagship-only | Yes (stacking); flexible clock partial |
| HyperCore scheduler and dynamic memory (HOS2+) | Software; shipped on Pad 6 (SD870) | **Yes**: but its perf configs target the new SoC, so keep munch thermal/perf HAL settings |
| AI memory preloading (HOS4) | Software and RAM; 8 GB is OK | Yes / partial |
| Gemini app, Gemini Live, Connected Apps (HOS3/4 Global) | Cloud | **Yes** (needs GMS and Global region) |
| Circle to Search (Global) | Cloud, Google app plus launcher/overlay gating | **Yes**: keep the overlay and `CONTEXTUAL_SEARCH` flag |
| Gemini Nano / AICore (on-device) | Allowlisted SoCs; Xiaomi uses AICORE_QC_SM8850 etc. | **No**: disable AICore features |
| HyperAI writing, summary, translation, speech recognition, AI search (HOS3) | Mostly cloud (MiMo / Gemini); some on-device ASR | **Partial**: cloud features work; offline and on-device modes may fail |
| AI Interpreter / call translation | Cloud plus audio HAL path | Partial [unverified] |
| AI Eraser / Magic Painting / AI dynamic wallpapers | Cloud or NPU, depending on feature | Partial (cloud); dynamic wallpapers are GPU-heavy, so optional |
| Super XiaoAi 2.0, Inspiration Ball, Expert Mode (HOS4 China) | Cloud; China-only | Not for Global; drop |
| HyperConnect: Touch to Share, Apple interop, phone↔PC, camera relay, dual-phone sync (HOS3/4) | Wi-Fi P2P, BT LE, NFC (Touch to Share uses NFC/UWB on some models) | **Partial**: Wi-Fi/BT parts work; UWB-based parts do not |
| UWB tag / car key, satellite messaging, LE Audio/Auracast | Dedicated radios | **No**: disable |
| Camera app 6.x features (HOS3/4: Leica looks, master/AI portrait, AI HDR, "more responsive camera") | ISP/NPU and per-device tuning; Leica only on Leica-branded devices | **Partial**: munch has no Leica; watermark only. Night and portrait depend on munch camx tuning. Use official munch tuning plus 5.1 app, or carefully gated 6.x |
| Upgraded HDR algorithm (HOS4) | New ISP/NPU | No / unverified |
| 120 Hz / variable refresh, DC dimming | Panel | Yes: keep the official munch display config. DC dimming depends on the clone panel |
| Post-quantum encryption, TEE cross-device unlock (HOS3) | Software / TEE | Software parts yes; TEE parts depend on the old QSEE (keymaster 4.x) |

## 5. Alignment recommendations for our port

1. **Firmware, modem and bootloader**
   - Firmware: stay on the OS1.0.9.0 Global set. It is bit-identical to 1.0.12, so there is nothing newer to flash.
   - Do not flash firmware from other regions expecting fixes; they are the same images.
2. **Vendor, odm, dtbo, boot**
   - Optional candidate: V816.0.12.0.ULMMIXM vendor/odm/dtbo/vendor_boot/boot.
   - Before switching, diff its vendor against 1.0.9: download about 760 MB of vendor payload ops via range requests. My extractor script was lost when the scratchpad was cleared, so this needs redoing.
   - Look in particular at `lib64/camera`, `firmware/` touch firmware, `etc/thermal*`, and `build.prop`.
   - Expect small changes. The security patch does not advance: vendor and platform SPL stay 2025-04-01.
3. **Security patch**: report vendor SPL 2025-04-01, which matches the newest official build. The platform SPL comes from the port's system (Android 17).
4. **Camera**
   - Keep the official HyperOS 1 munch camx stack: `com.qti.tuned.*`, `sensormodule`, `camxoverridesettings`, `munch.xml` camera features.
   - MiuiCamera 5.1.001140.0 is the official, validated pairing.
   - Only try 6.x if its feature keys are gated to munch capabilities. Disable Leica, AI-HDR and NPU modes.
5. **Props and identity**: match the latest official build.
   - `ro.product.*` brand POCO, model `22021211RG`, marketname "POCO F4 5G" for the Global munchg odm.
   - `ro.board.first_api_level=30`, `ro.product.first_api_level=31`.
   - Vendor fingerprint `Redmi/munch/munch:13/RKQ1.211001.001/V816.0.12.0.ULMMIXM` if moving to the 1.0.12 vendor.
6. **Features to enable**: new animations at reduced blur, HyperIsland, Gemini app, Circle to Search, cloud HyperAI (writing, translation, ASR), HyperConnect over Wi-Fi/BT, widget stacking.
7. **Features to disable or hide**: Gemini Nano / AICore (SM8850 feature flags), full Soft Light Glass refraction, UWB, satellite, LE Audio/Auracast, China-only XiaoAi/MiMo items, Xiaomi 17 camera Leica modes, and any eSIM/dti feature flags inherited from the Xiaomi 17.
8. **Performance and thermal**
   - Keep munch's `init.qcom.post_boot.sh` and `thermal-normal.conf` from 1.0.9.
   - HyperOS 4 perf/joyose profiles target new SoCs; check for a munch profile, or fall back to the official kona settings.

## Sources
- XFU HyperOS munch list: https://xmfirmwareupdater.com/hyperos/munch/ (plus per-build pages, e.g. https://xmfirmwareupdater.com/hyperos/munch/stable/OS1.0.9.0.ULMMIXM/, /OS1.0.1.0.ULMMIXM/, /OS1.0.4.0.ULMMIXM/, /OS1.0.15.0.ULMCNXM/)
- XFU MIUI pages: https://xmfirmwareupdater.com/miui/munch/stable/V14.0.1.0.TLMMIXM/ (etc.)
- XFU tracker data: https://github.com/XiaomiFirmwareUpdater/miui-updates-tracker (data/latest.yml, rss/munch.xml)
- miuirom.org: https://miuirom.org/phones/poco-f4 and https://miuirom.org/phones/redmi-k40s
- XimiTime OS1.0.12.0.ULMMIXM: https://ximitime.com/hyperos/munch/version/OS1.0.12.0.ULMMIXM/
- Official OTA (verified metadata): https://bigota.d.miui.com/OS1.0.12.0.ULMMIXM/miui_MUNCHGlobal_OS1.0.12.0.ULMMIXM_6af849fdcc_14.0.zip
- gsmManiaK, post-EOL update (2026-05-12): https://www.gsmmaniak.pl/1658372/xiaomi-aktualizacja-do-hyperos-dla-starych-telefonow/
- EOL list (June 2025): https://www.huaweicentral.com/these-7-xiaomi-devices-may-get-their-last-hyperos-update-next-month/amp/ ; https://droid.tools/7-new-devices-will-receive-hyperos-next-month/
- HyperOS 3 global device and feature list: https://www.fonearena.com/blog/465226/xiaomi-hyperos-3-device-list-global.html
- HyperOS 3 launch: https://www.gizmochina.com/2025/10/28/xiaomi-hyperos-3-launches-globally-with-a-host-of-smart-features/
- HyperOS 2 announcement: https://www.gsmarena.com/xiaomi_introduces_hyperos_2_with_more_performance_optimizations_and_more_ai-news-65128.php
- Pad 6 HyperOS 2 changelog: https://xmfirmwareupdater.com/hyperos/pipa/stable/OS2.0.2.0.UMZMIXM
- HyperOS 4 features: https://gadgets.beebom.com/guides/xiaomi-hyperos-4-features-list
- HyperOS 4 global beta: https://www.notebookcheck.net/Xiaomi-reveals-first-global-phones-eligible-for-initial-HyperOS-4-update.1396033.0.html ; https://digg.com/tech/9yxdksfc
- HyperIsland limits: https://www.notebookcheck.net/No-Hyper-Island-Xiaomi-reportedly-prevents-new-HyperOS-3-feature-from-working-on-multiple-Redmi-Note-smartphones.1126030.0.html
- Gemini Nano devices: https://developer.android.com/ai/aicore ; https://androidauthority.com/gemini-nano-features-devices-3490062
- GSMArena POCO F4 specs: https://www.gsmarena.com/xiaomi_poco_f4-11627.php
