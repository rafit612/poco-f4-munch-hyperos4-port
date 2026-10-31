package com.munch.photostage;

import android.Manifest;
import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.Switch;
import android.widget.TextView;

/** One switch: turns the background photo stage on or off (copies go to Pictures/PhotoStage, originals are never changed). */
public class StageMain extends Activity {
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        requestPermissions(new String[] {Manifest.permission.READ_MEDIA_IMAGES}, 1);
        final SharedPreferences sp = getSharedPreferences(StageJob.PREFS, 0);
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        l.setPadding(48, 96, 48, 48);
        TextView t = new TextView(this);
        t.setTextSize(16);
        t.setText("Photo stage: new photos from the Xiaomi camera get a processed copy in Pictures/PhotoStage (denoise if grainy, detail, tone, colour). Originals stay untouched.");
        Switch s = new Switch(this);
        s.setText("Enabled");
        s.setChecked(sp.getBoolean(StageJob.ON, false));
        if (s.isChecked()) { StageJob.schedule(this); } // an app update drops scheduled jobs; opening the app brings it back
        s.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override public void onCheckedChanged(CompoundButton v, boolean on) {
                sp.edit().putBoolean(StageJob.ON, on).apply();
                if (on) { StageJob.schedule(StageMain.this); } else { StageJob.cancel(StageMain.this); }
            }
        });
        l.addView(t);
        l.addView(s);
        setContentView(l);
    }
}
