# Security Assessment: POCO F4 (munch) running a third-party HyperOS 4 / Android 17 port

- **Assessment date:** 2026-10-23
- **Scope:** Authorized assessment requested by the device owner. PC-side, read-only static analysis of the ROM images, plus live-device facts collected earlier (cited as "LIVE").
- **Constraints:** No adb or device interaction in this phase. No exploitation. No existing files were modified.
- **Author role:** Android device security review

---

## 1. Device identification

| Item | Value | Source |
|---|---|---|
| Device | Xiaomi POCO F4 5G, codename `munch`, Snapdragon 870 (SM8250-AC), 8 GB / 256 GB | owner |
| ROM | Third-party port, HyperOS 4 / Android 17 beta, OS4.0.0.24 | LIVE, `system/build.prop` |
| Reference ROM | Official munch Global HyperOS 1.0.9 (EROFS, MD5-verified) | `stock_rom_1.0.9/images/` |
| Kernel | `4.19.325-zyndong-perf-g7e817c4ca270`, built with "ZyC clang 16.0.6" on a CI runner, 2026-09-10; KernelSU (ReSukiSU) + SUSFS built in | `boot.img` strings |
| Bootloader | Unlocked (`unlocked:yes`, verifiedbootstate **orange**) | LIVE |
| AVB | `vbmeta.img` flags=**2** (VERIFICATION_DISABLED), rollback_index 0. `vbmeta_system.img` flags=0, rollback_index 1740787200 | parsed header |
| Firmware | xbl/tz/hyp/keymaster etc. are genuine Xiaomi/Qualcomm-signed, dated Mar-Apr 2025 | LIVE + earlier analysis |
| Security patch | Vendor **2025-04-01**. System claims 2026-08-01 (port beta, not independently verifiable) | `build.prop` |
| SELinux | Enforcing (with permissive domains, see M3) | LIVE + `vendor_sepolicy.cil` |
| Platform signing key | Same as stock: `C9:00:9D:01:...:90:25` (Xiaomi platform cert, reused) | `apk_cert.py` on both `framework-res.apk` |
| Hardware note | Fingerprint sensor has a physically cut flex cable and the HAL crash-loops. This is hardware damage, not a software issue. | LIVE |

---

## 2. Method

1. Diffed official vs port vendor `fstab.qcom` and `build.prop` (`audit/vendor_diff/`). Diffed the vendor manifests (`audit/manifests/*.tsv`) by hash to find changed security files.
2. Extracted single files from the port ext4 images with `7z e -so` and from EROFS images with `dump.erofs --cat`. No partition was extracted in full.
3. Disassembled `framework.jar` and `services.jar` (port and stock) with SDK `dexdump -d`. Then:
   - located the KaoriosHook call sites;
   - compared the bodies of signature- and downgrade-check methods against stock.
4. Kaorios strings were obfuscated (bitwise-NOT of each UTF-16 code unit). I decoded them with a small offline script.
5. Dumped manifests and permissions of the mod APKs with `aapt2 dump badging/xmltree`. Extracted network endpoints with `strings`.
6. Compared the init `.rc` sets (port vs stock) and listed every service that runs as root. Read the new or changed services.
7. Listed file modes in all five port ext4 images (`7z l -slt`) to look for setuid/setgid and world-writable files.
8. Diffed official vs port `vendor_sepolicy.cil`, `init.qcom.rc` and `vendor_property_contexts`. Disassembled the new vendor binary with NDK `llvm-objdump`.
9. Parsed the AVB headers of `vbmeta*.img` and read the `boot.img`/`vendor_boot.img` strings.

---

## 3. Findings summary (ranked)

