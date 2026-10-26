# POCO F4 (munch) app audit (read-only)

- **Date:** 2026-10-23
- **Device:** HyperOS 4 Full Global port, after the camera/vendor fixes
- **Sources:** `adb pm` and `dumpsys package` (486 packages), compared against the indexed APKs of:
  - Xiaomi 17 Global HyperOS 4 (`G17`, including its mi_ext);
  - official munch HyperOS 1.0.9 Global (`H1`);
  - the original port (`PORT`);
  - the current flashed images (`NOW`).
- **Machine-readable table:** `app_inventory.tsv`. Columns: package, label, versionName, versionCode, partition, type, installed_u0, enabled, launcher, signer, targetSdk, abi, origin, codePath, G17_ver, H1_ver, PORT_ver.

## 1. Inventory summary

| origin | count | meaning |
|---|---|---|
| HOS4(port+G17) | 195 | same build in the port base and Xiaomi 17 Global (current HyperOS 4) |
| G17-Global | 75 | Global HyperOS 4 apps we added (Security, Music, Mms, Clock, XMSF, ...) |
| HOS4-portbase | 57 | HyperOS 4 China-base builds (Xiaomi 17 Global has another, mostly newer, build) or AOSP-only |
| user | 107 | Play / user-installed |
| apex | 27 | mainline modules |
| vendor(H1) | 14 | vendor apps (official HyperOS 1 vendor) |
| sys+data-update | 7 | system app updated from Play/GetApps (GMS, Mi Browser, GetApps, Game Center, XMSF, Package installer, System apps updater) |
| HyperOS1-OLD | 1 | `com.android.camera` 5.1.001140.0, intentionally |

**Signers:**
- **Platform key:** shared by all Xiaomi system apps (`6c02dd51` = C9:00… platform), so the Global and China copies are interchangeable signature-wise.
- **Google:** `d1b21c60`.

**ABI:**
- 244 packages are arm64.
- The rest are code-less (overlays/resources), so there are no 32-bit-only apps. `abilist32` still exists (armeabi-v7a).

**User apps:**
- **targetSdk:** min 29 (LMC 8.4 snapcam); everything else is 34–37. No compatibility risk.
- **Crashes:** none in the current crash buffer apart from the fingerprint HAL (sensor damaged). Configupdater and Photos each crashed once in the perf log.

## 2. Duplicate groups and recommendation

| function | packages | current default | recommendation (risk) |
|---|---|---|---|
| Phone / dialer | `com.android.contacts` (MIUI CN 18.30.00.20) + InCallUI 40.01.05 in the ROM; Google Phone from the Play Store | user picks (both kept, 2026-10-26) | Keep both. Google Phone is not in the ROM (mi_ext only has placeholders); Google's default-app overlay stays. |
| Contacts | MIUI Contacts (ROM); Google Contacts only if the user installs it | MIUI | Fine as is. |
| SMS | `com.android.mms` (MIUI Global 18.0.0.36) + `com.google.android.apps.messaging` | SMS = com.android.mms | Keep both: Google Messages gives RCS. User choice; hiding one is a user action (none). |
| Camera | MiuiCamera 5.1 + LMC 8.4 (org.codeaurora.snapcam) | — | Keep both (intentional). |
| Gallery | MIUI Gallery 4.3.1.6-global + Google Photos (user) | — | Keep. |
| Files | MIUI File Manager + DocumentsUI (system, required) + Files by Google (user) | — | User may uninstall Files by Google (none). |
| Calendar | Xiaomi Calendar Global (data-app) + Google Calendar (user) | — | User choice. Add `GoogleCalendarSyncAdapter` so the Xiaomi Calendar syncs Google accounts (see §5). |
| Browser | Mi Browser (updated-sys) + Chrome + Brave + Edge (user) | BROWSER = Chrome | User choice. Mi Browser can be removed from mi_ext if unwanted (low). |
| Remote (IR) | Mi Remote + Tiqiaa remote (user) | — | User choice (munch has an IR blaster). |
| Assistant | Google app (Velvet CtS) + Gemini + Assistant shortcut app (user) | ASSISTANT = Google | Keep. |
| Video | Mi Video (MIUIVideoPlayer, system, no launcher) + MX Player + Google TV | — | Fine. |
| Keyboard | Gboard only (+ Google voice IME) | — | No duplicate. |
| Compass / Recorder / Clock / Calculator / Messages (MIUI) | only the Global copies now (China copies removed earlier) | — | Done. |

