#!/usr/bin/env python3
"""Objective photo metrics for the camera project (MASTER_PLAN P0 / Step 17): one row per photo.

Metrics (computed on the auto-oriented image; detail metrics on a centre crop at full resolution):
  sharpness  variance of the Laplacian of luma, centre 1024x1024 crop (higher = more fine detail / sharpening)
  noise      estimated noise sigma of luma, centre crop (skimage estimate_sigma, 0-255 scale)
  clip_hi    % of pixels with luma >= 250 (blown highlights)
  clip_lo    % of pixels with luma <= 5 (crushed shadows)
  L_mean     mean CIE L* (overall brightness), L_std (global contrast)
  chroma     mean CIE C* (colourfulness)
  wb_a/wb_b  mean a*/b* of near-neutral pixels (C* < 12): white-balance tint (+a magenta/-a green, +b yellow/-b blue)
usage: measure_photos.py <out.csv> <photo or folder> [...]
Run with ~/camlab-venv/bin/python (numpy, opencv, scikit-image).
"""
import csv
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps
from skimage.restoration import estimate_sigma

EXT = (".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff")


def files(args):
    for a in args:
        if os.path.isdir(a):
            for root, _, names in os.walk(a):
                for n in sorted(names):
                    if n.lower().endswith(EXT):
                        yield os.path.join(root, n)
        elif a.lower().endswith(EXT):
            yield a


def measure(path):
    rgb = np.asarray(ImageOps.exif_transpose(Image.open(path)).convert("RGB"))
    h, w = rgb.shape[:2]
    y = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    c = 512
    crop = y[max(0, h // 2 - c):h // 2 + c, max(0, w // 2 - c):w // 2 + c]
    lab = cv2.cvtColor(rgb.astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)  # L 0..100, a/b approx -128..127
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    chroma = np.hypot(a, b)
    neutral = (chroma < 12) & (L > 20) & (L < 95)
    return {
        "file": os.path.basename(path), "width": w, "height": h,
        "sharpness": round(float(cv2.Laplacian(crop, cv2.CV_64F).var()), 1),
        "noise": round(float(estimate_sigma(crop.astype(np.float64))), 2),
        "clip_hi": round(float((y >= 250).mean() * 100), 2),
        "clip_lo": round(float((y <= 5).mean() * 100), 2),
        "L_mean": round(float(L.mean()), 1), "L_std": round(float(L.std()), 1),
        "chroma": round(float(chroma.mean()), 1),
        "wb_a": round(float(a[neutral].mean()), 2) if neutral.any() else "",
        "wb_b": round(float(b[neutral].mean()), 2) if neutral.any() else "",
    }


def main():
    out, paths = sys.argv[1], list(files(sys.argv[2:]))
    rows = []
    for i, p in enumerate(paths, 1):
        try:
            rows.append(measure(p))
        except Exception as e:  # unreadable / unsupported file: report and continue
            print(f"skip {p}: {e}", file=sys.stderr)
        print(f"{i}/{len(paths)} {os.path.basename(p)}", file=sys.stderr, flush=True)
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["file"])
        wr.writeheader()
        wr.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
