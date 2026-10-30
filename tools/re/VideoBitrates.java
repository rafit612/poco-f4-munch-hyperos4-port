package com.munch.camera;

import java.util.HashMap;

/**
 * Added to MiuiCamera by camera_watermark_patch.sh as the Marble profile's video bitrate table (Marble.C0()). The recorder looks up
 * "quality:fps:5:" for HEVC and "quality:fps::" for H.264 (quality = CamcorderProfile.QUALITY_*: 5 = 720p, 6 = 1080p, 8 = 2160p) and
 * falls back to the vendor media_profiles value (30 fps only, e.g. 4K = 50 Mbit/s for 30 and 60 fps) when a key is missing.
 * The inherited Common table only had 30 fps HEVC (720p 10.8, 1080p 15.4, 4K 38.5 Mbit/s). SD870 Venus encodes up to 160 Mbit/s.
 */
public final class VideoBitrates {
    private static final int HEVC = 5;

    private VideoBitrates() {
    }

    private static void put(HashMap<String, HashMap<String, String>> t, int quality, int fps, int codec, int mbps) {
        HashMap<String, String> v = new HashMap<>();
        v.put("videoBitRate", Integer.toString(mbps * 1000000));
        t.put(quality + ":" + fps + ":" + (codec == HEVC ? "5" : "") + ":", v);
    }

    public static HashMap<String, HashMap<String, String>> table() {
        HashMap<String, HashMap<String, String>> t = new HashMap<>();
        // HEVC
        put(t, 5, 30, HEVC, 12);
        put(t, 5, 60, HEVC, 18);
        put(t, 6, 30, HEVC, 25);
        put(t, 6, 60, HEVC, 40);
        put(t, 8, 30, HEVC, 60);
        put(t, 8, 60, HEVC, 100);
        // H.264
        put(t, 5, 30, 0, 16);
        put(t, 5, 60, 0, 24);
        put(t, 6, 30, 0, 32);
        put(t, 6, 60, 0, 50);
        put(t, 8, 30, 0, 80);
        put(t, 8, 60, 0, 120);
        return t;
    }
}