| ID | Severity | Finding | Status | Stock behaviour |
|---|---|---|---|---|
| C1 | **Critical** | User data not encrypted: FBE and metadata encryption removed from fstab, while `ro.crypto.state=encrypted` is spoofed | Verified (files + LIVE) | FBE aes-256-xts + metadata encryption, wrapped keys |
| C2 | **Critical** | Framework-level signature-verification and downgrade bypass ("CorePatch" baked into `services.jar`/`framework.jar`) | **Verified, new** | Full signature and downgrade enforcement |
| C3 | **Critical** | Unlocked bootloader with AVB verification disabled (vbmeta flags=2, `avb=` removed from every fstab entry), hidden behind spoofed "locked/green" properties | Verified | Locked, AVB enforced, green |
| H1 | **High** | Kaorios hook injected into every app process: replaces key-attestation chains with a keybox downloaded from a third-party server, can generate software keys in place of hardware-backed keys, and hides developer/ADB status and installed apps from apps | Verified (code/strings). Exact per-app scope depends on runtime settings (unverified) | Not present. Keystore attestation is genuine |
| H2 | **High** | Kernel-level root (KernelSU + SUSFS hiding) built into the kernel. Root manager installed. KSU modules add SELinux allow rules | Verified (boot.img + LIVE) | No root. Stock kernel |
| H3 | **High** | Privileged-permission allowlist disabled (`ro.control_privapp_permissions=disable`), and the privileged set includes third-party, testkey-signed and debug-signed apps | Verified | `enforce`. All Xiaomi/Google-signed |
| H4 | **High** | Outdated patch base: vendor/firmware SPL 2025-04-01. Kernel 4.19 is upstream end-of-life (4.19.325 is the final release) | Verified | Same vendor SPL (munch is end of life), but stock does not claim a 2026 patch level |
| M1 | Medium | FRP (Factory Reset Protection) partition pointer removed (`#ro.frp.pst=`) | Verified in file. Runtime effect unverified | FRP active |
| M2 | Medium | Porter's "license" kill-switch: new root service `vendor_security` (`/vendor/bin/show_alert_native`, seclabel `vendor_init`) polls a watermark and reboots to the bootloader if it is missing | **Verified, new** | Not present |
| M3 | Medium | New permissive SELinux domains `hal_ir_default` and `hal_vibrator_default` in the vendor policy, plus KSU-module allow rules | **Verified, new** (vendor). KSU rules from LIVE | No permissive domains |
| M4 | Medium | Spoofed device-integrity properties (bootloader, verified boot, warranty, encryption, `ro.is_ever_orange=0`) mislead the user, MDM and app risk engines | Verified | Real values |
| M5 | Medium | USB debugging enabled (for this assessment), and Kaorios hides `adb_enabled` / `development_settings_enabled` from apps | LIVE + code | Off by default, visible to apps |
| L1 | Low | Third-party apps preinstalled as system: Via browser, ViPER4Android (Firebase/ads SDKs), xiaomi.eu ext (`WRITE_SECURE_SETTINGS`), Xposed modules with no framework | Verified | Not present |
| L2 | Low | `/vendor/bin/bootctl` shell script runs `bootctl mark-boot-successful` 15 s after boot, outside `update_verifier` | Verified | update_verifier marks the slot only after dm-verity checks |
| L3 | Low | China-variant vendor daemons added: `slad`/SLA (with `net_admin`/`net_raw` caps and a `sla.ko` module), rongcard eID HAL, otrpagent | Verified present. Function unverified | Absent on Global |
| I1 | Info | `su_daemon` service (`/system/xbin/su --daemon`) is declared in `init.miui.ext.rc`, but no `su` binary exists. Inherited from stock, so inert | Verified | Same declaration in stock |
| I2 | Info | No setuid/setgid or world-writable files in system, system_ext, product, odm or mi_ext. `zygote_next` is AOSP. Firmware is genuine. Platform key is unchanged from stock | Verified | — |

---

## 4. Finding details

### C1. User data stored unencrypted (Critical)

**Evidence**
- In `audit/vendor_diff/off_etc_fstab.qcom` vs `port_etc_fstab.qcom`, the official `/data` line had:
  `inlinecrypt ... fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized+wrappedkey_v0,metadata_encryption=aes-256-xts:wrappedkey_v0,keydirectory=/metadata/vold/metadata_encryption`.
  The port line has none of these. `/metadata` also lost `wrappedkey`. SD-card `encryptable=footer` was removed too.
- Port `system/build.prop` sets `ro.crypto.state=encrypted` three times (lines 338, 392, and in the "# Spoofing" block).
- LIVE: `/data` is a raw mount of `/dev/block/sda34`, and `/data/misc/vold/user_keys` does not exist.

**Impact**
- Every file on `/data` is in plaintext on the UFS: messages, photos, app tokens, Wi-Fi keys, and Kaorios's keybox in the settings DB.
- The lock-screen PIN or password protects nothing at rest. Keymaster/TEE key binding is never used for storage.
- Apps and MDM that check the encryption state are told the device is encrypted.

