**Unofficial HyperOS 4 (OS4.0.0.24) / Android 17 for the POCO F4 5G (`munch`) only — at your own risk.**
A clean install erases all data and needs an unlocked bootloader. Not affiliated with Xiaomi, POCO or Google.

### Download
All three parts + `SHA256SUMS.txt`. Join them, check the zip, unzip, run the installer — step by step in
[INSTALL.md](https://github.com/rafit612/poco-f4-munch-hyperos4-port/blob/main/INSTALL.md).

| | |
|---|---|
| Linux / macOS join | `cat POCO-F4-munch-HyperOS4-A17-T20261026.zip.0* > POCO-F4-munch-HyperOS4-A17-T20261026.zip` |
| Windows join | `copy /b POCO-F4-munch-HyperOS4-A17-T20261026.zip.001+POCO-F4-munch-HyperOS4-A17-T20261026.zip.002+POCO-F4-munch-HyperOS4-A17-T20261026.zip.003 POCO-F4-munch-HyperOS4-A17-T20261026.zip` — or open `.zip.001` with 7-Zip |
| Zip SHA-256 | `eff467241d416db1b8159f4a15871a3afb9bebbb9bda61ed19513ecdf96774c9` |
| Install (clean) | `bash flash_linux.sh` · `flash_windows.bat` (phone in fastboot mode) |
| macOS | `brew install coreutils`, then `PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH" bash flash_linux.sh` |
| New to this? | [Beginner's guide](https://github.com/rafit612/poco-f4-munch-hyperos4-port/blob/main/docs/BEGINNER_GUIDE.md) (step by step, Bangla summary) |

### Contents
Final official munch firmware, port kernel `4.19.325-zyndong-perf`, official POCO F4 HyperOS 1.0.9 hardware layer,
HyperOS 4 system with the Xiaomi 17 Global layer. 28 images, checked by the installer (SHA-256) before flashing;
the installer refuses phones that are not `munch` and locked bootloaders.

### Highlights
- Global setup and apps, Xiaomi HyperAI (Gemini, AI Interpreter for calls, AI Subtitles), Circle to Search, Updater.
- Network type, VoLTE, video calling and Wi-Fi calling for every operator with a Xiaomi profile (~118 countries); full APN list.
- Official camera tuning for all four sensors + GCam LMC 8.4 with 13 configs; official audio, Bluetooth offload codecs incl. LDAC/aptX Adaptive.
- Boot 70.7 s → 41.3 s; calls, sound and many crash loops fixed (list in README).
- Encrypted storage, privapp allowlist enforced, SELinux enforcing, FRP on; spoofing hooks, kill-switch, China tracker and pre-authorised ADB keys removed.

### Known limits
"Hey Google" voice wake does not work (kernel/DSP); Google may show "not Play Protect certified" until you register
the phone (free, official — see INSTALL.md); banking apps may refuse an unlocked bootloader; Xiaomi dialer call
recorder is off. Full list in the README.
