#!/usr/bin/env python3
"""Post-capture photo stage for the native camera (MASTER_PLAN P8, rank 1 in docs/camera/07_IMPROVEMENT_PLAN.md).

Works on the saved JPEG, in CIE Lab, in three steps (each can be switched off):
  detail  noise-gated two-scale unsharp mask on L*; the gate is derived from the image's own noise level so flat areas are not
          boosted; overshoot is clamped to the local min/max (no halos)
  tone    lifts shadows slightly, compresses highlights (shoulder) and adds mid contrast only when the photo is flat
  denoise (--denoise A, off by default) edge-aware chroma/luma denoise for photos taken with the HAL noise reduction off
  colour  chroma gain towards a target mean C*, rolled off for very saturated pixels and halved for skin hues; near-neutrals are kept
usage: photo_stage.py <in.jpg> <out.jpg> [--detail A] [--tone A] [--colour A] [--report]      (A = strength, 0 = off, 1 = default)
Run with ~/camlab-venv/bin/python (numpy, opencv, pillow). EXIF and ICC are copied unchanged.
"""
import argparse
import io

import cv2
import numpy as np
from PIL import Image

TARGET_CHROMA = 14.0   # Xiaomi 17 indoor median 17.4, daylight 11.1; native v13 stand shots ~8
TARGET_L_MEDIAN = 46.0  # reference sets A/B median L*
SKIN_HUE = (20.0, 75.0)  # Lab hue angle in degrees; skin sits at roughly 35-65


def smoothstep(x, a, b):
    t = np.clip((x - a) / max(b - a, 1e-6), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def noise_sigma(L):
    """Noise level of L* from the finest-scale residual in the flattest 20 % of the image."""
    d = L - cv2.GaussianBlur(L, (0, 0), 1.0)
    g = cv2.GaussianBlur(L, (0, 0), 1.5)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    gm = np.hypot(gx, gy)
    flat = gm <= np.percentile(gm, 20)
    r = d[flat]
    return float(1.4826 * np.median(np.abs(r - np.median(r)))) + 1e-3, gm


def detail(L, amount):
    sig, gm = noise_sigma(L)
    gate = smoothstep(gm, 2.0 * sig, 7.0 * sig)  # edges/texture get the boost, flat noisy areas do not
    d1 = L - cv2.GaussianBlur(L, (0, 0), 0.9)
    d2 = cv2.GaussianBlur(L, (0, 0), 0.9) - cv2.GaussianBlur(L, (0, 0), 2.6)
    out = L + amount * gate * (1.15 * d1 + 0.55 * d2)
    k = np.ones((5, 5), np.uint8)
    lo, hi = cv2.erode(L, k), cv2.dilate(L, k)
    slack = 0.04 * (hi - lo) + 0.5
    return np.clip(out, lo - slack, hi + slack), sig


def denoise(L, a, b, amount):
    """Edge-aware noise removal for photos taken with the HAL noise reduction off: strong chroma blur (colour speckle is cheap to remove),
    luma blur only in flat areas (same gate as detail), edges and texture keep their pixels."""
    sig, gm = noise_sigma(L)
    gate = smoothstep(gm, 2.0 * sig, 7.0 * sig)
    # chroma: guide with the luma gradient so colour does not bleed across real edges
    ke = smoothstep(gm, 3.0 * sig, 10.0 * sig)
    a2 = cv2.GaussianBlur(a, (0, 0), 3.0)
    b2 = cv2.GaussianBlur(b, (0, 0), 3.0)
    a = a + amount * (1 - ke) * (a2 - a)
    b = b + amount * (1 - ke) * (b2 - b)
    # luma: pull flat areas toward a light blur, keep gated (edge/texture) pixels
    Lb = cv2.GaussianBlur(L, (0, 0), 1.3)
    L = L + amount * (1 - gate) * (Lb - L)
    return L, a, b, sig


def tone(L, amount):
    x = np.clip(L / 100.0, 0, 1)
    med = float(np.median(L))
    lift = np.clip((TARGET_L_MEDIAN - med) / 100.0, -0.04, 0.10)  # only brighten a dark photo, never darken a bright one
    y = x ** (1.0 - 1.4 * lift)
    sh = smoothstep(y, 0.78, 1.0)
    y = y - 0.12 * sh * (y - 0.78)  # highlight shoulder
    std = float(np.std(L))
    c = np.clip((21.0 - std) / 60.0, 0.0, 0.18)  # mid contrast only when the photo is flat
    y = y + c * (y - 0.5) * (1 - np.abs(2 * y - 1) ** 2)
    return L + amount * (np.clip(y, 0, 1) * 100.0 - L)


def colour(a, b, amount, target=TARGET_CHROMA):
    C = np.hypot(a, b)
    cur = float(np.mean(C))
    g = float(np.clip(target / max(cur, 1e-3), 1.0, 1.55))
    h = (np.degrees(np.arctan2(b, a)) + 360) % 360
    skin = smoothstep(h, SKIN_HUE[0] - 8, SKIN_HUE[0]) * (1 - smoothstep(h, SKIN_HUE[1], SKIN_HUE[1] + 12)) * (1 - smoothstep(C, 45, 70))
    gain = 1.0 + (g - 1.0) * amount * (1 - 0.5 * skin)
    gain = 1.0 + (gain - 1.0) * smoothstep(C, 2.0, 8.0) * (1 - smoothstep(C, 45, 85))  # keep neutrals, soften saturated
    return a * gain, b * gain


def process(rgb8, d=1.0, t=1.0, c=1.0, n=0.0):
    bgr = cv2.cvtColor(rgb8, cv2.COLOR_RGB2BGR).astype(np.float32) / 255.0
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2Lab)
    L, a, b = [lab[..., i].copy() for i in range(3)]
    sig = None
    if n > 0:
        L, a, b, sig = denoise(L, a, b, n)
    if d > 0:
        L, sig = detail(L, d)
    if t > 0:
        L = tone(L, t)
    if c > 0:
        a, b = colour(a, b, c)
    lab = np.stack([np.clip(L, 0, 100), np.clip(a, -127, 127), np.clip(b, -127, 127)], axis=-1).astype(np.float32)
    out = cv2.cvtColor(cv2.cvtColor(lab, cv2.COLOR_Lab2BGR), cv2.COLOR_BGR2RGB)
    return np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8), sig


