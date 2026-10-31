package com.munch.photostage;

import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfDouble;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.photo.Photo;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Photo stage (port of tools/camera_lab/photo_stage.py, see docs/camera/08_PHOTO_STAGE.md). Works on an RGB 8-bit Mat, in CIE Lab:
 *   denoise  non-local means, only when the photo is grainy (noise sigma > NLM_FROM, measured: HAL-NR photo 0.25-0.36, NR-off photo 1.15): h = 4.4 * sigma, capped at 6
 *   detail   noise-gated two-scale unsharp mask, overshoot clamped to the local min/max
 *   tone     lifts a dark photo, shoulder on highlights, mid contrast only when flat
 *   colour   chroma gain towards a mean C* of 14, halved for skin hues, neutrals kept
 */
public final class StageEngine {
    public static final double NLM_FROM = 0.6;
    public static final double TARGET_CHROMA = 14.0;
    public static final double TARGET_L = 46.0;
    public static final double MAX_CHROMA_GAIN = 1.25, SAT_FROM = 25.0, SAT_TO = 60.0; // were 1.55, 45, 85: blue and red went too vivid in daylight

    public static final class Report {
        public double noise, nlmH, medianL, meanC;
    }

    private StageEngine() { }

    /** Native images: the Java GC does not see their size, so every intermediate is released as soon as it is used (3.4 GB peak without this, the system killed the app). */
    private static void free(Mat... ms) {
        for (Mat m : ms) { if (m != null) { m.release(); } }
    }

    public static Mat process(Mat rgb8, float detail, float tone, float colour, Report rep) {
        Mat[] lab = toLab(rgb8);
        double sigma = noiseSigma(lab[0], null);
        rep.noise = sigma;
        if (sigma > NLM_FROM) {
            float h = (float) Math.min(6.0, 4.4 * sigma);
            rep.nlmH = h;
            free(lab);
            Mat dn = new Mat();
            Photo.fastNlMeansDenoisingColored(rgb8, dn, h, 1.6f * h, 7, 21);
            lab = toLab(dn);
            free(dn);
        }
        Mat L = lab[0], a = lab[1], b = lab[2];
        if (detail > 0) {
            Mat gm = new Mat();
            double sig = noiseSigma(L, gm);
            Mat n = detailStep(L, gm, sig, detail);
            free(gm, L);
            L = n;
        }
        if (tone > 0) {
            Mat n = toneStep(L, tone, rep);
            free(L);
            L = n;
        }
        if (colour > 0) { colourStep(a, b, colour, rep); }
        List<Mat> ch = new ArrayList<Mat>(Arrays.asList(L, a, b));
        Mat merged = new Mat();
        Core.merge(ch, merged);
        free(L, a, b);
        Mat rgbf = new Mat();
        Imgproc.cvtColor(merged, rgbf, Imgproc.COLOR_Lab2RGB);
        free(merged);
        Mat out = new Mat();
        rgbf.convertTo(out, CvType.CV_8UC3, 255.0);
        free(rgbf);
        return out;
    }

    private static Mat[] toLab(Mat rgb8) {
        Mat f = new Mat();
        rgb8.convertTo(f, CvType.CV_32FC3, 1.0 / 255.0);
        Mat lab = new Mat();
        Imgproc.cvtColor(f, lab, Imgproc.COLOR_RGB2Lab);
        free(f);
        List<Mat> ch = new ArrayList<Mat>();
        Core.split(lab, ch);
        free(lab);
        return new Mat[] {ch.get(0), ch.get(1), ch.get(2)};
    }

    private static Mat blur(Mat m, double s) {
        Mat o = new Mat();
        Imgproc.GaussianBlur(m, o, new Size(0, 0), s);
        return o;
    }

