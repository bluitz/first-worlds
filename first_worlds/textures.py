"""textures.py

Procedural texture generators for learning purposes.

This module provides tiny, pure-Python utilities to generate simple
color, checkerboard and noise images that can be used as stand-ins for PBR
maps (albedo/baseColor, roughness, metalness, normal-like height shading).

If Pillow is unavailable, we fall back to minimal stubs sufficient for tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import math
import random

try:  # Optional Pillow dependency
    from PIL import Image, ImageFilter
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

    class _FakeImage:
        def __init__(self, size: tuple[int, int], mode: str = "RGB") -> None:
            self.size = size
            self.mode = mode
        def convert(self, mode: str):
            self.mode = mode
            return self
        def filter(self, *_args, **_kwargs):
            return self
        def point(self, *_args, **_kwargs):
            return self

    class Image:  # type: ignore
        @staticmethod
        def new(_mode: str, size: tuple[int, int], *_args, **_kwargs):
            return _FakeImage(size=size, mode=_mode)

    class ImageFilter:  # type: ignore
        GaussianBlur = object()
        FIND_EDGES = object()


Color = Tuple[int, int, int]


@dataclass
class TextureMaps:
    """A small container for PBR-like texture maps.

    - albedo: base color texture (RGB)
    - roughness: grayscale; higher = more matte
    - metalness: grayscale; higher = more metallic
    - normal_like: grayscale; fake surface detail (we won't do true tangent-space normals)
    """

    albedo: "Image"
    roughness: "Image"
    metalness: "Image"
    normal_like: "Image"


def make_solid(size: int, color: Color):
    """Create a solid color image of size (size x size).

    Note: In fallback mode this returns a minimal stub that only exposes `.size`.
    """
    return Image.new("RGB", (size, size), color)


def make_checkerboard(size: int, squares: int, color_a: Color, color_b: Color):
    """Generate a checkerboard image using pure Python loops.
    """
    if HAVE_PIL:
        img = Image.new("RGB", (size, size), color_a)
        px = img.load()
        block = max(1, size // squares)
        for y in range(size):
            for x in range(size):
                if ((x // block) + (y // block)) % 2 == 0:
                    px[x, y] = color_a
                else:
                    px[x, y] = color_b
        return img
    # Fallback stub
    return Image.new("RGB", (size, size))


def make_value_noise(size: int, octaves: int = 4, seed: int | None = None):
    """Generate simple value noise as a grayscale image without numpy.

    This is not Perlin/Simplex. It's intentionally simple: random grid values
    bilinearly interpolated, combined over a few octaves.
    """
    rng = random.Random(seed)

    def lerp(a: float, b: float, t: float) -> float:
        return a * (1.0 - t) + b * t

    def noise_grid(step: int):
        grid = [[rng.random() for _ in range(step + 1)] for _ in range(step + 1)]
        out = [[0.0 for _ in range(size)] for _ in range(size)]
        for yi in range(size):
            y = yi * step / max(1, size - 1)
            y0 = int(math.floor(y))
            y1 = min(step, y0 + 1)
            ty = y - y0
            for xi in range(size):
                x = xi * step / max(1, size - 1)
                x0 = int(math.floor(x))
                x1 = min(step, x0 + 1)
                tx = x - x0
                v00 = grid[y0][x0]
                v10 = grid[y0][x1]
                v01 = grid[y1][x0]
                v11 = grid[y1][x1]
                a = lerp(v00, v10, tx)
                b = lerp(v01, v11, tx)
                out[yi][xi] = lerp(a, b, ty)
        return out

    img = [[0.0 for _ in range(size)] for _ in range(size)]
    amplitude = 1.0
    frequency = 1
    for _ in range(octaves):
        step = max(1, size // (4 * frequency))
        ng = noise_grid(step)
        for y in range(size):
            for x in range(size):
                img[y][x] += amplitude * ng[y][x]
        amplitude *= 0.5
        frequency *= 2

    # Normalize to 0..255
    min_v = min(min(row) for row in img)
    max_v = max(max(row) for row in img)
    scale = 255.0 / (max_v - min_v + 1e-6)

    if HAVE_PIL:
        out = Image.new("L", (size, size))
        px = out.load()
        for y in range(size):
            for x in range(size):
                px[x, y] = int((img[y][x] - min_v) * scale)
        return out
    return Image.new("L", (size, size))


def generate_pbr_like(size: int, style: str, seed: int | None = None) -> TextureMaps:
    """Generate a set of simple PBR-like maps by style keyword.

    Supported styles:
    - "checker": high-contrast checkerboard albedo, mid roughness, zero metalness.
    - "stone": noisy albedo with blurred roughness and subtle height/normal-like details.
    - "metal": gray albedo, high metalness, low roughness.
    """
    style = style.lower().strip()
    if style == "checker":
        albedo = make_checkerboard(size, squares=8, color_a=(220, 220, 220), color_b=(40, 40, 40))
        roughness = Image.new("L", (size, size), 160)
        metalness = Image.new("L", (size, size), 0)
        normal_like = Image.new("L", (size, size), 128)
        return TextureMaps(albedo, roughness, metalness, normal_like)

    if style == "stone":
        base = make_value_noise(size, octaves=4, seed=seed)
        if HAVE_PIL:
            albedo = Image.merge("RGB", (base, base.point(lambda p: min(255, p + 15)), base))  # type: ignore[attr-defined]
            roughness = base.filter(ImageFilter.GaussianBlur(radius=1.5))
            metalness = Image.new("L", (size, size), 0)
            normal_like = base.filter(ImageFilter.FIND_EDGES).point(lambda p: min(255, int(p * 0.8)))
        else:
            albedo = Image.new("RGB", (size, size))
            roughness = Image.new("L", (size, size))
            metalness = Image.new("L", (size, size))
            normal_like = Image.new("L", (size, size))
        return TextureMaps(albedo, roughness, metalness, normal_like)

    if style == "metal":
        albedo = Image.new("RGB", (size, size), (128, 128, 128))
        roughness = Image.new("L", (size, size), 50)
        metalness = Image.new("L", (size, size), 200)
        normal_like = Image.new("L", (size, size), 128)
        return TextureMaps(albedo, roughness, metalness, normal_like)

    # Fallback
    return generate_pbr_like(size=size, style="checker", seed=seed)
