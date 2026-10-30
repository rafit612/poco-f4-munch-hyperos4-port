# Phone checks, 2026-10-30: Wi-Fi / mobile data, lock-screen toggle, dialer and contacts

No network names, numbers, IPs or contact data are recorded here. Raw logs are on the pendrive only
(`camera_project/network_check_2026-10-30/`).

## 1. Wi-Fi and mobile data
* Link when connected: Wi-Fi 6 (11ax), 5 GHz channel 161 (5805 MHz, 80 MHz wide), WPA3, RSSI -47 to -60 dBm, 1200 Mbit/s. Healthy.
* Surroundings: 2.4 GHz has 5 networks on channels 1, 2, 3, 5, 8 (overlapping, congested); 5 GHz has 5 networks, two of them on 149/153 inside
  our 80 MHz block. Before the reboot the phone sat on 2.4 GHz channels 3/4; 15 `DATA_STALL_BAD_TX` events with 19-34 retries at -35 dBm
  (interference signature) and one real 44 s outage at 05:00.
* **An external 85-second rhythm exists.** Phone ping to the router: 15-18 consecutive packets lost, every 85.0 s (16:07:04 ... 16:19:49).
  The laptop on the same router and channel is hit at the same instants (1-8 packets). With the phone's Wi-Fi switched **off** for 5 minutes
  the laptop was still hit at 16:26:54, 16:28:19, 16:29:44. So the source is the router or something on that channel, not the ROM.
  Nothing on the phone repeats every 85 s (searched every log line).
* The phone suffers more than the laptop and does so in some states only: after a Wi-Fi off/on it had no loss for 6 minutes; later it
  was back at 12 % (laptop 2 %). Open: a router-side fix (fixed channel, 80 -> 40 MHz or another 5 GHz channel, reboot, firmware) is the
  first thing to try; the cause of the phone's extra sensitivity is not found.
* Phone-side findings (real, not the cause of the 85 s rhythm): Settings keeps a second Wi-Fi interface `wlan1` (role SECONDARY_LONG_LIVED,
  requestor `com.android.settings`) and re-requests it every time Wi-Fi connects; `slave_wifi_on`/`wifi_slave_on`/`linkturbo_is_enable`
  switched off did not remove it (all restored to 1). `WifiClientModeImpl: Fail to get mlo info` every 3 s (10 873 times in 10 h, log noise:
  the Android 17 Wi-Fi stack asks the 2022 vendor HAL for Wi-Fi 7 data). One SELinux read denial on `wifi_hal_prop` (system_server).
  `cnss: Antenna switch request failed` at every boot (WLAN/modem coexistence, unchanged since the first snapshot).
* **Mobile data is switched off on both SIMs** (`mobile_data0/1 = 0`), so the phone is Wi-Fi-only; there is no Wi-Fi/mobile auto-switch to
  observe. Over 10 h both SIMs stayed IN_SERVICE on LTE: no fallback to 3G/2G, no 5G (`isEndcAvailable=false` on the serving cells).
  Preferred network type 32 = 5G/4G/3G/2G auto. LTE signal marginal at this spot (main cell RSRP -99 dBm, RSRQ -16 dB, SNR 4 dB).
* SIM 1 IMS (voice) flips LTE <-> IWLAN every 10-15 min for ~19 s and every handover fails with `HANDOFF_PREFERENCE_CHANGED`
  (`startHandover not supported on service DATA < 1.6`: vendor radio HAL older than the framework). SIM 2 IMS registration failed once
  (`4002, Unable to connect`). Harmless for data while mobile data is off; relevant for VoLTE/Wi-Fi calling.

## 2. Lock-screen toggle that turns itself off
* The only enabled accessibility service is the third-party `com.myapp.restart/PowerMenuService` ("Restart" power-menu app), and
  `dumpsys accessibility` listed it under **Crashed services**: Android shows a crashed accessibility service as switched off.
* Reproduced the toggle (delete + restore of `enabled_accessibility_services`): the service bound at once, the crashed list cleared and it
  stayed bound for the whole 10-minute watch. So switching it on works; it dies later when its process is killed. The app's MIUI
  autostart permission is denied (`MIUIOP 10008: ignore`), so after a kill nothing restarts it.
* Ruled out: gesture navigation reverting `accessibility_button_mode` (setting it to 0 stayed 0; original 1 restored).
* Fix for the owner (settings, not code): Security > Permissions > Autostart ON and Battery > No restrictions for that app. Not applied
  without asking (it is a user permission).

## 3. Dialer and contacts
* Providers are fast: 1,387 contacts / 3,022 raw contacts / 15,660 data rows answer in ~1.3 s including 1.2 s of tool start-up.
* **The call log holds 14 entries, the oldest 2026-10-25 23:36** (install day). Older history is not on the phone; this is missing data,
  not slow loading.
* Duplicates: MIUI Contacts + Google Contacts both handle `VIEW contacts/calls` (chooser opens); MIUI InCallUI + XiaomiInCallUI + the
  Dialer's own in-call UI exist. `android.process.acore` (contacts provider) restarted 12 times in 10.5 h; ActivityManager logged 42
  "non-cached process may get frozen soon" warnings for the Google Dialer (HyperOS freezer treats it as a normal app).
* ROM: see `ROM_HISTORY.md` section 11 (Google Phone + Contacts staged as priv-apps, MIUI Call parked). Needs the P9 build, a flash and a
  real call test before it counts as done.
