# Notes for AI coding agents (Codex, Claude Code, others)

This repo builds an unofficial HyperOS 4 / Android 17 ROM for one device: **POCO F4 5G, codename `munch`**
(Snapdragon 870, kona). A mistake here can leave a phone unbootable. Work in this order: investigate, compare with
a reference ROM, explain, then change. Never flash, wipe or push to a phone without the owner saying so.

## Layout
- `secure_build/payload_tele/<partition>/` — files layered onto the base images; `<partition>.remove` lists paths to
  drop (one per line, `#` comments). `*.meta` = `uid gid mode selinux-label` for each added file.
- `secure_build/payload_plus/` — the earlier layer the base images (`out_sunday_plus`) were built from.
- `secure_build/build_tele.sh` — rebuilds images: `W=<work dir with port/<part> mounts> PARTS="system product" bash secure_build/build_tele.sh`.
- `tools/` — `erofs_tar_rebuild.py`, `verify_img.py`, `erofs_symlink_check.py`, `privcheck.py`, `axml.py`, …
- `port_fixes/` — sources of the overlays and generated XML (VoLTE/carrier config, APN, sound trigger).
- `release/` — install scripts that go into the download zip.
- `ROM_HISTORY.md` — every change with its reason; read it before changing anything.

## Rules that come from real failures
1. **EROFS images:** build only with the patched `tools/erofs/munch/mkfs.erofs` (`-E noinline_data`; patch in
   `tools/erofs_patch/`). Stock mkfs.erofs 1.9.1 creates symlinks the 4.19 kernel cannot read. Every image must
   report `errors 0` (verify_img) and `crossing block boundary 0` (erofs_symlink_check).
2. **SELinux:** the phone compiles its policy at boot. Any change to `product_sepolicy.cil` needs a new
   `product_sepolicy_and_mapping.sha256` and an offline `secilc -N` compile against plat + mapping 30.0 + vendor
   before flashing. In CIL, `;;*` is a directive, not a comment — use `;`.
3. **System apps from another ROM:** check that every framework class the app uses exists in this port's
   framework (the Xiaomi 17 TeleService needed `ConnectionService$VendorExt` and broke every call). Run
   `tools/privcheck.py` (privapp allowlist is enforced; a gap stops boot). Then test the real function (place a call).
4. **Overlays (RRO):** fine for values (bool, string, integer, arrays). Never replace a whole app XML page with an
   RRO: the page's own resource references resolve against the overlay and show raw IDs.
5. **Boot image:** `/system` carries no ART boot image on purpose (the port's was stale); odrefresh builds it on
   /data at first boot.
6. **Audio DSP:** do not re-add Google's hotword engines to `sound_trigger_platform_info.xml`; with this kernel they
   crash the audio DSP (no sound at all).
7. **Telephony:** change `ro.build.fingerprint` (release tag) in `product/etc/build.prop` for each release, or carrier
   config stays cached.
8. Keep `ro.control_privapp_permissions=enforce`, SELinux enforcing, encryption, and no pre-authorised `adb_keys`.

## Keep the documents current
After every piece of work, in the same change: update the markdown files it touches (the subsystem page, `docs/ROM_OPTIMIZATION_PLAN.md` status, `ROM_HISTORY.md` for anything that changes the phone or the build, `docs/hardware/AUDIT_STATUS.md` for corrected facts, camera pages for camera work) and the graph copy in `docs/rom_map/corpus`. Say plainly what was checked and what was not.

## Recovery
If a flashed image does not boot: in fastbootd (`fastboot reboot fastboot` from the bootloader) flash the previous
image of that partition, e.g. `fastboot flash vendor <previous vendor.img>`.
