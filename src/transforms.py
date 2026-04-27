"""Image transforms: standard preprocessing + the three degradation
families the brief asks for (frequency, spatial, brightness).

The degradation builders return *PIL-in / PIL-out* callables so they can
be applied either offline (saved to ``data/degraded_faces/``) or on the
fly inside a Dataset.
"""
from __future__ import annotations

import io
import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from torchvision import transforms as T

from . import config as C


# -------------------------------------------------------------------------
# Standard pipelines
# -------------------------------------------------------------------------
def standard_train_transform(image_size: Tuple[int, int] = C.FACE_SIZE) -> Callable:
    return T.Compose([
        T.Resize(image_size),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomRotation(degrees=10),
        T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        T.ToTensor(),
        T.Normalize(C.IMAGENET_MEAN, C.IMAGENET_STD),
    ])


def standard_eval_transform(image_size: Tuple[int, int] = C.FACE_SIZE) -> Callable:
    return T.Compose([
        T.Resize(image_size),
        T.ToTensor(),
        T.Normalize(C.IMAGENET_MEAN, C.IMAGENET_STD),
    ])


# -------------------------------------------------------------------------
# Degradation families (PIL -> PIL)
# -------------------------------------------------------------------------
def brightness_degradation(severity: float = 0.5) -> Callable:
    """Multiplicative brightness/contrast change.

    severity in [0,1]; 0 -> no change, 1 -> very dark or very bright.
    Sign is randomised per call so the dataset contains both.
    """
    def _apply(img: Image.Image) -> Image.Image:
        sign = random.choice([-1, 1])
        factor = 1.0 + sign * severity
        factor = max(0.1, factor)
        img = ImageEnhance.Brightness(img).enhance(factor)
        # also nudge contrast so changes are not purely additive
        img = ImageEnhance.Contrast(img).enhance(1.0 + sign * severity * 0.5)
        return img
    return _apply


def spatial_degradation(severity: float = 0.5) -> Callable:
    """Rotation + small translation + occasional crop+resize."""
    max_rot = 10 + severity * 25  # up to ~35 deg
    max_trans = 0.05 + severity * 0.15

    def _apply(img: Image.Image) -> Image.Image:
        rot = random.uniform(-max_rot, max_rot)
        img = img.rotate(rot, resample=Image.BILINEAR, fillcolor=(0, 0, 0))
        w, h = img.size
        tx = int(random.uniform(-max_trans, max_trans) * w)
        ty = int(random.uniform(-max_trans, max_trans) * h)
        img = img.transform(
            img.size, Image.AFFINE, (1, 0, tx, 0, 1, ty),
            resample=Image.BILINEAR, fillcolor=(0, 0, 0),
        )
        if random.random() < 0.5:
            crop_frac = 0.7 + (1 - severity) * 0.25
            cw, ch = int(w * crop_frac), int(h * crop_frac)
            x0 = random.randint(0, max(0, w - cw))
            y0 = random.randint(0, max(0, h - ch))
            img = img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)
        if random.random() < 0.5:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return img
    return _apply


def frequency_degradation(severity: float = 0.5) -> Callable:
    """Gaussian blur + JPEG re-compression + Gaussian noise (frequency-domain hits)."""
    blur_radius = 0.5 + severity * 3.0
    jpeg_q = int(max(8, 80 - severity * 70))
    noise_sigma = severity * 25  # in 0-255 image domain

    def _apply(img: Image.Image) -> Image.Image:
        # Blur
        if random.random() < 0.7:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        # JPEG re-compression
        if random.random() < 0.7:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=jpeg_q)
            buf.seek(0)
            img = Image.open(buf).convert("RGB").copy()
        # Additive Gaussian noise
        if random.random() < 0.7 and noise_sigma > 0:
            arr = np.asarray(img).astype(np.float32)
            arr += np.random.normal(0, noise_sigma, arr.shape)
            arr = np.clip(arr, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
        return img
    return _apply


# -------------------------------------------------------------------------
# Combined "all three" degradation, used to materialise the degraded set
# -------------------------------------------------------------------------
@dataclass
class DegradationConfig:
    severity: float = 0.5
    p_brightness: float = 0.7
    p_spatial: float = 0.7
    p_frequency: float = 0.7


def make_degradation(cfg: DegradationConfig = DegradationConfig()) -> Callable:
    bri = brightness_degradation(cfg.severity)
    spa = spatial_degradation(cfg.severity)
    fre = frequency_degradation(cfg.severity)

    def _apply(img: Image.Image) -> Image.Image:
        if random.random() < cfg.p_brightness:
            img = bri(img)
        if random.random() < cfg.p_spatial:
            img = spa(img)
        if random.random() < cfg.p_frequency:
            img = fre(img)
        return img
    return _apply


# -------------------------------------------------------------------------
# Dataset-time wrappers
# -------------------------------------------------------------------------
def degraded_eval_transform(
    image_size: Tuple[int, int] = C.FACE_SIZE,
    cfg: DegradationConfig = DegradationConfig(),
) -> Callable:
    """Apply degradation on the fly during evaluation (no horizontal flip etc)."""
    deg = make_degradation(cfg)

    def _t(img: Image.Image):
        img = deg(img)
        return T.Compose([
            T.Resize(image_size),
            T.ToTensor(),
            T.Normalize(C.IMAGENET_MEAN, C.IMAGENET_STD),
        ])(img)
    return _t


def mixed_train_transform(
    image_size: Tuple[int, int] = C.FACE_SIZE,
    p_degrade: float = 0.5,
    cfg: DegradationConfig = DegradationConfig(),
) -> Callable:
    """Train-time transform that mixes original and degraded faces."""
    deg = make_degradation(cfg)
    base = standard_train_transform(image_size)

    def _t(img: Image.Image):
        if random.random() < p_degrade:
            img = deg(img)
        return base(img)
    return _t


# -------------------------------------------------------------------------
# Visual examples (for the report)
# -------------------------------------------------------------------------
def make_example_grid(
    pil_image: Image.Image,
    severities: Sequence[float] = (0.25, 0.5, 0.75),
) -> Dict[str, List[Image.Image]]:
    """Return a {family: [variant_imgs]} dict for plotting in notebook 04."""
    out: Dict[str, List[Image.Image]] = {}
    for name, fn in (
        ("brightness", brightness_degradation),
        ("spatial", spatial_degradation),
        ("frequency", frequency_degradation),
    ):
        variants = []
        for s in severities:
            f = fn(s)
            variants.append(f(pil_image.copy()))
        out[name] = variants
    return out
