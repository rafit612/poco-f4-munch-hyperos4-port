package com.munch.camera;

import android.util.Log;

import java.io.RandomAccessFile;

/**
 * Added to MiuiCamera by camera_watermark_patch.sh. A parallel shot first writes a small preview JPEG into a file that is
 * pre-allocated to 16 MiB; the processed photo later overwrites it. When the shot is abandoned (capture start arrived after
 * the mode was left, e.g. switching to video at night), the processed photo is dropped and the file stays a preview followed
 * by ~16 MB of zeros. trim() cuts such a file after its last non-zero byte so the preview remains as a normal small JPEG.
 * Only files of >= 8 MiB that start with a JPEG marker and end in >= 1 MiB of zeros are changed; errors are only logged.
 */
public final class PlaceholderTrim {
    private static final String TAG = "MunchPlaceholderTrim";

    private PlaceholderTrim() {
    }

    public static void trim(String path) {
        if (path == null) {
            return;
        }
        try (RandomAccessFile f = new RandomAccessFile(path, "rw")) {
            long len = f.length();
            if (len < (8L << 20) || f.read() != 0xFF || f.read() != 0xD8) {
                return;
            }
            byte[] buf = new byte[1 << 16];
            long end = len;
            while (end > 2) {
                int n = (int) Math.min(buf.length, end);
                f.seek(end - n);
                f.readFully(buf, 0, n);
                int i = n - 1;
                while (i >= 0 && buf[i] == 0) {
                    i--;
                }
                if (i >= 0) {
                    end = end - n + i + 1;
                    break;
                }
                end -= n;
            }
            if (len - end < (1L << 20)) {
                return;
            }
            f.setLength(end);
            Log.w(TAG, "abandoned shot: trimmed placeholder " + path + " from " + len + " to " + end + " bytes");
        } catch (Throwable t) {
            Log.w(TAG, "trim failed for " + path + ": " + t);
        }
    }
}
