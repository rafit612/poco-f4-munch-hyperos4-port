package com.munch.nrprobe;

import android.app.Activity;
import android.content.Context;
import android.graphics.ImageFormat;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraMetadata;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.CaptureResult;
import android.hardware.camera2.TotalCaptureResult;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.Image;
import android.media.ImageReader;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.util.Size;
import android.view.Surface;
import android.view.WindowManager;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Test tool (not part of the ROM): takes the same still scene through Camera2 with different noise-reduction / edge modes, to see whether
 * the HAL can deliver more detail than the native camera app. Output: /sdcard/Android/data/com.munch.nrprobe/files/nr<N>_edge<E>_<k>.jpg + log.txt
 * start: am start -n com.munch.nrprobe/.NrProbe [--es id 0]   (grant CAMERA first: pm grant com.munch.nrprobe android.permission.CAMERA)
 */
public class NrProbe extends Activity {
    private CameraDevice dev;
    private CameraCaptureSession sess;
    private ImageReader jpeg;
    private Handler h;
    private HandlerThread ht;
    private CameraCharacteristics cc;
    private File out;
    private PrintLog log;
    private final List<int[]> combos = new ArrayList<int[]>();
    private int idx = 0, rep = 0;

    private static class PrintLog {
        final FileOutputStream f;
        PrintLog(File d) throws Exception { f = new FileOutputStream(new File(d, "log.txt")); }
        void p(String s) { try { f.write((s + "\n").getBytes()); f.flush(); } catch (Exception e) { /* ignore */ } }
    }

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON | WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON | WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED);
        ht = new HandlerThread("nrprobe");
        ht.start();
        h = new Handler(ht.getLooper());
        try {
            out = getExternalFilesDir(null);
            for (File f : out.listFiles()) { f.delete(); }
            log = new PrintLog(out);
            String id = getIntent().getStringExtra("id");
            if (id == null) { id = "0"; }
            CameraManager m = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
            cc = m.getCameraCharacteristics(id);
            int[] nrAvail = cc.get(CameraCharacteristics.NOISE_REDUCTION_AVAILABLE_NOISE_REDUCTION_MODES);
            int[] edgeAvail = cc.get(CameraCharacteristics.EDGE_AVAILABLE_EDGE_MODES);
            log.p("camera " + id + " NR modes " + Arrays.toString(nrAvail) + " edge modes " + Arrays.toString(edgeAvail));
            // (NR, EDGE): 0 off, 1 fast, 2 high quality, 3 minimal, 4 zsl
            int[][] want = {{2, 2}, {0, 0}, {3, 2}, {1, 1}, {0, 2}, {3, 0}};
            for (int[] w : want) {
                if (has(nrAvail, w[0]) && has(edgeAvail, w[1])) { combos.add(w); }
            }
            StreamConfigurationMap map = cc.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
            Size best = null;
            for (Size s : map.getOutputSizes(ImageFormat.JPEG)) {
                if (s.getWidth() * 3 != s.getHeight() * 4) { continue; }
                if (s.getWidth() > 4700) { continue; }
                if (best == null || s.getWidth() > best.getWidth()) { best = s; }
            }
            log.p("jpeg size " + best);
            jpeg = ImageReader.newInstance(best.getWidth(), best.getHeight(), ImageFormat.JPEG, 2);
            jpeg.setOnImageAvailableListener(new ImageReader.OnImageAvailableListener() {
                @Override public void onImageAvailable(ImageReader r) { save(r); }
            }, h);
            m.openCamera(id, new CameraDevice.StateCallback() {
                @Override public void onOpened(CameraDevice d) { dev = d; startSession(); }
                @Override public void onDisconnected(CameraDevice d) { log.p("disconnected"); d.close(); }
                @Override public void onError(CameraDevice d, int e) { log.p("error " + e); d.close(); }
            }, h);
        } catch (Exception e) {
            if (log != null) { log.p("fatal " + e); }
        }
    }

    private static boolean has(int[] a, int v) {
        if (a == null) { return false; }
        for (int x : a) { if (x == v) { return true; } }
        return false;
    }

    private void startSession() {
        try {
            final SurfaceTexture st = new SurfaceTexture(0);
            st.setDefaultBufferSize(1280, 960);
            final Surface prev = new Surface(st);
            dev.createCaptureSession(Arrays.asList(prev, jpeg.getSurface()), new CameraCaptureSession.StateCallback() {
                @Override public void onConfigured(CameraCaptureSession s) {
                    sess = s;
                    try {
                        CaptureRequest.Builder pb = dev.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
                        pb.addTarget(prev);
                        pb.set(CaptureRequest.CONTROL_AF_MODE, CameraMetadata.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
                        sess.setRepeatingRequest(pb.build(), null, h);
                        h.postDelayed(new Runnable() { @Override public void run() { shoot(); } }, 3500);
                    } catch (CameraAccessException e) { log.p("preview " + e); }
                }
                @Override public void onConfigureFailed(CameraCaptureSession s) { log.p("configure failed"); }
            }, h);
        } catch (Exception e) { log.p("session " + e); }
    }

    private void shoot() {
        if (idx >= combos.size()) { log.p("DONE"); finishAffinity(); return; }
        int[] c = combos.get(idx);
        try {
            CaptureRequest.Builder b = dev.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE);
            b.addTarget(jpeg.getSurface());
            b.set(CaptureRequest.NOISE_REDUCTION_MODE, c[0]);
            b.set(CaptureRequest.EDGE_MODE, c[1]);
            b.set(CaptureRequest.JPEG_QUALITY, (byte) 95);
            b.set(CaptureRequest.CONTROL_AF_MODE, CameraMetadata.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
            sess.capture(b.build(), new CameraCaptureSession.CaptureCallback() {
                @Override public void onCaptureCompleted(CameraCaptureSession s, CaptureRequest r, TotalCaptureResult t) {
                    log.p("result nr=" + t.get(CaptureResult.NOISE_REDUCTION_MODE) + " edge=" + t.get(CaptureResult.EDGE_MODE)
                        + " iso=" + t.get(CaptureResult.SENSOR_SENSITIVITY) + " exp_ns=" + t.get(CaptureResult.SENSOR_EXPOSURE_TIME)
                        + " focus_dist=" + t.get(CaptureResult.LENS_FOCUS_DISTANCE) + " af=" + t.get(CaptureResult.CONTROL_AF_STATE));
                }
            }, h);
        } catch (Exception e) { log.p("capture " + e); }
    }

    private void save(ImageReader r) {
        Image im = r.acquireLatestImage();
        if (im == null) { return; }
        int[] c = combos.get(idx);
        try {
            ByteBuffer buf = im.getPlanes()[0].getBuffer();
            byte[] data = new byte[buf.remaining()];
            buf.get(data);
            File f = new File(out, "nr" + c[0] + "_edge" + c[1] + "_" + (rep + 1) + ".jpg");
            FileOutputStream o = new FileOutputStream(f);
            o.write(data);
            o.close();
            log.p("saved " + f.getName() + " " + data.length);
        } catch (Exception e) { log.p("save " + e); }
        im.close();
        if (++rep >= 2) { rep = 0; idx++; }
        h.postDelayed(new Runnable() { @Override public void run() { shoot(); } }, 1500);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        try { if (sess != null) { sess.close(); } if (dev != null) { dev.close(); } } catch (Exception e) { /* ignore */ }
        ht.quitSafely();
    }
}
