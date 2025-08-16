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

try:  # Optional Pillow dependency for combining maps
	from PIL import Image
	HAVE_PIL = True
except Exception:
	HAVE_PIL = False


@dataclass
class MaterialParams:
	base_color_tex: Optional[Texture] = None
	# simplepbr expects a single MetalRoughness texture where
	#   G channel = roughness, B channel = metallic (R/A unused)
	metal_roughness_tex: Optional[Texture] = None


def pil_to_panda_texture(pil_image) -> Texture:
	"""Convert a Pillow image to a Panda3D Texture (RGBA)."""
	rgba = pil_image.convert("RGBA")
	width, height = rgba.size
	pnm = PNMImage(width, height, 4)
	data = rgba.tobytes()
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


def combine_metal_roughness_to_texture(roughness_img, metalness_img, size: int | None = None) -> Optional[Texture]:
	"""Pack roughness (G) and metalness (B) into one RGBA image for simplepbr.

	Returns a Panda3D Texture, or None if Pillow is unavailable.
	"""
	if not HAVE_PIL:
		return None
	# Ensure both are single-channel L images and same size
	r = Image.new("L", roughness_img.size, 255)
	g = roughness_img.convert("L")
	b = metalness_img.convert("L")
	a = Image.new("L", roughness_img.size, 255)
	combo = Image.merge("RGBA", (r, g, b, a))
	return pil_to_panda_texture(combo)


def apply_material(nodepath, params: MaterialParams) -> None:
	"""Attach textures to a NodePath using simplepbr's expected shader inputs.

	Expected inputs:
	- p3d_TextureBaseColor: base/albedo map (RGBA/RGB)
	- p3d_TextureMetalRoughness: packed map where G=roughness, B=metallic
	"""
	if params.base_color_tex is not None:
		nodepath.set_shader_input("p3d_TextureBaseColor", params.base_color_tex)
	if params.metal_roughness_tex is not None:
		nodepath.set_shader_input("p3d_TextureMetalRoughness", params.metal_roughness_tex)
