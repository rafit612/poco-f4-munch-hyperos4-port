# Beginner's guide — install HyperOS 4 on your POCO F4 5G, step by step

This guide is for people who have **never installed a custom ROM**. Every step says what to do and what you
should see. Go slowly; do not skip steps. If something looks different from what is written here, **stop** and
read [If something goes wrong](#if-something-goes-wrong).

People who know fastboot can use the short version: [INSTALL.md](../INSTALL.md).

---

## Read this first

- **Only for the POCO F4 5G** (codename `munch`). Not for POCO F4 GT, POCO F5, Redmi Note or any other phone.
- **Everything on the phone will be erased** — photos, chats, apps. Back up first (step 1).
- **At your own risk.** This is not an official Xiaomi update. If something goes wrong, you fix it yourself (this guide
  shows how for the common problems).
- **Time:** about 1 hour of work, plus the waiting time Xiaomi gives you before you can unlock (often 7 days).
- **You need:**
  - your POCO F4 5G, charged to at least 60 %;
  - a USB cable that can transfer data (the one from the box is best; some cheap cables only charge);
  - a Windows, Linux or Mac computer with about 15 GB free space and internet;
  - a Xiaomi account (free) and a SIM card with mobile data (Xiaomi needs it for unlocking).

### Words you will see

| Word | What it means |
|---|---|
| **ROM** | The phone's operating system (Android + HyperOS). This project is a ROM. |
| **Bootloader** | A small program that starts the phone. It is "locked" from the factory so only Xiaomi software runs. You must **unlock** it once to install this ROM. |
| **Fastboot mode** | A special screen (a rabbit/robot and the word FASTBOOT) where a computer can write software to the phone. You open it with **Power + Volume down**. |
| **Fastbootd** | A second fastboot mode the installer switches to by itself. You do not need to do anything. |
| **Flash** | Write software (an "image") onto the phone. |
| **Wipe** | Erase all user data. |
| **Platform-tools** | Free program from Google that contains `fastboot` and `adb`, the tools that talk to the phone. |
| **Image (.img)** | One piece of the ROM (the system, the camera software, the modem, …). The ROM has 28 of them. |
| **Boot loop** | The phone restarts again and again and never reaches the home screen. Fixable (see below). |

---

## Step 1 — Back up your phone

Everything will be erased. Save what you want to keep:
- **Photos/videos:** Google Photos backup, or copy the `DCIM` folder to the computer with the USB cable
  (choose "File transfer" on the phone's USB notification).
- **WhatsApp:** WhatsApp → Settings → Chats → Chat backup → Back up (to Google Drive).
- **Contacts:** make sure they are saved in your Google account (Contacts app → Settings → Accounts).
- **Other files:** copy `Download`, `Documents` and anything else from the phone to the computer.

## Step 2 — Check that you really have a POCO F4 5G

Settings → **About phone** → **Detailed info and specs** → **Model**. It must be one of:
`22021211RG`, `22021211RI` or `22021211RC`.
Anything else → **stop, this ROM is not for your phone.**

## Step 3 — Unlock the bootloader (one time only)

> Unlocking erases the phone. Xiaomi makes you wait several days between steps 3.3 and 3.5.

**3.1 Turn on Developer options.** Settings → About phone → tap **OS version** 7 times quickly.
You see "You are now a developer".

**3.2 Link your Xiaomi account.** Settings → Additional settings → **Developer options**:
- turn on **OEM unlocking**;
- open **Mi Unlock status** → *Add account and device*. Mobile data must be on (Wi-Fi off) for this step.
You see "Added successfully".

**3.3 On the computer (Windows):** download the official **Mi Unlock** tool from <https://en.miui.com/unlock/>,
extract it, run `miflash_unlock.exe`, sign in with the **same** Xiaomi account.

**3.4 Put the phone in fastboot mode:** switch the phone **off**. Hold **Power + Volume down** together until you see
**FASTBOOT** on the screen, then let go. Connect the USB cable.

**3.5 Press Unlock** in Mi Unlock.
- If it says you must wait (for example "168 hours"), unplug, use the phone normally, and come back after that time.
  Do **not** remove the account from the phone while waiting.
- When it works, the phone is erased and restarts. From now on every start shows a small warning that the bootloader
  is unlocked. That is normal.

> **Community tool, only if the official way is blocked for you:** [HyperSploit](https://github.com/linuxct/HyperSploit)
> is a third-party tool that bypasses HyperOS unlock limits. People report that it works on HyperOS 1 and fails on
> newer versions. We did not make or check it. Use it **at your own risk** and follow its own instructions.

## Step 4 — Install the tools on your computer

### Windows
1. Download **SDK Platform-Tools for Windows** from
   <https://developer.android.com/tools/releases/platform-tools> (accept the terms).
2. Right-click the zip → *Extract all* → choose `C:\` — you now have a folder `C:\platform-tools`.
3. Download and install the **Google USB Driver** from
   <https://developer.android.com/studio/run/win-usb> (or Xiaomi's USB driver; Mi Unlock often installs one already).
4. Install **7-Zip** from <https://www.7-zip.org/> (free; needed to open the ROM).

### Linux (Ubuntu, Mint, Debian)
Open a terminal and run:
```sh
sudo apt update
sudo apt install android-sdk-platform-tools p7zip-full
```

### Mac
Install Homebrew from <https://brew.sh>, then in Terminal: `brew install android-platform-tools p7zip`.

## Step 5 — Download the ROM

1. Open the project's **Releases** page:
   <https://github.com/rafit612/poco-f4-munch-hyperos4-port/releases>.
2. In the newest release, under *Assets*, download **all three parts** and the checksum file:
   - `POCO-F4-munch-HyperOS4-A17-T20261026.zip.001`
   - `POCO-F4-munch-HyperOS4-A17-T20261026.zip.002`
   - `POCO-F4-munch-HyperOS4-A17-T20261026.zip.003`
   - `SHA256SUMS.txt`
3. Put them all in **one** new folder, for example `C:\POCO-ROM` (Windows) or `~/POCO-ROM` (Linux/Mac).
   Total download is about 6 GB.

## Step 6 — Unpack the ROM

### Windows
1. Open `C:\POCO-ROM`, right-click `POCO-F4-munch-HyperOS4-A17-T20261026.zip.001` →
   **7-Zip → Extract Here**. 7-Zip joins the three parts by itself.
2. Wait a few minutes. You get a folder `POCO-F4-munch-HyperOS4-A17-T20261026` containing:
   `images` (a folder), `SHA256SUMS`, `flash_linux.sh`, `flash_windows.bat`, `README.txt`.
3. Copy `fastboot.exe`, `AdbWinApi.dll` and `AdbWinUsbApi.dll` from `C:\platform-tools` **into** that folder
   (next to `flash_windows.bat`).

### Linux / Mac
```sh
cd ~/POCO-ROM
7z x POCO-F4-munch-HyperOS4-A17-T20261026.zip.001
cd POCO-F4-munch-HyperOS4-A17-T20261026
```

Don't worry about checking files by hand: the installer checks every image before it writes anything. If a download
was damaged, it stops and tells you to download again.

## Step 7 — Connect the phone in fastboot mode

1. Switch the phone **off**. Hold **Power + Volume down** until **FASTBOOT** appears. Connect the USB cable
   (use a port directly on the computer, not a hub; on desktops the back ports are best).
2. **Windows:** open the ROM folder, click the address bar, type `cmd` and press Enter — a black window opens in that
   folder. **Linux/Mac:** use the terminal from step 6.
3. Type this and press Enter:
   ```
   fastboot devices
   ```
   You should see one line with a code and the word `fastboot`. If you see nothing → see
   [If something goes wrong](#if-something-goes-wrong) (usually the driver or the cable).
4. Type:
   ```
   fastboot getvar product
   ```
   You should see `product: munch`. If you see anything else, **stop**.

## Step 8 — Install the ROM

1. In the same window, start the installer:
   - **Windows:** `flash_windows.bat`
   - **Linux/Mac:** `bash flash_linux.sh`

   > **Mac, release T20261026:** its installer expects `sha256sum`. Run it like this:
   > `brew install coreutils && PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH" bash flash_linux.sh`

2. It checks the images ("Checking image files"), checks that the phone is a POCO F4 with an unlocked bootloader,
   and asks you to type **YES** (capital letters). Type `YES` and press Enter.
3. Now it writes about 40 items. You will see many lines like `Sending …`, `Writing … OKAY`.
   The line `Invalid sparse file format at header magic` is **normal**.
   In the middle the phone restarts into a different fastboot screen (fastbootd) by itself — keep the cable connected.
4. It takes about 10–15 minutes. **Do not unplug the cable or press buttons** while it runs.
5. At the end you see `Done.` and the phone restarts.

If any line says `FAILED`, the installer stops. Nothing is "half broken" yet in a dangerous way — read the message and
go to [If something goes wrong](#if-something-goes-wrong).

## Step 9 — First start

1. The first start takes **3–5 minutes** (the phone prepares itself once). Later starts take about 40 seconds.
   The unlock warning at the start is normal.
2. Set up the phone: language → **region** (choose your country; it decides regional features) → Wi-Fi →
   Google account → restore your apps if you like.
3. After setup:
   - **SIM:** Settings → Mobile networks → tap your SIM → you can choose 5G/4G, turn on **VoLTE** and **Wi-Fi calls**
     (they only work if your operator allows them). If mobile internet does not work: *Access Point Names* → ⋮ → *Reset*.
   - **Camera:** the normal Camera app works. **LMC 8.4** (Google Camera) is also installed; to load the best settings,
     double-tap the black area next to the shutter button and pick `POCO-F4-FINAL.xml`.
   - **AI:** Settings → **Xiaomi HyperAI** (Gemini, AI Interpreter for translating phone calls, AI Subtitles).

## Step 10 — If Google says "This device isn't Play Protect certified"

Google has not certified this HyperOS version for the POCO F4, so Google may show this message and block some Google
sign-ins. Google itself offers a free fix: register your phone.

1. Find your phone's **GSF ID** — the detailed way (it needs temporary root) is in
   [INSTALL.md → Google Play Protect certification](../INSTALL.md#google-play-protect-certification).
2. On a computer or the phone, open <https://www.google.com/android/uncertified/>, sign in with the **same Google
   account** you use on the phone, paste the number, tick *I'm not a robot*, press **Register**.
3. Phone: Settings → Apps → **Google Play Store** → Force stop → Clear data. Restart the phone.
4. Wait 15 minutes to a few hours (at most 24). The message goes away.

---

## If something goes wrong

Stay calm — almost everything here can be fixed by running the installer again.

| What you see | What to do |
|---|---|
| `fastboot devices` shows nothing / `waiting for any device` | Try another USB cable and another USB port. Windows: install the Google USB Driver (step 4), then in *Device Manager* look for "Android" with a yellow mark → right-click → Update driver → *Browse* → `C:\platform-tools` or the driver folder. Restart the computer. |
| `'fastboot' is not recognized` (Windows) | You did not copy `fastboot.exe` into the ROM folder (step 6.3), or the black window was not opened inside the ROM folder |
| `this is not a POCO F4 5G` | Wrong phone or wrong mode. Do not continue. |
| `bootloader is locked` | Go back to step 3 |
| `checksum mismatch` | A download is damaged — download all parts again |
| `phone did not reach fastbootd` | Update platform-tools (step 4), then run the installer again |
| `Not enough space to resize partition` | Run the installer again (it frees space first). If it repeats, see INSTALL.md → Troubleshooting |
| The phone shows the logo for more than 10 minutes, or keeps restarting | Hold **Power + Volume down** until FASTBOOT appears → run the installer again (Step 7–8) |
| After an update the phone only starts into fastboot | In the black window: `fastboot --set-active=a` then `fastboot reboot` |
| No mobile internet / MMS | Settings → Mobile networks → SIM → Access Point Names → ⋮ → Reset |

**Going back to the official Xiaomi software:** download the official *Fastboot ROM* for the POCO F4 (HyperOS 1.0.9 or
1.0.12 Global) and install it with Xiaomi's **MiFlash** tool, option **clean all**. Never choose *clean all and lock*
unless you are installing official Xiaomi software — locking with a custom ROM breaks the phone.

## FAQ

**Will I lose my data?** The first install erases everything. Later updates of this ROM can keep your data
(`flash_windows.bat update` / `bash flash_linux.sh update`) unless the release notes say otherwise.

**Can I get updates?** Only from this project's Releases page. If the phone's own *System update* app ever offers
something, do **not** install it.

**Do banking apps work?** Many do; some refuse phones with an unlocked bootloader. Test the apps you need.

**Does "Hey Google" work?** No, voice wake-up does not work on this phone's kernel. Long-press the power button to
open the assistant instead.

**Can I lock the bootloader again?** Not with this ROM. Only after going back to official Xiaomi software.

**Is it safe?** It is more secure than the port it is based on (encryption, no tracker, no hidden spoofing), but an
unlocked bootloader is always less secure than a locked official phone. See the README's Security section.

---

## বাংলায় সংক্ষেপে

> **শুধু POCO F4 5G (munch) ফোনের জন্য। নিজের দায়িত্বে করবেন। ফোনের সব ডেটা মুছে যাবে — আগে ব্যাকআপ নিন।**

1. **ব্যাকআপ:** ছবি, WhatsApp, কন্টাক্ট — সব Google বা কম্পিউটারে রাখুন।
2. **মডেল দেখুন:** Settings → About phone → Detailed info and specs → Model হতে হবে `22021211RG`, `22021211RI` বা `22021211RC`।
3. **বুটলোডার আনলক:** Developer options চালু করুন (OS version-এ ৭ বার চাপুন) → OEM unlocking চালু → Mi Unlock status-এ
   Xiaomi অ্যাকাউন্ট যোগ করুন (মোবাইল ডেটা চালু রেখে)। কম্পিউটারে অফিশিয়াল Mi Unlock টুল দিয়ে আনলক করুন। Xiaomi কয়েক দিন
   অপেক্ষা করতে বলতে পারে।
4. **কম্পিউটারে টুল:** Google-এর Platform-Tools আর 7-Zip ইনস্টল করুন (Windows-এ USB ড্রাইভারও)।
5. **ROM ডাউনলোড:** Releases পেজ থেকে ৩টা পার্ট (`.zip.001`, `.002`, `.003`) আর `SHA256SUMS.txt` এক ফোল্ডারে নামান।
6. **খুলুন:** `.zip.001`-এ রাইট-ক্লিক → 7-Zip → Extract Here। Windows হলে `fastboot.exe` আর দুটো `.dll` ফাইল ROM ফোল্ডারে কপি করুন।
7. **ফোন fastboot মোডে:** ফোন বন্ধ → Power + Volume down একসাথে চেপে ধরুন → FASTBOOT লেখা আসবে → USB লাগান।
   `fastboot getvar product` লিখলে `munch` দেখাতে হবে।
8. **ইনস্টল:** Windows-এ `flash_windows.bat`, Linux-এ `bash flash_linux.sh` চালান → `YES` লিখুন → ১০–১৫ মিনিট অপেক্ষা করুন,
   কেবল খুলবেন না।
9. **প্রথম চালু:** ৩–৫ মিনিট লাগবে। সেটআপে নিজের দেশ (region) বেছে নিন।
10. **"Play Protect certified নয়" দেখালে:** <https://www.google.com/android/uncertified/> থেকে ফোনের GSF ID রেজিস্টার করুন
    (বিস্তারিত INSTALL.md-তে)।

সমস্যা হলে ঘাবড়াবেন না — Power + Volume down দিয়ে fastboot-এ গিয়ে আবার ইনস্টলার চালালেই বেশিরভাগ ঠিক হয়ে যায়।
