# Signature fix and call-speaker fix: build, flash and test plan (prepared 2026-10-31, nothing flashed)

What it changes, on the **system partition only** (no data wipe, product and vendor untouched):
| File | Change | Why |
|---|---|---|
| `/system/framework/framework.jar` | Seven real signature and digest checks restored; new helper `com.xBuild.isSystemPath`; the full APK check is skipped only for APKs under `/system`, `/system_ext`, `/product`, `/vendor`, `/odm`, `/mi_ext` | C2: any modified APK was accepted as validly signed |
| `/system/framework/services.jar` | 16 package-manager methods restored from the Xiaomi 17 reference (signature compare, downgrade check, permission signature match, key-set checks, minimum signature scheme, install-time verifier hooks) | C2 |
| `/system/priv-app/Telecom/Telecom.apk` | `isCurrentCommunicationDevice` re-reads the real device | Loudspeaker button sometimes does nothing |
| removed | `/system/framework/oat/arm64/services.{odex,vdex,art}` (+ `.fsv_meta`) | Stale precompiled code of the old jar, would be rejected at every boot |
Evidence and tools: `docs/hardware/AUDIT_STATUS.md` (C2), `docs/ROM_PHASE2_CHANGES.md` (E, F), `docs/hardware/subsystems/CALL_SPEAKER_BUG.md`. Rebuild with `tools/re/fix_framework_signatures.py`, `fix_services_signatures.py`, `fix_telecom_speaker.py`. The patched `services.jar` needs the patched `framework.jar` (always flashed together; they are one image).

## Build (done offline)
Base = the image on the phone: `secure_build/out_tele_T20261030_v13/system.img` (checked: byte for byte equal to the running partition, sha256 `a66cc607...`).
`W=<workdir> PARTS=system PAYLOAD=secure_build/payload_sigfix OUT=secure_build/out_sigfix bash secure_build/build_tele.sh` with the base mounted at `$W/port/system`. Checks that must pass: `verify_img` errors 0, `erofs_symlink_check` crossing 0, `privcheck` unchanged. Result in `secure_build/out_sigfix/` (git-ignored; regenerate with the tools).

**Built 2026-10-31 (nothing flashed):** `secure_build/out_sigfix/system.img`, 905,007,104 bytes, sha256 `bcd19ccddcbf6a8815515536edb23e1ca960dbe6eee143cc53b0f84fe23a60ca` (build 60 s). Checks: `verify_img` errors 0, unlabeled 0, `erofs_symlink_check` crossing block boundary 0. Independent comparison of the finished image with the base: 4,203 entries become 4,197; exactly 3 files replaced (`framework.jar`, `services.jar`, `Telecom.apk`, content equals the patched payload, owner, mode and SELinux label `u:object_r:system_file:s0` unchanged), exactly 6 removed (stale `services` odex, vdex, art and their `.fsv_meta`), none added. The phone's current jars were checked equal to the base image's. Flash script: `secure_build/flash_system_nowipe.sh` (modelled on the proven product one; checks the checksum, flashes only `system`, no erase).

## RESULT of the first flash (2026-10-31 20:53): did NOT boot, rolled back at 21:07
`out_sigfix/system.img` (all three fixes together) was flashed no-wipe. The phone never came up on adb for 12 minutes and then dropped into the bootloader (slot A: `slot-successful` yes, retry count down to 2, `is-userspace` no), so the boot failed early, before `adbd`. No log of the failed boot exists (no pstore, adb never appeared). Rollback with `flash_system_nowipe.sh out_tele_T20261030_v13` worked: boot completed in about 1 min, the system partition hash is back to `a66cc607...`, SELinux enforcing, user data untouched.
Cause: **unknown**. Candidates, not tested: (1) the system image carries fs-verity metadata (`*.fsv_meta`) per file, and the three replaced files kept their old `.fsv_meta`; (2) dex version 040 written by smali in the boot-classpath `framework.jar` (the original is 039); (3) the old boot image and odrefresh artifacts on `/data` built against the old `framework.jar`; (4) a fix that really broke a boot-critical app (the exemption path check or an unexpected signature use). The two-file and one-file variants were not tried separately.
**Next step proposal:** bisect, one flash each with rollback ready: (a) `Telecom.apk` alone (also delivers the speaker fix; low risk), (b) `framework.jar` alone with dex version 039 and matching `.fsv_meta` handling, (c) `services.jar`. Before that, check how `*.fsv_meta` is used at boot, and try to capture an early log (kernel console is not available; consider `logcat` over adb at the first moment, or a debug `init` log).

