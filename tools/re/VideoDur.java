package com.munch.camera;

import android.media.MediaMetadataRetriever;
import android.util.Log;

import java.io.File;
import java.io.RandomAccessFile;

/**
 * Called by the camera's video save step (n7.Q.a) after its two duration reads. They sometimes return 0 for long recordings, and the app then DELETES the file
 * as "invalid". With data in the file, read the length from the MP4 header (mvhd) instead, so a finished recording is never thrown away.
 */
public final class VideoDur {
    private static final String TAG = "MunchVideoDur";
    private static final long MIN_FILE = 1024 * 1024;

    private VideoDur() { }

    public static long fix(String path, long duration) {
        if (duration > 0 || path == null) { return duration; }
        File f = new File(path);
        long len = f.length();
        if (len < MIN_FILE) { return duration; } // really empty: the app may delete it as before
        probe(path);
        long ms = 0;
        try { ms = mvhdMillis(f); } catch (Throwable t) { Log.w(TAG, "mvhd read failed", t); }
        Log.w(TAG, "duration 0 from the app, file " + len + " bytes, mvhd " + ms + " ms: keeping the file");
        return ms > 0 ? ms : 1000;
    }

    /** Only to record in the log why the framework read fails. */
    private static void probe(String path) {
        MediaMetadataRetriever r = new MediaMetadataRetriever();
        try {
            r.setDataSource(path);
            Log.w(TAG, "retriever now says duration " + r.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION));
        } catch (Throwable t) {
            Log.w(TAG, "retriever failed: " + t);
        } finally {
            try { r.release(); } catch (Throwable t) { /* ignore */ }
        }
    }

    static long mvhdMillis(File f) throws Exception {
        RandomAccessFile a = new RandomAccessFile(f, "r");
        try {
            long moov = find(a, 0, a.length(), "moov");
            if (moov < 0) { return 0; }
            long hdr = headerSize(a, moov);
            long mvhd = find(a, moov + hdr, moov + boxSize(a, moov), "mvhd");
            if (mvhd < 0) { return 0; }
            a.seek(mvhd + headerSize(a, mvhd));
            int version = a.readByte();
            a.skipBytes(3);
            long timescale, units;
            if (version == 1) {
                a.skipBytes(16);
                timescale = a.readInt() & 0xffffffffL;
                units = a.readLong();
            } else {
                a.skipBytes(8);
                timescale = a.readInt() & 0xffffffffL;
                units = a.readInt() & 0xffffffffL;
            }
            return timescale > 0 && units > 0 ? units * 1000 / timescale : 0;
        } finally {
            a.close();
        }
    }

    private static long find(RandomAccessFile a, long from, long end, String type) throws Exception {
        byte[] t = new byte[4];
        long pos = from;
        while (pos + 8 <= end) {
            long size = boxSize(a, pos);
            if (size < 8) { return -1; }
            a.seek(pos + 4);
            a.readFully(t);
            if (type.equals(new String(t, "ISO-8859-1"))) { return pos; }
            pos += size;
        }
        return -1;
    }

    private static long headerSize(RandomAccessFile a, long pos) throws Exception {
        a.seek(pos);
        return (a.readInt() & 0xffffffffL) == 1 ? 16 : 8;
    }

    private static long boxSize(RandomAccessFile a, long pos) throws Exception {
        a.seek(pos);
        long s = a.readInt() & 0xffffffffL;
        if (s == 1) { a.seek(pos + 8); return a.readLong(); }
        return s == 0 ? a.length() - pos : s;
    }
}
