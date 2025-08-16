import json
from first_worlds.textures import generate_pbr_like
from first_worlds.commands import infer_style_from_prompt
from first_worlds.recipe import SceneRecipe, ObjectRecipe


def test_generate_checker_maps():
    maps = generate_pbr_like(64, "checker")
    assert maps.albedo.size == (64, 64)
    assert maps.roughness.size == (64, 64)
    assert maps.metalness.size == (64, 64)
    assert maps.normal_like.size == (64, 64)


def test_infer_style_from_prompt():
    assert infer_style_from_prompt("make floor wet cobblestone at night") == "stone"
    assert infer_style_from_prompt("super shiny chrome look") == "metal"
    assert infer_style_from_prompt("unknown words") == "checker"


def test_scene_recipe_roundtrip(tmp_path):
    scene = SceneRecipe(objects=[
        ObjectRecipe(
            name="cube",
            model_path=None,
            position=(1.0, 2.0, 3.0),
            hpr=(10.0, 20.0, 30.0),
            scale=(1.0, 1.0, 1.0),
            material_style="stone",
        )
    ])
    path = tmp_path / "scene.json"
    scene.save(str(path))
    loaded = SceneRecipe.load(str(path))
    assert loaded.objects[0].name == "cube"
    assert loaded.objects[0].position == (1.0, 2.0, 3.0)
    assert loaded.objects[0].material_style == "stone"