There are no same-package duplicates left on any partition. The China/Global shadowing was fixed earlier.

## 3. Apps from an older OS (and why)

| package | installed | newer HyperOS 4 build | can HyperOS 4 replace it? |
|---|---|---|---|
| com.android.camera | 5.1.001140.0 (HyperOS 1, official munch) | G17 6.6.000570.5 / port 6.7.000070.0 | **No.** The vendor is now the official HyperOS 1 camera stack (OV64B40/OV8856/IMX596/GC02M1 tuning). The 6.x apps call newer camx/anc node APIs: portrait crashed in `libanc_dc_base` and night photos came out purple. Keep 5.1. |
| com.miui.gallery | 4.3.1.6-global (older Global build from port base) | G17 5.4.2.10 | **No.** G17 Gallery needs `hyperos.rustruntime.v3` / runtime 3.9 and crashes on the port's 3.1. Keep 4.3.1.6. |
| vendor apps (Soter, IFAA, Eid, Mipay, CneApp, TimeService, GFTest, SensorTestTool, gpudrivers, CACert, IWlan) | 13 (HyperOS 1 vendor) | — | Keep. They match the vendor HALs. |
| com.android.nfc (NQNfcNci 16) + ST extension | 16 | G17 ships Nfc_st (ST chip) | **No.** munch has NXP SN100U, so keep NQNfcNci. The ST extension service is unused but harmless. |

The rest of `HOS4-portbase` are not old: they are HyperOS 4 China-region builds of the same generation (see §4).

## 4. China-base builds / China-only apps still present

**China-only** (not in official munch Global or in Xiaomi 17 Global):

| package | what | remove? |
|---|---|---|
| com.miui.contentextension (Taplus) | CN long-press text recognition/search | Remove from product (low). No dependents found. |
| com.miui.contentcatcher | CN app-content capture service (system uid) | Remove together with Taplus (low–medium; framework tolerates absence on Global). |
| com.xiaomi.digitalkey | CN car digital key (system uid) | Remove (low). |
| com.xiaomi.macro (MiMacro) | CN game macro | Remove (low). |
| com.xiaomi.app.toolbox | CN game toolbox | Remove (low–medium; Game Center Global uses its own toolbox). |
| com.xiaomi.security.onetrack | CN security telemetry | Remove (low). |
| com.newcall.overlay.miui | CN "NewCall" video-call overlay | Remove (low). |
| com.miui.wmsvc (WMService, system uid) | watermark/WM service | Keep (medium: may be used by Screenshot/Gallery). |
| com.wapi.wapicertmanage, com.mobiletools.systemhelper (**correction 2026-10-25: not harmless** - China carrier self-registration + Baidu location SDK sending IMEI/IMSI/cell/location; removed from product/pangu in `out_tele`), com.xiaomi.gnss.polaris | WAPI certs / port helper / GNSS assist | Keep (harmless or needed). |
| com.miui.accessibility "V8.0.8.CN" (Mi Ditto) | China build | Replace with G17 V0.9.3.GL (low; no Rust, no sharedUid). |

**China-region HyperOS 4 builds with a Global G17 equivalent:**
- All checked: no Rust runtime, platform key.
- Ranked by value / risk:
  - **Low risk, user-visible:**
    - Notes 3.0.7.1 → 3.2.2.7 (G17 data-app; move to app/);
    - Clipboard/phrases 3.9.4 → 5.7.2;
    - Screenshot;
    - Screen Recorder (system uid);
    - Quick ball;
    - MiWallpaper;
    - DeviceInfoQR.
  - **Region data:** CarrierStudioApn 19.0.0 → 23.0.0 (Global APN/carrier DB; useful for BD carriers). Low–medium.
  - **Medium (system uid, framework-coupled):**
    - AOD;
    - Notification center;
    - SecurityAdd/SecurityCore — **recommended**: they pair with the Global Security 13.5.8 already installed;
    - Mirror / Mi Connect / Continuity (Global cross-device builds);
    - AON.
  - **Keep port build:**
    - MiuiHome (G17 needs Rust 3.9);
    - SystemUI plugin (tied to the port SystemUI; G17 is older);
    - MiSound (Earphones; tied to the Dolby/audio stack);
    - AuthManager (`com.lbe.security.miui`; core permission app);
    - MiuiCredentialManager;
    - Gboard/Play/Downloads (they update via Play).

