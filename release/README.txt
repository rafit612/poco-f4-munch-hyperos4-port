HyperOS 4 / Android 17 for POCO F4 5G (munch) - release T20261026
=====================================================================

ONLY FOR POCO F4 5G (munch: models 22021211RG, 22021211RI, 22021211RC). AT YOUR OWN RISK.
Unofficial; not affiliated with Xiaomi, POCO or Google. A clean install ERASES ALL DATA.

Contents
  images/            28 partition images (firmware, kernel, vbmeta, system images)
  SHA256SUMS         checksums of every image (the scripts check them before flashing)
  flash_linux.sh     installer for Linux / macOS
  flash_windows.bat  installer for Windows

Install (bootloader must be unlocked, phone in fastboot mode: Power + Volume down)
  Linux/macOS:  bash flash_linux.sh          (clean install, erases data)
                bash flash_linux.sh update   (update from an earlier release of this ROM, keeps data)
  Windows:      flash_windows.bat            /  flash_windows.bat update

First boot takes 3-5 minutes.

Full guide, screenshots, features, limits and source:
  https://github.com/rafit612/poco-f4-munch-hyperos4-port
  (INSTALL.md: bootloader unlock, platform-tools, troubleshooting, Google Play Protect registration)
