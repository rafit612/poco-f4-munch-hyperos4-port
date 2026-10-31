package com.munch.photostage;

import android.app.job.JobInfo;
import android.app.job.JobParameters;
import android.app.job.JobScheduler;
import android.app.job.JobService;
import android.content.ComponentName;
import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.ContentValues;
import android.content.Context;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.provider.MediaStore;

import org.opencv.android.Utils;
import org.opencv.core.Mat;
import org.opencv.imgproc.Imgproc;

import java.io.InputStream;
import java.io.OutputStream;

/**
 * Background watcher: when a new photo from the native camera (owner com.android.camera, DCIM/Camera) appears in MediaStore, runs StageEngine on it
 * and saves a COPY as Pictures/PhotoStage/<same name>. The original is never modified. Own output and other apps' photos (e.g. LMC) are skipped.
 * Runs as a content-trigger job (system decides when; needs battery not low) plus a persisted 15-minute catch-up job.
 */
public class StageJob extends JobService {
    static { System.loadLibrary("opencv_java4"); }
    static final int JOB_ID = 4711, CATCHUP_ID = 4712;
    private static final java.util.concurrent.atomic.AtomicBoolean BUSY = new java.util.concurrent.atomic.AtomicBoolean();
    static final String PREFS = "stage", LAST = "last_id", ON = "enabled";
    static final String CAMERA_PKG = "com.android.camera";
    static final String TRY_ID = "try_id", TRY_N = "try_n";
    static final int MAX_TRIES = 3;
    private volatile boolean stop;

    static void schedule(Context c) {
        baseline(c);
        JobScheduler js = (JobScheduler) c.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        JobInfo.Builder b = new JobInfo.Builder(JOB_ID, new ComponentName(c, StageJob.class));
        b.addTriggerContentUri(new JobInfo.TriggerContentUri(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, JobInfo.TriggerContentUri.FLAG_NOTIFY_FOR_DESCENDANTS));
        b.setTriggerContentUpdateDelay(8000).setTriggerContentMaxDelay(60000).setRequiresBatteryNotLow(true);
        js.schedule(b.build());
        // If the system kills the process mid-work, the content-trigger job does not come back by itself (seen 2026-10-31):
        // this persisted job re-arms it and catches up on missed photos within 15 minutes, also after a reboot.
        if (js.getPendingJob(CATCHUP_ID) == null) {
            js.schedule(new JobInfo.Builder(CATCHUP_ID, new ComponentName(c, StageJob.class)).setPeriodic(15 * 60 * 1000L)
                    .setPersisted(true).setRequiresBatteryNotLow(true).build());
        }
    }

