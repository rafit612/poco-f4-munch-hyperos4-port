# Install guide — HyperOS 4 / Android 17 for POCO F4 5G (munch)

First time installing a ROM? Use the **[beginner's guide](docs/BEGINNER_GUIDE.md)** — it explains every step and every word.

> [!CAUTION]
> **POCO F4 5G (`munch`) only. At your own risk.** A clean install erases everything on the phone. Unlocking the
> bootloader also erases everything and may affect warranty. Back up first. Never relock the bootloader while this
> ROM (or any custom ROM) is installed — that bricks the phone.

**Model check:** Settings → About phone → Detailed info and specs → Model must be **22021211RG** (Global),
**22021211RI** (India) or **22021211RC** (Redmi K40S China). Anything else: stop.

You need: the phone with ≥ 60 % battery, a data-capable USB cable, a PC (Linux, macOS or Windows), about 15 GB free
disk space, and 20–40 minutes.

---

## 1. Unlock the bootloader

**Official way (recommended):**
1. Phone: Settings → About phone → tap *OS version* 7 times → Developer options appear (Settings → Additional settings).
2. Developer options → **OEM unlocking** on, **Mi Unlock status** → add your Xiaomi account (SIM with mobile data needed).
3. PC (Windows): download the official **Mi Unlock tool** from <https://en.miui.com/unlock/>, sign in with the same
   account, phone in fastboot mode (power off, then hold **Power + Volume down**), press *Unlock*.
4. Xiaomi usually makes you wait (often 7 days or more). When it finishes, the phone is wiped and shows an
   "unlocked" warning at every boot — that is normal.

**Community tool (only if the official way is blocked for you):** [HyperSploit](https://github.com/linuxct/HyperSploit)
is a third-party exploit that bypasses HyperOS's unlock restrictions. Reports say it works on **HyperOS 1** and fails on
newer versions. It is not ours, we did not audit it, and Xiaomi does not support it — **use it at your own risk** and
follow its own README.

## 2. Install the Android platform-tools (fastboot)

| System | How |
|---|---|
| Linux (Debian/Ubuntu) | `sudo apt install android-sdk-platform-tools` — or the zip from Google (below), then add it to `PATH` |
| Linux (Arch) | `sudo pacman -S android-tools` |
| macOS | `brew install android-platform-tools` |
| Windows | Download **SDK Platform-Tools for Windows** from <https://developer.android.com/tools/releases/platform-tools>, extract it, and either add the folder to `PATH` or copy `fastboot.exe` and `AdbWinApi*.dll` into the ROM folder. Install the **Google USB Driver** (or Xiaomi's driver) if `fastboot devices` shows nothing |

Use platform-tools **35 or newer** (older versions cannot talk to fastbootd). Check: `fastboot --version`.
Linux without `sudo` for USB: install the `android-udev` rules (most distributions have a package).

## 3. Download, join and check the ROM

From [Releases](../../releases) download **all** parts of `POCO-F4-munch-HyperOS4-A17-T20261026.zip.001`, `.002`, …
and `SHA256SUMS.txt` into one folder.

**Join the parts:**

| System | Command |
|---|---|
| Linux / macOS | `cat POCO-F4-munch-HyperOS4-A17-T20261026.zip.0* > POCO-F4-munch-HyperOS4-A17-T20261026.zip` |
| Windows (cmd) | `copy /b POCO-F4-munch-HyperOS4-A17-T20261026.zip.001+POCO-F4-munch-HyperOS4-A17-T20261026.zip.002+POCO-F4-munch-HyperOS4-A17-T20261026.zip.003 POCO-F4-munch-HyperOS4-A17-T20261026.zip` (all parts, in order) |
| Windows (7-Zip) | Right-click `….zip.001` → 7-Zip → *Extract here* (7-Zip joins the parts by itself; then skip the unzip step) |

**Check the zip** against the value in `SHA256SUMS.txt`:
- Linux: `sha256sum POCO-F4-munch-HyperOS4-A17-T20261026.zip` · macOS: `shasum -a 256 …zip`
- Windows: `certutil -hashfile POCO-F4-munch-HyperOS4-A17-T20261026.zip SHA256`

**Unzip** it. You get a folder with `images/` (28 partition images), `SHA256SUMS`, `flash_linux.sh`,
`flash_windows.bat` and `README.txt`. The scripts check every image again before flashing.

## 4. Flash

1. Power the phone off, then hold **Power + Volume down** until **FASTBOOT** appears. Connect USB.
2. Check the connection: `fastboot devices` (shows a serial number) and `fastboot getvar product` (must say `munch`).
3. Run the script from the ROM folder:
   - Linux / macOS: `bash flash_linux.sh` (macOS with release T20261026: `brew install coreutils`, then
     `PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH" bash flash_linux.sh`)
   - Windows: double-click `flash_windows.bat` (or run it in `cmd`)
4. Type `YES` when asked. The script then:
   - refuses to continue unless the phone reports `munch` and the bootloader is unlocked;
   - flashes firmware (abl, aop, bluetooth, dsp, modem, tz, xbl, …), `boot`, `dtbo`, `vendor_boot` to both slots,
     and `vbmeta` with verification disabled;
   - switches to fastbootd and flashes `system`, `system_ext`, `product`, `vendor`, `odm`, `mi_ext`;
   - erases `metadata` and `userdata` (so the first boot sets up encryption) and reboots.

The message `Invalid sparse file format at header magic` is normal. Any `FAILED` line stops the script — see
Troubleshooting.

<details>
<summary>Manual commands (what the script runs)</summary>

```sh
cd POCO-F4-munch-HyperOS4-A17-T20261026
fastboot getvar product          # must print: product: munch
for p in abl aop bluetooth cmnlib cmnlib64 devcfg dsp featenabler hyp imagefv keymaster modem qupfw tz uefisecapp xbl xbl_config boot dtbo vendor_boot; do
  fastboot flash ${p}_a images/$p.img
  fastboot flash ${p}_b images/$p.img
done
fastboot --disable-verity --disable-verification flash vbmeta_a images/vbmeta.img
fastboot --disable-verity --disable-verification flash vbmeta_b images/vbmeta.img
fastboot flash vbmeta_system_a images/vbmeta_system.img
fastboot flash vbmeta_system_b images/vbmeta_system.img
fastboot --set-active=a
fastboot reboot fastboot         # fastbootd
for p in system system_ext product vendor odm mi_ext; do
  fastboot delete-logical-partition ${p}_a-cow; fastboot delete-logical-partition ${p}_b
done
for p in system system_ext product vendor odm mi_ext; do fastboot flash $p images/$p.img; done
fastboot reboot bootloader
fastboot erase metadata
fastboot erase userdata
fastboot reboot
```
(`delete-logical-partition` errors for partitions that do not exist are fine.)
</details>

## 5. After the first boot

- The first boot takes **3–5 minutes** (Android builds its boot image once). Later boots take about 40 s.
- Follow the setup wizard: pick your **region** (it decides regional features), connect Wi-Fi, sign in to Google.
- Unlock the phone once after every restart (storage is encrypted).
- **SIM settings:** Settings → Mobile networks → your SIM: *Preferred network type*, *Use VoLTE*, *Wi-Fi calls*.
  VoLTE only works if your operator allows this phone. If mobile data or MMS does not work: Access Point Names → Reset.
- **GCam:** LMC 8.4 is preinstalled; its configs are copied to `/sdcard/LMC8.4` after the first unlock. Double-tap the
  black area next to the shutter to load one — `POCO-F4-FINAL.xml` is the recommended one.
- **AI:** Settings → Xiaomi HyperAI (Gemini, AI Interpreter for live call translation, AI Subtitles …).
  "Hey Google" voice wake does not work on this kernel; long-press the power button for the assistant.
- **Phone and SMS apps:** Xiaomi Phone/Contacts and Xiaomi Messages are included. You can install Google Phone and
  Google Messages from the Play Store; choose defaults in Settings → Apps → Default apps.
- Developer options and USB debugging are off. If you turn USB debugging on, the phone asks you to authorise each PC.

## Google Play Protect certification

After setup Google may show **"This device isn't Play Protect certified"** and block signing in to some Google apps.
No HyperOS 4 build for munch is certified by Google, and this ROM does not fake another phone. Google has a free,
official registration for custom ROMs; do it once per install (a factory reset creates a new ID):

1. **Get your GSF ID** (Google Services Framework Android ID).
   - Try an ID app such as *Device ID* (Evozi) first. Current Play Services hide this ID from normal apps, so it may
     show nothing.
   - If it is empty, read it with temporary root (KernelSU is built into the kernel): install a KernelSU
     manager app (for example ReSukiSU, from its official project page), grant root to *Shell*, then on the PC:
     ```sh
     adb exec-out su -c "cat /data/data/com.google.android.gms/databases/gservices.db" > gservices.db
     sqlite3 gservices.db "select value from main where name='android_id';"
     ```
     (Windows: install `sqlite3` or open the file with *DB Browser for SQLite*.) Afterwards **turn the Shell grant off
     in the manager first**, then uninstall the manager and reboot — uninstalling alone keeps the grant.
2. Open <https://www.google.com/android/uncertified/> signed in with the Google account used on the phone, paste
   the number (decimal), pass the captcha, press **Register**.
3. Settings → Apps → **Google Play Store** → Force stop → Clear storage. Reboot.
4. Wait: usually 15 minutes, up to 24 hours. The notification and sign-in block disappear. The Play Store's
   "Play Protect certification" line may still say "not certified"; apps that demand strong Play Integrity can still
   refuse to run.

## Updating to a newer release (keeps your data)

Releases that only change the system images can be installed without a wipe:
```sh
bash flash_linux.sh update          # Linux / macOS
flash_windows.bat update            # Windows
```
This flashes only `system`, `system_ext`, `product`, `vendor`, `odm`, `mi_ext`. Read each release's notes: if it says
"clean install", use the normal command instead.

## Going back to official HyperOS 1

Download the official **fastboot ROM** for munch (HyperOS 1.0.9 / 1.0.12 Global, "Fastboot" package) and flash it
with **Xiaomi MiFlash** using **clean all**. Do **not** choose *clean all and lock* unless the official ROM is
fully installed and boots — locking with anything else bricks the phone.

## Troubleshooting

| Problem | What to do |
|---|---|
| `fastboot devices` shows nothing / `< waiting for any device >` | Other USB cable/port (USB 2 ports work best), install the Google/Xiaomi USB driver (Windows), udev rules (Linux) |
| Script: "not a POCO F4 5G" | You are on another phone or the wrong mode. Stop. |
| Script: "bootloader is locked" | Unlock first (step 1) |
| "phone did not reach fastbootd" | Update platform-tools (35+); run `fastboot reboot fastboot` by hand, then re-run the script |
| `FAILED (remote: 'Not enough space to resize partition')` | In fastbootd: `fastboot delete-logical-partition <name>_b` for system, system_ext, product, vendor, odm, mi_ext, then flash again |
| Stuck on the boot logo for more than 10 minutes, or boot loop | Hold Power + Volume down → fastboot → run the script again (clean install) |
| Lands in fastboot after restarting | `fastboot --set-active=a`, `fastboot reboot` |
| No mobile data / MMS | Settings → Mobile networks → SIM → Access Point Names → ⋮ → Reset |
| No sound / call problems after an update | Make sure all six system images came from the same release |

Problems that are not in this list: open an issue on GitHub with the phone model, what you did, and the exact error.
