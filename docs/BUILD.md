# Building and patching the images

Everything here runs on Linux (tested on Ubuntu 26.04, x86-64) with Python 3, `fusermount`, Android build-tools
(`aapt2`, `zipalign`, `apksigner`) and platform-tools. Read [`../AGENTS.md`](../AGENTS.md) first: it lists the
rules that come from real failures.

## How the images are made

No source is compiled. Each partition image is the base image plus a payload:

```
base image (EROFS)  ──mount──►  tools/erofs_tar_rebuild.py  ──►  tar  ──►  mkfs.erofs (patched)  ──►  new image
                                   + secure_build/payload_tele/<part>/        (add / replace files)
                                   − secure_build/payload_tele/<part>.remove   (drop paths)
```

- `payload_tele/<part>/…` — files to add or replace, at their path inside the partition. Every file has a
  `<file>.meta` with `uid gid mode selinux-label` (example: `0 0 644 u:object_r:system_file:s0`).
- `payload_tele/<part>.remove` — one partition-relative path per line (`#` comments); the path and everything under it
  is dropped.
- `secure_build/payload_plus/` — the earlier layer that produced the base images.
- Checks after every image: `tools/verify_img.py` (payload byte-identical, removals gone, labels kept — must end in
  `errors 0`) and `tools/erofs_symlink_check.py` (must print `crossing block boundary 0`).

## Rebuild a partition

```sh
# 1. Mount the base images (read-only, FUSE) under a work dir:  $W/port/<partition>
W=$HOME/romwork; mkdir -p $W/port/system
tools/erofs/root/usr/bin/erofsfuse <base>/system.img $W/port/system

# 2. Build (writes secure_build/out_tele/<part>.img and SHA256SUMS)
W=$W PARTS="system" bash secure_build/build_tele.sh
```

`build_tele.sh` uses the patched `tools/erofs/munch/mkfs.erofs` (erofs-utils 1.9.1 + `tools/erofs_patch/`; build
steps in `tools/erofs_patch/BUILD.txt`). Stock mkfs.erofs 1.9.1 must not be used for this kernel.

To build a patch on top of a release, mount the **release** images as the base and put only your change in the
payload (or a copy of `payload_tele` holding just your files).

## Typical changes

| Change | Where | Notes |
|---|---|---|
| A build property | `payload_tele/<part>/…/build.prop` | `product` overrides `vendor` on this phone; bump `ro.build.fingerprint`'s release tag in `product/etc/build.prop` every release (carrier config cache) |
| A resource value of a system app (bool, string, integer, array) | new static RRO in `product/overlay/` | Examples: `port_fixes/volte_overlay/build.sh`, `port_fixes/apn_overlay/`. Do not replace whole XML pages with an RRO |
| A row in a Settings page | `tools/axml.py set-attr` / `add-pref` on the APK's binary XML | Settings.apk in this port is already re-signed; `zipalign -p 4` afterwards |
| A new boot-time service | `product/etc/init/*.rc` + its own SELinux domain in `product/etc/selinux/product_sepolicy.cil`, label in `product_file_contexts`, new `product_sepolicy_and_mapping.sha256` | Compile the full policy offline with `secilc -N` (plat + mapping 30.0 + vendor) before flashing; `;;*` is not a comment in CIL |
| A system app from another ROM | `payload_tele/<part>/(priv-)app/…` + privapp XML | Check its framework classes exist here, run `tools/privcheck.py`, then test the actual function |
| Carrier config / APNs | `port_fixes/volte_overlay/` (generators + `build.sh`), `port_fixes/apn_merge/merge_apns.py` | Inputs from Xiaomi 17 Global in `global_inputs/` |

## Shipping a release or a patch

1. Build the changed partitions, check `errors 0` and `crossing block boundary 0`.
2. Flash on a test phone (`flash_linux.sh update` from a release folder, or `fastboot flash <part> <img>` in fastbootd),
   boot, and test what you changed — plus a phone call, sound and mobile data.
3. Assemble the release folder: `images/` (firmware + kernel images from the previous release, new system images),
   `SHA256SUMS` (`cd images && sha256sum *.img > ../SHA256SUMS`), `release/flash_linux.sh`, `release/flash_windows.bat`,
   `release/README.txt`.
4. A patch release may contain only the changed system images; say "update (no wipe)" in the release notes.

## Using Codex, Claude Code or another AI agent

Point the agent at this repository; `AGENTS.md` (Codex) and `CLAUDE.md` (Claude Code) are read automatically and
contain the build and safety rules. Keep the phone's flashing and wiping decisions with a human: ask the agent to
investigate and propose, then approve each flash.