**Scenario:** someone who finds or steals the phone boots any image through the unlocked bootloader (or uses a recovery) and copies all user data without knowing the PIN.

**Stock behaviour:** FBE v2 with hardware-wrapped keys plus metadata encryption. Data is unreadable before the first unlock.

### C2. Signature-verification and downgrade bypass in framework (Critical, new)

**Evidence:** `dexdump` of the port `services.jar` (classes3.dex) and `framework.jar` (classes.dex), compared with stock 1.0.9.

| Method | Port body | Stock size |
|---|---|---|
| `PackageManagerServiceUtils.verifySignatures(...)Z` | `const/4 v0,1; return` (2 units) | 303 units |
| `PackageManagerServiceUtils.compareSignatures(SigningDetails,SigningDetails)I` | returns 0 (= `SIGNATURE_MATCH`) | 78 units (array variant) |
| `PackageManagerServiceUtils.checkDowngrade(...)` (3 overloads) | `return-void` | 213 units |
| `PackageManagerServiceUtils.isDowngradePermitted(IZ)Z` | returns true | 33 units |
| `InstallPackageHelper.doesSignatureMatchForPermissions(...)Z` | returns true | 106 units |
| `SigningDetails.checkCapability(SigningDetails,I)` / `(String,I)` / `checkCapabilityRecover` / `hasAncestorOrSelf` | return true | 27 / 41 / – / 27 units |
| `PackageParser$SigningDetails.checkCapability` (both) | return true | — |

**Impact**
- Android's app-identity model is gone. An APK signed with any key can be installed as an "update" over any existing app, including privileged or platform apps (GMS, Phonesky, Settings providers, the package installer, banking apps).
- The new APK inherits the original app's data directory, its granted runtime permissions, and any signature-level permissions it declares or uses.
- Downgrades to older, vulnerable versions are always allowed.
- C1 and H3 make this worse: the replaced app can be a privileged app whose permissions are no longer allowlisted.

**Scenario:** a malicious APK, sideloaded or pushed by any app holding `INSTALL_PACKAGES` (Kaorios, InstallerX, xiaomi.eu ext via settings), is installed as an update to an existing banking or messaging app and reads that app's stored session data.

