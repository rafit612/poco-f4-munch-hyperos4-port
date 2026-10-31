# Loudspeaker button does nothing during a call (found 2026-10-31)

Owner report: in the last call the speaker mode showed on but no sound came from the loudspeaker; it happens now and then.

## What happened in the last call (18:44:56 to 18:46:31)
| Time | Event |
|---|---|
| 18:44:56.8 | Call starts. Telecom sets the communication device to earpiece (`AudioManager: setCommunicationDevice earpiece`) |
| 18:45:00.99 | Owner taps Speaker. Telecom logs `USER_SWITCH_SPEAKER`, `Enter pending route, orig=EARPIECE, dest=SPEAKER`, then at once `EXIT_PENDING_ROUTE` and tells the dialer "route: SPEAKER" |
| 18:45:01 | **No `setCommunicationDevice(speaker)` call, no `setForceUse`, no audio policy change.** The audio HAL only switches the ultrasound proximity sensor off and keeps the handset (`voice-handset`, snd device 44) |
| 18:45:01 to 18:46:31 | The call runs on the earpiece for 90 s while the screen shows Speaker |
| 18:46:32 | After the call ends, the audio policy finally sets the speaker (too late) |
In the earlier calls that worked (12:42, 17:58, 17:59) the speaker came on through a device-changed event, so the audio system really switched.

## Cause (confirmed in the Telecom code)
`com.android.server.telecom.CallAudioRouteController` (in `/system/priv-app/Telecom/Telecom.apk`) keeps a cached copy of the last communication device, `mCurrentCommunicationDevice`. It is updated only by the listener `onCommunicationDeviceChanged`, which ignores a null device ("It should not happen as device is null"). `isCurrentCommunicationDevice(route)` compares the destination route with that cache, and when it says "already the current device" Telecom skips the `setCommunicationDevice` call.
The log shows how the cache goes stale:
* 18:20:58 a WhatsApp Business call set the communication device to **speaker**; Telecom's cache became speaker.
* WhatsApp calls ended at 18:29, 18:42 and 18:43; the audio service cleared the device, and the listener ignored the null, so the cache stayed **speaker**.
* The phone call at 18:44:56 started on the earpiece (the default, no change event), so the cache was never corrected.
* At 18:45:00 the owner tapped Speaker: Telecom compared with the stale cache, concluded the speaker was already the current device, and did nothing.
This is why it happens only sometimes: it needs an earlier audio session that left the speaker as the last device (a speaker call or video in another app) right before a phone call.

## Compared with the Xiaomi 17 reference (HyperOS 4, newer Telecom)
The reference `isCurrentCommunicationDevice` re-reads the real device from `AudioManager.getCommunicationDevice()` before comparing, so a stale cache can't cause this. The port's Telecom lacks it. The reference also has other newer changes (`mSkipDisconnectSco`, a same-Bluetooth-device check, an auto-answer-with-wired-headset allowance). The `AudioRoute` class itself is identical.

## Workaround for now
Tap Speaker off and on again (or tap Earpiece, then Speaker). Going to the earpiece sends a real `setCommunicationDevice(earpiece)`, the listener fires and the cache is correct again.

## Fix (ROM build, section F of `ROM_PHASE2_CHANGES.md`)
Apply the reference's change to the port's `Telecom.apk`: in `isCurrentCommunicationDevice`, for non-Bluetooth routes, read `audioManager.getCommunicationDevice()` instead of using the cache. A smali patch of one method, not a replacement of the whole app (the reference build is newer and larger). Alternative: also treat a null device in the listener as "cleared". Test: play a WhatsApp call on speaker, end it, make a phone call, tap Speaker: sound must come from the loudspeaker. Then repeat with earpiece, Bluetooth and wired headset. `tools/privcheck.py` and boot checks as for any system app; rollback by the previous system image.

## Not checked
Whether other callers (Meet, Messenger) leave the same stale state; the case where both SIMs ring; Bluetooth calls.