## 5. HyperOS 4 apps missing on the phone

**Supported on munch and worth adding:**
- **GoogleCalendarSyncAdapter.** Needed for the Xiaomi Calendar and Google account sync.
- **aptxals** (`com.qualcomm.qtil.aptxals`). aptX Adaptive license service; SD870/QCA6390 support aptX Adaptive.
- **xdivert** (Smart-Divert). Dual-SIM call divert.
- **ThirdAppAssistantGlobal**. Smart app assistant.
- **Mi Mover** (MIUIHuanjiGlobal). Earlier it was a data-app; it's absent now.
- **TrichromeLibrary64 + YTMusic.** Optional; Chrome from Play brings its own.
- **Wallpaper Carousel** (MiGalleryLockScreenGlobalOs4). Optional; ads-based.
- **MiuiPocoLauncherResOverlay.** POCO-branded launcher resources; cosmetic.
- **dpmserviceapp** (QTI data perf) and **FrameworksResNonModem**. Check vendor DPM support first; the vendor has `vendor_dpmtcm_socket`, so `dpmserviceapp` is plausible.
- **GoogleFeedback** and the **Google mainline overlays**. Low value.

**Not supported or not wanted on munch (skip):**
- eSIM: EuiccGoogle, MIUIEsimLPA, EsimTransferOverlay.
- Gemini Nano: AICore stub and AICoreConfigOverlay.
- Car / carrier apps: MIS (car), dti carrier apps (LatAm), Vodafone/H3G carrier overlays.
- CameraTools (needs a newer camera stack).
- Bloat / telemetry: Facebook preinstalls, MSA, Analytics, Community/Store.
- Google NetworkStack/CaptivePortal/PackageInstaller swaps. These are core-module swaps with no user benefit.

**HyperOS 4 parts present but useless on munch** (harmless; leave them):
- the UWB resource overlays;
- the IFAA/Soter/Eid/Mipay China payment vendor apps (vendor, same as official Global);
- ST NFC extension;
- WAPI.

## 6. Proposed image changes (ranked by risk, lowest first)

1. **product remove** (China-only):
   - `priv-app/MIUIContentExtension`
   - `app/ContentCatcherOS4`
   - `app/com.xiaomi.macro`
   - `priv-app/Toolbox`
   - `app/SecurityOnetrackService`
   - `overlay/MiuiNewCallSdkResOverlay.apk`

   **system_ext remove:** `app/digitalkey`.
2. **product add/replace** (G17, no Rust):
   - `app/GoogleCalendarSyncAdapter`
   - `app/ThirdAppAssistantGlobal`
   - Notes, Phrase, Screenshot, ScreenRecorder, TouchAssistant, MiWallpaper, DeviceInfoQR (G17 builds)
   - MIUIAccessibility (Global)

   **system_ext:** `priv-app/aptxals`.
3. **product:** SecurityAdd and SecurityCore (G17) to match Global Security.

   **system_ext:** CarrierStudioApn 23.0.0 (G17).
4. ~~mi_ext remove GoogleDialer / GoogleContacts~~ — not needed: they are empty placeholders in this port; the user keeps both dialers (2026-10-26).
5. **Medium:**
   - AOD and NotificationCenter (G17);
   - Mirror, mi_connect_service and LyraSdkSpp (G17 Global cross-device);
   - `xdivert` and `dpmserviceapp` (system_ext).

   Each needs a privapp allowlist check (G17 XMLs) and a boot test.
6. **Do NOT change:**
   - MiuiCamera 5.1
   - Gallery 4.3.1.6
   - MiuiHome
   - SystemUI plugin
   - MiSound
   - AuthManager
   - NQNfcNci
   - vendor apps

Every add needs the same pre-flash checks as before:
- no `hyperos.rustruntime`;
- `uses-library` present;
- native libs uncompressed (or a data-app);
- privapp permissions allowlisted (`privcheck.py`);
- platform cert C9:00.
