#!/usr/bin/env python3
"""Fine detail per region for stand A/B shots: Laplacian variance of luma on a 3x3 grid (full resolution, no rescale).

Same scene + same grid for every photo, so the numbers compare build against build (higher = more fine detail / sharpening).
Also prints the noise sigma of the flattest tile (skimage estimate_sigma) to tell real detail from kept noise.
usage: tile_detail.py <photo.jpg> [...]      Run with ~/camlab-venv/bin/python.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps
from skimage.restoration import estimate_sigma


def tiles(path):
    img = np.asarray(ImageOps.exif_transpose(Image.open(path)).convert("L"), dtype=np.float32)
    h, w = img.shape
    out = []
    for r in range(3):
        for c in range(3):
            t = img[r * h // 3:(r + 1) * h // 3, c * w // 3:(c + 1) * w // 3]
            out.append((cv2.Laplacian(t, cv2.CV_32F).var(), t))
    return (w, h), out


def main():
    print("photo, size, " + ", ".join(f"t{i}" for i in range(9)) + ", mean, noise_flat")
    for p in sys.argv[1:]:
        size, ts = tiles(p)
        lap = [v for v, _ in ts]
        flat = ts[int(np.argmin(lap))][1]
        noise = estimate_sigma(flat[::2, ::2])
        print(f"{os.path.basename(p)}, {size[0]}x{size[1]}, " + ", ".join(f"{v:.1f}" for v in lap)
              + f", {np.mean(lap):.1f}, {noise:.2f}")


if __name__ == "__main__":
    main()
