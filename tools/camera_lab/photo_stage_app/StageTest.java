package com.munch.photostage;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.BatteryManager;
import android.os.Bundle;
import android.content.Context;

import org.opencv.android.Utils;
import org.opencv.core.Mat;
import org.opencv.imgproc.Imgproc;
import org.opencv.photo.Photo;

import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintWriter;

/**
 * Speed test for the photo stage on the phone (not part of the ROM): loads files/in.jpg, runs OpenCV non-local-means denoise with strength h
 * (intent extra "h", default 5; "tpl" template window 7, "win" search window 21), writes files/out.jpg and files/log.txt with timings.
 * "--ez full true" runs the whole StageEngine (denoise if grainy, detail, tone, colour) instead.
 * start: am start -n com.munch.photostage/.StageTest --ef h 5 --ei win 21
 */
public class StageTest extends Activity {
    static { System.loadLibrary("opencv_java4"); }

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        final float h = getIntent().getFloatExtra("h", 5f);
        final int win = getIntent().getIntExtra("win", 21);
        final int tpl = getIntent().getIntExtra("tpl", 7);
        new Thread(new Runnable() { @Override public void run() { work(h, tpl, win); } }).start();
    }

    private void work(float h, int tpl, int win) {
        File dir = getExternalFilesDir(null);
        PrintWriter log = null;
        try {
            log = new PrintWriter(new FileOutputStream(new File(dir, "log.txt")));
            BatteryManager bm = (BatteryManager) getSystemService(Context.BATTERY_SERVICE);
            long t0 = System.nanoTime();
            Bitmap bmp = BitmapFactory.decodeFile(new File(dir, "in.jpg").getAbsolutePath());
            Mat rgba = new Mat(); Utils.bitmapToMat(bmp, rgba);
            Mat rgb = new Mat(); Imgproc.cvtColor(rgba, rgb, Imgproc.COLOR_RGBA2RGB);
            long t1 = System.nanoTime();
            log.println("loaded " + rgb.cols() + "x" + rgb.rows() + " in " + (t1 - t0) / 1000000 + " ms, battery temp " + bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CURRENT_NOW));
            Mat dst = new Mat();
            if (getIntent().getBooleanExtra("full", false)) {
                StageEngine.Report rep = new StageEngine.Report();
                dst = StageEngine.process(rgb, 1f, 1f, 1f, rep);
                log.println("full stage: noise " + rep.noise + " nlmH " + rep.nlmH + " medianL " + rep.medianL + " meanC " + rep.meanC);
            } else {
                Photo.fastNlMeansDenoisingColored(rgb, dst, h, 1.6f * h, tpl, win);
            }
            long t2 = System.nanoTime();
            log.println("NLM h=" + h + " tpl=" + tpl + " win=" + win + ": " + (t2 - t1) / 1000000 + " ms");
            Mat outRgba = new Mat(); Imgproc.cvtColor(dst, outRgba, Imgproc.COLOR_RGB2RGBA);
            Bitmap ob = Bitmap.createBitmap(outRgba.cols(), outRgba.rows(), Bitmap.Config.ARGB_8888);
            Utils.matToBitmap(outRgba, ob);
            FileOutputStream fo = new FileOutputStream(new File(dir, "out.jpg"));
            ob.compress(Bitmap.CompressFormat.JPEG, 95, fo); fo.close();
            long t3 = System.nanoTime();
            log.println("saved in " + (t3 - t2) / 1000000 + " ms; total " + (t3 - t0) / 1000000 + " ms; max heap " + Runtime.getRuntime().maxMemory() / 1048576 + " MB");
            log.println("DONE");
        } catch (Throwable e) {
            if (log != null) { log.println("FAILED " + e); }
        } finally {
            if (log != null) { log.close(); }
            runOnUiThread(new Runnable() { @Override public void run() { finish(); } });
        }
    }
}