    private static Mat smoothstep(Mat x, double a, double b) {
        Mat t = new Mat();
        Core.subtract(x, new Scalar(a), t);
        Core.multiply(t, new Scalar(1.0 / Math.max(b - a, 1e-6)), t);
        Imgproc.threshold(t, t, 0, 0, Imgproc.THRESH_TOZERO);
        Imgproc.threshold(t, t, 1, 1, Imgproc.THRESH_TRUNC);
        Mat t2 = new Mat();
        Core.multiply(t, t, t2);
        Mat u = new Mat();
        Core.multiply(t, new Scalar(-2.0), u);
        Core.add(u, new Scalar(3.0), u);
        Core.multiply(t2, u, t2);
        free(t, u);
        return t2;
    }

    private static float[] sample(Mat m, int step) {
        Mat s = new Mat();
        Imgproc.resize(m, s, new Size(Math.max(1, m.cols() / step), Math.max(1, m.rows() / step)), 0, 0, Imgproc.INTER_NEAREST);
        float[] d = new float[(int) s.total()];
        s.get(0, 0, d);
        free(s);
        return d;
    }

    private static double percentile(float[] v, double p) {
        float[] c = v.clone();
        Arrays.sort(c);
        return c[(int) Math.min(c.length - 1, Math.max(0, p * (c.length - 1)))];
    }

    /** Noise sigma of L* from the finest-scale residual in the flattest 20 % of the image; optionally returns the gradient magnitude. */
    private static double noiseSigma(Mat L, Mat gmOut) {
        Mat b1 = blur(L, 1.0);
        Mat d = new Mat();
        Core.subtract(L, b1, d);
        Mat g = blur(L, 1.5);
        Mat gx = new Mat(), gy = new Mat(), gm = new Mat();
        Imgproc.Sobel(g, gx, CvType.CV_32F, 1, 0);
        Imgproc.Sobel(g, gy, CvType.CV_32F, 0, 1);
        Core.magnitude(gx, gy, gm);
        free(b1, g, gx, gy);
        float[] dv = sample(d, 4), gv = sample(gm, 4);
        free(d);
        double thr = percentile(gv, 0.20);
        List<Float> r = new ArrayList<Float>();
        for (int i = 0; i < gv.length; i++) { if (gv[i] <= thr) { r.add(dv[i]); } }
        float[] rv = new float[r.size()];
        for (int i = 0; i < rv.length; i++) { rv[i] = r.get(i); }
        double med = percentile(rv, 0.5);
        float[] dev = new float[rv.length];
        for (int i = 0; i < rv.length; i++) { dev[i] = (float) Math.abs(rv[i] - med); }
        if (gmOut != null) { gm.copyTo(gmOut); }
        free(gm);
        return 1.4826 * percentile(dev, 0.5) + 1e-3;
    }

