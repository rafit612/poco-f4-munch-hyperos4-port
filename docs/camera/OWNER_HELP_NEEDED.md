# What the owner has to do (camera project)

Things only a person with the phone in hand can do: real scenes, daylight, a real call. Everything else in the plan is done or is being done on the laptop.
Where to put the photos: just take them with the Xiaomi camera (and, where it says so, with LMC too). Say "done" in the chat and the shots are pulled and measured; nothing needs to be copied by hand.
Status of the rest of the plan: `PLAN_STATUS.md` (generated). Last updated 2026-10-31. **The project is paused until these photos and videos are taken.**

## A. Photo and video tests (about 30 minutes in total)

| # | When | What to do | What it decides |
|---|---|---|---|
| 1 | Daylight, outside | **Done 2026-10-31** (overcast). A sunny repeat is welcome. | Native about 2x softer than LMC; noise reduction stays on |
| 2 | Daylight, outside | One portrait of a person, face in shade and one with the sun behind them (backlit). Native camera, Portrait mode if it works, normal Photo mode if not. | Skin colour, backlit highlights (task P8 "window/backlit") |
| 3 | Inside, normal room light | Same scene again: one of your desk or a bookshelf with print, native + LMC. Then one video of 20 s with a person in frame in **native Video mode with Bokeh on**. | Indoor noise, video bokeh quality (P8) |
| 4 | Evening, outside | Night mode in the native camera: one scene with lights (street lamp), and the same scene in LMC Night Sight. | Purple cast is a known limit; this checks outdoor highlights |
| 6 | Outside, walking | Handheld video 15 s, 1080p, native camera, walking slowly. Then the same in 4K. | Stabilisation / OIS (P8 "OIS check") |
| 7 | Anywhere | Take new photos, then compare 5-6 pairs in Pictures/PhotoStage with the originals (same file names; only copies made after 2026-10-31 13:30 have the gentler colour). Say **better / same / too strong** for sharpness, colour and brightness. | The look of the photo stage |

Tips: keep the phone steady, tap to focus, do not use zoom unless the row says so, do not delete the new shots before they are measured (they are read from the DCIM folder).

## B. Phone and account things

| # | What | Why only the owner |
|---|---|---|
| 8 | Make one outgoing call on **SIM 1** that is answered, and say if voice works both ways on both SIMs. SIM 2 outgoing and incoming and SIM 1 incoming already connected. | The log cannot show sound |
| 9 | Change the router (Wi-Fi 5 GHz) channel to 36-48 or 149-165 and width 80 MHz; keep it off 161 if you want 160 MHz tests. Then say if the 85-second drops stop. | Router login |
| 10 | Restart-app setting: allow autostart + no battery restriction for the accessibility service app (the one that crashed the lock-screen toggle). | Needs phone settings screens |
| 11 | Decide: remove the disabled KernelSU module `munch_cam_watermark`? | Your call |
| 12 | Decide: what to do with `~/kernel_build` (about 20 GB, kernel work was stopped). | Your call |
| 13 | GitHub history: see the note from the push of 2026-10-31. Old commits may stay reachable by hash until GitHub support purges them: the purge request (also for the old IMEI commit) is yours to send. | Account owner |
| 14 | Gate G1 (P0): read `MODE_TEST_RESULTS.md` baseline and say "stable". | Sign-off |

## C. What I will do without you (not blocked)

Nothing is running. On return: measure the new shots, then adjust PhotoStage, and build the next ROM image if something changed (about 14 GB free needed).
