# Dynamic Island: features and position (checked 2026-10-31)

Owner request: are all Dynamic Island features present, and is the island in the right place? One read-only pass plus one short, reversible test (a simulated charger plug-in, then `dumpsys battery reset`).

## Position: correct
| Item | Measured |
|---|---|
| Screen | 1080 x 2400, status bar 94 px |
| Camera hole (system cutout) | Rect x 512 to 568, y 0 to 94: centre x = **540**, exactly the middle |
| Island pill (charging, screenshots) | x 312 to 768 in one frame and 321 to 758 in another: centre **539.5 to 540**; vertically it covers about y 8 to 102 with the hole centred at about y 55 |
| Island window | `DynamicIslandWindow`, full width at the top, collapsed (height 0) when idle |
The island is centred on the hole in both directions, to within a pixel. It is wider than the hole, as designed, and covers it while shown. Not checked: other island sizes (expanded), landscape, the lock screen.

## Features
**Switches on this phone:** `support_dynamic_island=1`, `support_dynamic_island_blur=1`, `support_status_bar_follow=1` (global settings), `persist.sys.feature.island=1`, `ro.miui.notch=1`. `persist.sys.feature.island.animation` and the glow shader properties are empty (defaults).
**Code compared with the Xiaomi 17 HyperOS 4 reference:**
* SystemUI island classes: 17 on the phone against 18 in the reference; the only one missing is an internal lambda.
* SystemUI plugin (`MIUISystemUIPlugin`): the same 24 island and focus classes; 4251 island-related strings against 4213. Only a few names differ: the reference has `miuiIslandMediaController` and `islandShowingFlow`; the port's plugin additionally has an island glow shader (`IslandGlowShader`, `IslandGlowView`).
* Conclusion: the island code is complete and the same generation as Xiaomi 17's. Nothing is missing from the code; what shows up depends on the apps that feed it.
**Verified working:** the charging island ("Charging 100 %" with the lightning icon and a glow effect, then it folds into the status bar battery).
**Not verified yet (needs the app to run):**
| Island | Fed by | Open question |
|---|---|---|
| Call | Dialer | The ROM uses Google Dialer (owner choice), not Xiaomi's InCallUI. Xiaomi's island for calls is built for its own dialer; Google Dialer may only give the normal ongoing-call notification. **Needs a real call** |
| Music | Media session | `MiuiIslandMediaController` exists; try with a player |
| Timer, alarm, stopwatch | Xiaomi Clock | Needs a timer run |
| Navigation | Maps apps | Needs a Maps trip |
| Screen recording, hotspot, Wi-Fi, file transfer | System | Needs a run each |
| Delivery, taxi, flights (third-party "live updates") | Apps sending focus notifications | `secure focus_notifs` and `updatable_focus_notifs` are empty `[]`; the live-update blacklist and mini-window lists exist in the plugin. The cloud lists that normally fill these may never download on this ROM |
Checklist for the owner: call, music, timer, Maps navigation, screen recording, hotspot, one delivery or ride app; say which ones show an island. I will read the logs of each to see why when one doesn't.

## Method and limits
Position from `dumpsys window` (cutout and window frame) and from screenshots of the top 300 px taken every 0.5 s while the island showed; the battery was set back with `dumpsys battery reset` and read back as real (AC, charging, 100 %). Class and string comparison from the dex files of `MiuiSystemUI.apk` and `MIUISystemUIPlugin.apk` on the phone and in the reference image on the pendrive. Names present do not prove a feature works; only the charging island was seen working.
