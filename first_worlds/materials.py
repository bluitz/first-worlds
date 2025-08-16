"""materials.py

Helpers to apply simple PBR-like parameters to Panda3D nodes.

We use `simplepbr` for a basic PBR effect. Textures are provided as Pillow
images and converted to Panda3D textures. For a beginner-friendly approach,
we keep parameters minimal and avoid advanced shader graphs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from panda3d.core import Texture, PNMImage, SamplerState


@dataclass
class MaterialParams:
    base_color_tex: Optional[Texture] = None
    roughness_tex: Optional[Texture] = None
    metalness_tex: Optional[Texture] = None


def pil_to_panda_texture(pil_image) -> Texture:
    """Convert a Pillow image to a Panda3D Texture (RGBA)."""
    rgba = pil_image.convert("RGBA")
    width, height = rgba.size
    pnm = PNMImage(width, height, 4)
    data = rgba.tobytes()
    # PNMImage expects rows from bottom to top; we can fill directly via setXelA
    # for simplicity, we iterate Python-side (fine for small textures)
    idx = 0
    for y in range(height):
        for x in range(width):
            r = data[idx] / 255.0
            g = data[idx + 1] / 255.0
            b = data[idx + 2] / 255.0
            a = data[idx + 3] / 255.0
            pnm.setXelA(x, height - 1 - y, r, g, b, a)
            idx += 4
    tex = Texture()
    tex.load(pnm)
    tex.set_magfilter(SamplerState.FT_linear)
    tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)
    return tex


def apply_material(nodepath, params: MaterialParams) -> None:
    """Attach textures to a NodePath in a simple PBR-friendly way.

    Assumes `simplepbr.init()` was called on the ShowBase app.
    """
    if params.base_color_tex is not None:
        nodepath.setTexture(params.base_color_tex, 1)
    if params.roughness_tex is not None:
        nodepath.setTexture(params.roughness_tex, 1)
        nodepath.set_shader_input("roughnessTex", params.roughness_tex)
    if params.metalness_tex is not None:
        nodepath.setTexture(params.metalness_tex, 1)
        nodepath.set_shader_input("metalnessTex", params.metalness_tex)