    private static Mat detailStep(Mat L, Mat gm, double sig, float amount) {
        Mat gate = smoothstep(gm, 2.0 * sig, 7.0 * sig);
        Mat b09 = blur(L, 0.9), b26 = blur(L, 2.6);
        Mat d1 = new Mat(), d2 = new Mat();
        Core.subtract(L, b09, d1);
        Core.subtract(b09, b26, d2);
        free(b09, b26);
        Mat boost = new Mat();
        Core.addWeighted(d1, 1.15, d2, 0.55, 0.0, boost);
        free(d1, d2);
        Core.multiply(gate, boost, boost);
        Core.multiply(boost, new Scalar(amount), boost);
        free(gate);
        Mat out = new Mat();
        Core.add(L, boost, out);
        free(boost);
        Mat k = Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(5, 5));
        Mat lo = new Mat(), hi = new Mat();
        Imgproc.erode(L, lo, k);
        Imgproc.dilate(L, hi, k);
        free(k);
        Mat slack = new Mat();
        Core.subtract(hi, lo, slack);
        Core.multiply(slack, new Scalar(0.04), slack);
        Core.add(slack, new Scalar(0.5), slack);
        Mat floor = new Mat(), ceil = new Mat();
        Core.subtract(lo, slack, floor);
        Core.add(hi, slack, ceil);
        free(lo, hi, slack);
        Core.max(out, floor, out);
        Core.min(out, ceil, out);
        free(floor, ceil);
        return out;
    }

    private static Mat toneStep(Mat L, float amount, Report rep) {
        float[] s = sample(L, 8);
        double med = percentile(s, 0.5);
        rep.medianL = med;
        MatOfDouble mean = new MatOfDouble(), std = new MatOfDouble();
        Core.meanStdDev(L, mean, std);
        double lift = Math.max(-0.04, Math.min(0.10, (TARGET_L - med) / 100.0));
        Mat x = new Mat();
        Core.multiply(L, new Scalar(0.01), x);
        Imgproc.threshold(x, x, 0, 0, Imgproc.THRESH_TOZERO);
        Imgproc.threshold(x, x, 1, 1, Imgproc.THRESH_TRUNC);
        Mat y = new Mat();
        Core.pow(x, 1.0 - 1.4 * lift, y);
        free(x);
        Mat sh = smoothstep(y, 0.78, 1.0);
        Mat t = new Mat();
        Core.subtract(y, new Scalar(0.78), t);
        Core.multiply(sh, t, t);
        Core.multiply(t, new Scalar(0.12), t);
        Core.subtract(y, t, y);
        free(sh, t);
        double c = Math.max(0.0, Math.min(0.18, (21.0 - std.toArray()[0]) / 60.0));
        if (c > 0) {
            Mat z = new Mat();
            Core.multiply(y, new Scalar(2.0), z);
            Core.subtract(z, new Scalar(1.0), z);
            Mat z2 = new Mat();
            Core.multiply(z, z, z2);
            Core.subtract(z2, new Scalar(1.0), z2);
            Core.multiply(z2, new Scalar(-1.0), z2);
            Mat yc = new Mat();
            Core.subtract(y, new Scalar(0.5), yc);
            Core.multiply(yc, z2, yc);
            Core.multiply(yc, new Scalar(c), yc);
            Core.add(y, yc, y);
            free(z, z2, yc);
        }
        Imgproc.threshold(y, y, 0, 0, Imgproc.THRESH_TOZERO);
        Imgproc.threshold(y, y, 1, 1, Imgproc.THRESH_TRUNC);
        Core.multiply(y, new Scalar(100.0), y);
        Mat diff = new Mat();
        Core.subtract(y, L, diff);
        Core.multiply(diff, new Scalar(amount), diff);
        Mat out = new Mat();
        Core.add(L, diff, out);
        free(y, diff, mean, std);
        return out;
    }

    private static void colourStep(Mat a, Mat b, float amount, Report rep) {
        Mat C = new Mat();
        Core.magnitude(a, b, C);
        double cur = Core.mean(C).val[0];
        rep.meanC = cur;
        double g = Math.max(1.0, Math.min(MAX_CHROMA_GAIN, TARGET_CHROMA / Math.max(cur, 1e-3)));
        Mat hue = new Mat();
        Core.phase(a, b, hue, true);
        Mat up = smoothstep(hue, 12.0, 20.0);
        Mat down = smoothstep(hue, 75.0, 87.0);
        free(hue);
        Core.multiply(down, new Scalar(-1.0), down);
        Core.add(down, new Scalar(1.0), down);
        Mat satLo = smoothstep(C, 45.0, 70.0);
        Core.multiply(satLo, new Scalar(-1.0), satLo);
        Core.add(satLo, new Scalar(1.0), satLo);
        Mat skin = new Mat();
        Core.multiply(up, down, skin);
        Core.multiply(skin, satLo, skin);
        free(up, down, satLo);
        Mat gain = new Mat();
        Core.multiply(skin, new Scalar(-0.5), gain);
        Core.add(gain, new Scalar(1.0), gain);
        Core.multiply(gain, new Scalar((g - 1.0) * amount), gain);
        free(skin);
        Mat neutral = smoothstep(C, 2.0, 8.0);
        Mat sat = smoothstep(C, SAT_FROM, SAT_TO);
        free(C);
        Core.multiply(sat, new Scalar(-1.0), sat);
        Core.add(sat, new Scalar(1.0), sat);
        Core.multiply(gain, neutral, gain);
        Core.multiply(gain, sat, gain);
        Core.add(gain, new Scalar(1.0), gain);
        free(neutral, sat);
        Core.multiply(a, gain, a);
        Core.multiply(b, gain, b);
        free(gain);
    }
}