## Before the flash (owner)
1. USB cable and port checked (the link drops on long transfers); battery above 50 %.
2. Camera shots and PhotoStage verdict finished: this flash makes the first boot slow and resets nothing, but it is a good moment to have everything pulled.
3. **Done (2026-10-31, read-only):** installed apps audited for the new rules. All 99 user apps (326 APK files) and all 28 system apps updated through the Play Store (75 files, including Play Services, Dialer, Contacts, WebView, PhotoStage) pass real signature verification, and each base APK's certificate equals the one stored in `packages.xml`. So the fix will not remove or refuse any installed app on signature grounds (Android deletes apps under `/data/app` that fail verification at boot, which would otherwise have been the danger). Tools: `tools/re/verify_installed_apps_drive.py` and `verify_installed_apps_compare.py`. Preinstalled system apps were checked separately (12 modified ones rely on the system-partition exemption).
4. Owner says go. Rollback ready: `bash secure_build/flash_system_nowipe.sh secure_build/out_tele_T20261030_v13 "rollback"` (about 2 min, reboots into the old system; needs fastbootd, the old image is byte-identical to what runs today).

## Flash
`bash secure_build/flash_system_nowipe.sh secure_build/out_sigfix "signature + speaker fix"` (reboots to fastbootd, flashes `system`, reboots; checks the checksum first). Expect a long first boot (the boot image and system-server code are rebuilt on `/data` by odrefresh: several minutes, the screen may stay on the logo).
If the logo stays beyond 15 minutes: hold power 15 s, enter fastbootd (Vol Down + Power), run the rollback command above.

## Tests after the flash
| # | Test | Pass |
|---|---|---|
| 1 | Boot to home screen; `getprop sys.boot_completed` 1; SELinux enforcing; crash buffer 0 | all |
| 2 | `dumpsys package` lists the 12 modified apps (SystemUI, Settings, PowerKeeper, Joyose, SystemUIPlugin, Phonesky, HTMLViewer, five overlays) as installed and enabled | all present |
| 3 | `tools/privcheck.py`: priv-apps, 0 missing | unchanged |
| 4 | A test APK with a **broken signature** (modified after signing): `pm install` | refused with a signature error |
| 5 | The same APK signed with another key over an installed test app | refused (`INSTALL_FAILED_UPDATE_INCOMPATIBLE`) |
| 6 | A normally signed app installs and updates; Play Store updates itself; GMS updates | works |
| 7 | Camera (native) opens, takes a photo and a video, Gallery opens it; PhotoStage runs | works, no permission denials in the log |
| 8 | Call: SIM 1 and SIM 2 outgoing and incoming, voice both ways | works |
| 9 | Speaker bug: make a WhatsApp call on speaker, end it, make a phone call, tap Speaker | sound from the loudspeaker |
| 10 | Wi-Fi, Bluetooth audio, GPS fix outside, charging, mobile data | unchanged |
| 11 | Installing a sideloaded app: how long the install-time verifier check takes | under a few seconds |
| 12 | `logcat` for `PackageManager` signature, `Telecom`, `installd` errors in the first hour | none new |
Results go into `ROM_HISTORY.md` and `docs/hardware/AUDIT_STATUS.md` (C2 becomes Fixed only after tests 4 to 6 pass).

## If a preinstalled app is refused after the flash
Most likely cause: an app that was modified after signing and sits outside the six exempt partitions, or a signature permission between apps with different certificates (the camera is signed with a debug key). The log line names the package. Remedy options: roll back, or add that path/package to the exemption list in `com.xBuild.isSystemPath` and rebuild.