    /** Remembers the newest existing photo so only photos taken after switching on are processed. */
    static void baseline(Context c) {
        SharedPreferences sp = c.getSharedPreferences(PREFS, 0);
        if (sp.getLong(LAST, -1) >= 0) { return; }
        long last = 0;
        Cursor q = c.getContentResolver().query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, new String[] {MediaStore.Images.Media._ID}, null, null,
                MediaStore.Images.Media._ID + " DESC");
        if (q != null) { if (q.moveToFirst()) { last = q.getLong(0); } q.close(); }
        sp.edit().putLong(LAST, last).apply();
    }

    static void cancel(Context c) {
        JobScheduler js = (JobScheduler) c.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        js.cancel(JOB_ID);
        js.cancel(CATCHUP_ID);
    }

    @Override
    public boolean onStartJob(final JobParameters p) {
        if (!getSharedPreferences(PREFS, 0).getBoolean(ON, false)) { return false; }
        if (!BUSY.compareAndSet(false, true)) { // the other job is already working through the list
            if (p.getJobId() == JOB_ID) { schedule(this); }
            return false;
        }
        new Thread(new Runnable() {
            @Override public void run() {
                try {
                    long before;
                    do { // photos taken while a batch ran do not raise a new trigger, so look again until nothing is new
                        before = getSharedPreferences(PREFS, 0).getLong(LAST, -1);
                        runOnce();
                    } while (!stop && getSharedPreferences(PREFS, 0).getLong(LAST, -1) != before);
                } catch (Throwable e) { android.util.Log.e("PhotoStage", "run failed", e); }
                BUSY.set(false);
                if (getSharedPreferences(PREFS, 0).getBoolean(ON, false)) { schedule(StageJob.this); }
                jobFinished(p, false);
            }
        }).start();
        return true;
    }

    @Override
    public boolean onStopJob(JobParameters p) {
        stop = true;
        return true;
    }

    private void runOnce() throws Exception {
        SharedPreferences sp = getSharedPreferences(PREFS, 0);
        ContentResolver cr = getContentResolver();
        long last = sp.getLong(LAST, -1);
        Uri base = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
        if (last < 0) { baseline(this); last = sp.getLong(LAST, 0); }
        Cursor c = cr.query(base, new String[] {MediaStore.Images.Media._ID, MediaStore.Images.Media.DISPLAY_NAME, MediaStore.Images.Media.OWNER_PACKAGE_NAME,
                MediaStore.Images.Media.RELATIVE_PATH, MediaStore.Images.Media.IS_PENDING},
                MediaStore.Images.Media._ID + " > ?", new String[] {String.valueOf(last)}, MediaStore.Images.Media._ID + " ASC");
        if (c == null) { return; }
        while (c.moveToNext() && !stop) {
            long id = c.getLong(0);
            String name = c.getString(1), owner = c.getString(2), rel = c.getString(3);
            if (c.getInt(4) != 0) { break; } // still being written: retry next time
            if (!isNativePhoto(owner, rel, name)) {
                android.util.Log.d("PhotoStage", "skip " + name + " owner=" + owner + " path=" + rel);
                sp.edit().putLong(LAST, id).commit();
                continue;
            }
            // The system may kill this process while it works (camera in front, low memory): a photo counts as done only after its copy is saved.
            int tries = sp.getLong(TRY_ID, -1) == id ? sp.getInt(TRY_N, 0) : 0;
            if (tries >= MAX_TRIES) {
                android.util.Log.w("PhotoStage", "giving up on " + name + " after " + tries + " tries");
                sp.edit().putLong(LAST, id).commit();
                continue;
            }
            sp.edit().putLong(TRY_ID, id).putInt(TRY_N, tries + 1).commit();
            try { stage(cr, ContentUris.withAppendedId(base, id), name); } catch (Throwable e) { android.util.Log.e("PhotoStage", "stage " + name, e); }
            sp.edit().putLong(LAST, id).commit();
        }
        c.close();
    }

    /** MediaProvider may hide the owner from this app (seen when it runs from /product): then the native camera's IMG_ names decide; LMC saves F4_... names. */
    static boolean isNativePhoto(String owner, String rel, String name) {
        if (rel == null || !rel.startsWith("DCIM/Camera") || name == null || !name.toLowerCase().endsWith(".jpg")) { return false; }
        return owner != null ? CAMERA_PKG.equals(owner) : name.startsWith("IMG_");
    }

    static final long MAX_PIXELS = 24000000L; // 16 MP photos fit in the heap; panoramas (76 MP) do not and are skipped

    private void stage(ContentResolver cr, Uri src, String name) throws Exception {
        BitmapFactory.Options bo = new BitmapFactory.Options();
        bo.inJustDecodeBounds = true;
        InputStream probe = cr.openInputStream(src);
        try { BitmapFactory.decodeStream(probe, null, bo); } finally { probe.close(); }
        if ((long) bo.outWidth * bo.outHeight > MAX_PIXELS) {
            android.util.Log.d("PhotoStage", "skip " + name + ": over 24 MP");
            return;
        }
        Bitmap bmp;
        InputStream in = cr.openInputStream(src);
        try { bmp = BitmapFactory.decodeStream(in); } finally { in.close(); }
        Mat rgba = new Mat(); Utils.bitmapToMat(bmp, rgba); bmp.recycle();
        Mat rgb = new Mat(); Imgproc.cvtColor(rgba, rgb, Imgproc.COLOR_RGBA2RGB); rgba.release();
        Mat out = StageEngine.process(rgb, 1f, 1f, 1f, new StageEngine.Report()); rgb.release();
        Mat orgba = new Mat(); Imgproc.cvtColor(out, orgba, Imgproc.COLOR_RGB2RGBA); out.release();
        Bitmap ob = Bitmap.createBitmap(orgba.cols(), orgba.rows(), Bitmap.Config.ARGB_8888);
        Utils.matToBitmap(orgba, ob); orgba.release();
        ContentValues v = new ContentValues();
        v.put(MediaStore.Images.Media.DISPLAY_NAME, name);
        v.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
        v.put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/PhotoStage");
        v.put(MediaStore.Images.Media.IS_PENDING, 1);
        Uri dst = cr.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v);
        OutputStream os = cr.openOutputStream(dst);
        try { ob.compress(Bitmap.CompressFormat.JPEG, 95, os); } finally { os.close(); ob.recycle(); }
        copyExif(cr, src, dst);
        ContentValues done = new ContentValues();
        done.put(MediaStore.Images.Media.IS_PENDING, 0);
        cr.update(dst, done, null, null);
        android.util.Log.d("PhotoStage", "copied " + name);
    }

    private void copyExif(ContentResolver cr, Uri src, Uri dst) {
        try {
            InputStream in = cr.openInputStream(src);
            android.media.ExifInterface a = new android.media.ExifInterface(in);
            in.close();
            java.io.FileDescriptor fd;
            android.os.ParcelFileDescriptor pfd = cr.openFileDescriptor(dst, "rw");
            android.media.ExifInterface b = new android.media.ExifInterface(pfd.getFileDescriptor());
            for (String t : new String[] {"DateTime", "DateTimeOriginal", "DateTimeDigitized", "Make", "Model", "ExposureTime", "FNumber", "ISOSpeedRatings",
                    "PhotographicSensitivity", "FocalLength", "FocalLengthIn35mmFilm", "Flash", "WhiteBalance", "GPSLatitude", "GPSLatitudeRef", "GPSLongitude",
                    "GPSLongitudeRef", "GPSAltitude", "GPSAltitudeRef", "GPSDateStamp", "GPSTimeStamp"}) {
                String s = a.getAttribute(t);
                if (s != null) { b.setAttribute(t, s); }
            }
            b.setAttribute("Software", "PhotoStage");
            b.saveAttributes();
            pfd.close();
        } catch (Throwable e) { android.util.Log.w("PhotoStage", "exif copy failed", e); }
    }
}
