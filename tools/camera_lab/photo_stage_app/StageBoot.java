package com.munch.photostage;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** A job with a content trigger cannot be persisted, so it is gone after a reboot: schedule it again if the switch is on. */
public class StageBoot extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent i) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(i.getAction()) && c.getSharedPreferences(StageJob.PREFS, 0).getBoolean(StageJob.ON, false)) {
            StageJob.schedule(c);
        }
    }
}