def metrics(rgb8):
    """Same family as measure_photos.py, plus edge slope (median gradient on the strongest 1 % edges) and halo share."""
    lab = cv2.cvtColor(cv2.cvtColor(rgb8, cv2.COLOR_RGB2BGR).astype(np.float32) / 255.0, cv2.COLOR_BGR2Lab)
    L = lab[..., 0]
    h, w = L.shape
    c = L[h // 2 - 512:h // 2 + 512, w // 2 - 512:w // 2 + 512]
    sig, _ = noise_sigma(L)
    g = cv2.GaussianBlur(L, (0, 0), 0.7)
    gm = np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)) / 8.0
    edge = gm >= np.percentile(gm, 99)
    k = np.ones((7, 7), np.uint8)
    over = (L > cv2.dilate(cv2.GaussianBlur(L, (0, 0), 2.0), k) + 4) | (L < cv2.erode(cv2.GaussianBlur(L, (0, 0), 2.0), k) - 4)
    C = np.hypot(lab[..., 1], lab[..., 2])
    near = C < 12
    return {
        "lap": float(cv2.Laplacian(c, cv2.CV_32F).var()),
        "noise": sig,
        "edge": float(np.median(gm[edge])),
        "halo%": 100.0 * float(over.mean()),
        "clipHi%": 100.0 * float((rgb8.max(axis=-1) >= 250).mean()),
        "L": float(np.median(L)),
        "Lstd": float(np.std(L)),
        "C": float(np.mean(C)),
        "wb_a": float(np.mean(lab[..., 1][near])) if near.any() else 0.0,
        "wb_b": float(np.mean(lab[..., 2][near])) if near.any() else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"), ap.add_argument("dst")
    ap.add_argument("--detail", type=float, default=1.0), ap.add_argument("--tone", type=float, default=1.0)
    ap.add_argument("--colour", type=float, default=1.0), ap.add_argument("--denoise", type=float, default=0.0), ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    im = Image.open(a.src)
    exif, icc = im.info.get("exif"), im.info.get("icc_profile")
    rgb = np.asarray(im.convert("RGB"))
    out, sig = process(rgb, a.detail, a.tone, a.colour, a.denoise)
    kw = {"quality": 95, "subsampling": 0}
    if exif:
        kw["exif"] = exif
    if icc:
        kw["icc_profile"] = icc
    Image.fromarray(out).save(a.dst, **kw)
    if a.report:
        for name, arr in (("before", rgb), ("after ", out)):
            m = metrics(arr)
            print(name, "  ".join(f"{k} {v:7.2f}" for k, v in m.items()))


if __name__ == "__main__":
    main()