**Note:** the strings "CorePatch" and "disableVerification" do not appear (only AOSP's `disableVerificationForUid`). The patch is applied directly to the method bodies.

**Stock behaviour:** full signature matching, key rotation (lineage) checks and downgrade blocking.

### C3. Verified boot disabled and lock state spoofed (Critical)

**Evidence**
- `rom_extract/images/vbmeta.img`: AVB magic present, flags=2 (`AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED`).
- Port fstab: `avb=vbmeta_system`, `avb`, `avb=vbmeta` and `avb_keys=...gsi...` were removed from system, system_ext, product, vendor, odm and mi_ext.
- LIVE: `unlocked:yes`, state orange.
- Port `system/build.prop` "# Spoofing" block (lines 390-409):
  `ro.secureboot.lockstate=locked`, `ro.boot.flash.locked=1`, `ro.boot.vbmeta.device_state=locked`, `(vendor.)ro.boot.verifiedbootstate=green`, `ro.boot.veritymode=enforcing`, `ro.boot.warranty_bit=0` (and three variants), `ro.is_ever_orange=0`, `ro.secureboot.devicelock=1`.

**Impact:** nothing checks the integrity of boot, vendor or system. A person with brief physical access can persistently change any partition, for example adding a hidden implant to the kernel or system. The device would still report "locked/green", and the user would not see it.

**Scenario:** an evil-maid attacker flashes a modified boot image over fastboot in under a minute. It survives reboots and is not detected.

**Stock behaviour:** locked bootloader, AVB chain enforced with dm-verity, and the boot-state reported honestly through the TEE.

### H1. Kaorios framework hook: attestation spoofing, software keys, anti-detection (High)

**Evidence** (port `framework.jar`, classes7.dex `android.security.kaorios.*` and `com.kousei.framework.*`, with a bundled BouncyCastle). KaoriosHook call sites:

| Hooked AOSP method | Kaorios method |
|---|---|
| `Instrumentation.newApplication` | `initContext` (runs in every app process) |
| `ApplicationPackageManager.hasSystemFeature` | `hasSystemFeature` (Pixel feature spoofing) |
| `Settings.{System,Secure,Global,Config}.get*` | hides `adb_enabled` / `development_settings_enabled` from apps |
| Keystore attestation path | replaces the certificate chain with a keybox fetched from a third-party server |

**Impact**
- Banking, payment and DRM apps receive a forged "hardware-backed, locked, genuine" attestation. Their risk engines cannot see the real device state (C3, H2).
- If the downloaded keybox is revoked or malicious, apps may fail, or keys may silently become software keys.
- A third-party server controls code-signing-like material that runs in every app process.

**Scenario:** the keybox server is compromised or changes owner; every device using this port then trusts an attacker-supplied attestation chain.

**Stock behaviour:** not present. Attestation comes from the device's own TEE key.

### H2. Kernel root with hiding (High)
- **Evidence:**
  - Kernel `4.19.325-zyndong-perf` contains KernelSU (ReSukiSU) and SUSFS.
  - LIVE: the manager is installed and root is granted to `shell` for this assessment.
  - KSU modules add their own SELinux allow rules (Section 6).
- **Impact:** any app the user grants root can do anything, and SUSFS can hide it from detection.
- **Stock behaviour:** no root.

### H3. Privileged-permission allowlist disabled (High)
- **Evidence:**
  - Product `ro.control_privapp_permissions=disable`, system_ext `log` (official HyperOS 4: `enforce`).
  - Privileged apps include InstallerX (replaces the package installer), Gboard re-signed with the AOSP test key, and the debug-signed camera.
- **Impact:** any APK in a privileged directory gets every privileged permission it asks for. With C2, a privileged app can be replaced by an update signed with any key.

### H4. Outdated security patch base (High)
- **Evidence:**
  - LIVE `ro.vendor.build.security_patch=2025-04-01`; `ro.build.version.security_patch=2026-08-01` (system only).
  - Kernel 4.19 is upstream end-of-life.
- **Impact:** vendor, firmware and kernel vulnerabilities fixed after April 2025 stay open. The 2026 system date covers only the Android framework layer.
- **Stock behaviour:** munch is also end of life on stock. The last official vendor patch is the same.

### M1. FRP disabled (Medium)
- **Evidence:** the `#ro.frp.pst=` line is commented out in the vendor build.prop. LIVE: `ro.frp.pst` is empty, although the `frp` partition (`/dev/block/sda9`) exists.
- **Impact:** after a factory reset, a thief does not need the owner's Google account.

### M2. Porter's reboot kill-switch `vendor_security` (Medium)
- **Evidence:**
  - Vendor `init.qcom.rc` runs `service vendor_security /vendor/bin/show_alert_native`, as root with `seclabel u:r:vendor_init:s0`, on `sys.boot_completed=1`.
  - The binary (6,888 bytes, NDK r29 build, RUNPATH pointing at a Termux path) reads `/system/usr/keylayout/zyn_f4`. If the file does not contain `ZYN_HOS4_2026`, it sets `sys.powerctl=reboot,bootloader`.
  - The service is not `oneshot`, so init restarts it in a loop (LIVE: 20 starts in 3 minutes).
- **Impact:** a hidden root-level reboot trigger. Changing the system partition, even in an unrelated way, can leave the phone looping into fastboot.
- **Status:** still running. A fix to stop it after boot was prepared, but the assessment tooling's permission policy blocked it. **Do not delete or edit `zyn_f4`.**

### M3. Permissive SELinux domains (Medium)
- **Evidence:** LIVE `/vendor/etc/selinux/vendor_sepolicy.cil` contains `(typepermissive hal_vibrator_default)` and `(typepermissive hal_ir_default)`. Neither appears in official vendor policy.
- **Impact:** the vibrator and IR HAL processes are not confined by SELinux. A bug in either becomes a wider foothold. The risk is limited because both are small HALs.

### M4. Spoofed integrity properties (Medium)
See C3. In addition, `ro.crypto.state=encrypted` (C1) and `ro.mi.os.version.beta=true` with `publish=false`. MDM, banking and anti-fraud checks are told the opposite of the truth.

### M5. USB debugging enabled and hidden (Medium)
LIVE `adb_enabled=1` (needed for this assessment). Kaorios hides it from apps (H1). **Action:** turn it off when the work is finished.

### L1. Third-party apps preinstalled as system (Low)
Via browser, ViPER4Android (Firebase and ads SDKs), xiaomi.eu ext (`WRITE_SECURE_SETTINGS`), and KaoriosToolbox. Each one can be uninstalled or disabled.

### L2. Boot marked successful by a script (Low)
The port's `/vendor/bin/bootctl` script, and this session's `bd_region` module, run `bootctl mark-boot-successful` without dm-verity checks. Without them the port falls into fastboot after 7 boots, because it never marks a boot successful itself. This is acceptable given C3, but it removes A/B automatic rollback.

### L3. China-variant vendor daemons (Low)
`slad` (SLA, with `net_admin`/`net_raw` capabilities and `sla.ko`), the rongcard eID HAL and `otrpagent` are present. They are normal on CN builds and absent on Global.

### Additional findings from the live session (2026-10-23)

| ID | Severity | Finding | Status |
|---|---|---|---|
| A1 | Low | The K90 donor's `traced.relay_producer_port=vsock://-1:2010` crash-looped `traced` (71 restarts in 7 minutes) | **Fixed** (prop removed at boot) |
| A2 | Low | `ATFWD-daemon` was killed by its old seccomp policy (missing `gettid`), 26 restarts | **Fixed** (policy bind mount with added syscalls) |
| A3 | Info | The dead fingerprint sensor caused a system_server ↔ hwservicemanager retry loop (~1.3 CPU cores) | **Fixed** (feature hidden until the hardware is repaired) |
| A4 | Info | The port adds a virtual fingerprint HAL APEX (`com.android.hardware.biometrics.fingerprint.virtual`) | Inactive (no virtual sensor configured) |

---

## 5. Remediation roadmap

| Priority | Action | Fixes | Needs |
|---|---|---|---|
| 1 | Turn off USB debugging and revoke Shell root when the work ends | M5, part of H2 | Settings, ReSukiSU manager |
| 2 | Disable Kaorios (`persist.sys.kaorios`) if you don't use apps that need forged attestation | H1 | One module, reboot |
| 3 | Set the privileged-permission allowlist back to `enforce` (log first, then enforce) | H3 | Module plus a per-app allowlist check |
| 4 | Remove third-party system apps you don't use (Via, ViPER, xiaomi.eu ext, KaoriosToolbox) | L1 | Uninstall |
| 5 | **Restore /data encryption (FBE + metadata)**: rebuild the vendor fstab from official, then format data | **C1** | Vendor image rebuild + **full wipe** (deferred by owner) |
| 6 | Restore FRP (`ro.frp.pst=/dev/block/bootdevice/by-name/frp`) | M1 | Vendor rebuild (can be combined with 5) |
| 7 | Remove `vendor_security` from `init.qcom.rc` | M2 | Vendor rebuild (with 5) |
| 8 | A signature/downgrade bypass (C2) and AVB-off (C3) are inherent to this port. The only full fix is an official ROM with the bootloader re-locked | C2, C3 | Owner decision (rejected: owner wants the newest OS) |

Residual risk with items 1–4 done: **high**. Data at rest is still unencrypted (C1), and boot integrity is unchecked (C3). Keep the phone physically secure and don't keep high-value secrets (banking OTP, password vault) on it until C1 is fixed.

---

## 6. Changes made during this engagement (all reversible KernelSU modules)

| Module | Purpose | Security effect |
|---|---|---|
| `bd_region` | BD region, marks boot successful | Neutral (L2) |
| `finddevice_priv` | Xiaomi Find Device as priv-app + 6 sepolicy allow rules for `hal_mtdservice` | Adds anti-theft. Rules are narrow |
| `port_fixes` | 17 sepolicy allow rules (perf HAL, system_suspend, micharge, dpmtcm) | Narrow allow rules, no new permissive domains |
| `camera_tune` | Official camera configs and tuning (bind mounts) | Neutral |
| `hw_optimize` | Official thermal, Doze, timers, munch.xml, Wi-Fi config, audio, crash-loop fixes | Neutral to positive (A1–A3) |
| `hyperai_k90` | Official Xiaomi-signed HyperOS 4 AI apps (China) | Adds Xiaomi CN cloud services; more data sent to Xiaomi CN servers |
| `com.munch.brightness.overlay` | Official brightness values (user-installed RRO) | Neutral |

Identifiers (serial numbers, IMEIs, tokens) are intentionally left out of this report.
