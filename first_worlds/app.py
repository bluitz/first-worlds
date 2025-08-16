"""app.py

Main application: minimal scene with a cube, console-driven commands.

Controls:
- Drag with left mouse to orbit.
- Use terminal prompts to apply material styles.

This keeps UI complexity low while showing core concepts: generate textures,
apply to object, export/import recipe.
"""
from __future__ import annotations

import os
from typing import Optional

from .engine import Engine, EngineConfig
from .textures import generate_pbr_like
from .materials import MaterialParams, apply_material, pil_to_panda_texture
from .commands import infer_style_from_prompt
from .recipe import SceneRecipe, ObjectRecipe


def _build_material_from_style(style: str, size: int = 256) -> MaterialParams:
    maps = generate_pbr_like(size=size, style=style)
    return MaterialParams(
        base_color_tex=pil_to_panda_texture(maps.albedo),
        roughness_tex=pil_to_panda_texture(maps.roughness.convert("RGB")),
        metalness_tex=pil_to_panda_texture(maps.metalness.convert("RGB")),
    )


def run() -> None:
    app = Engine(EngineConfig())
    cube = app.add_unit_cube("cube")
    cube.set_pos(0, 0, 0)
    cube.set_scale(1.5)

    # Apply default material
    params = _build_material_from_style("checker")
    apply_material(cube, params)

    def apply_style(style: str) -> None:
        material = _build_material_from_style(style)
        apply_material(cube, material)

    def export_recipe(path: str) -> None:
        recipe = SceneRecipe(objects=[
            ObjectRecipe(
                name="cube",
                model_path=None,
                position=tuple(cube.get_pos()),
                hpr=tuple(cube.get_hpr()),
                scale=tuple(cube.get_scale()),
                material_style="checker",  # For simplicity, we track last style loosely
            )
        ])
        recipe.save(path)
        print(f"Saved recipe to {path}")

    def import_recipe(path: str) -> None:
        if not os.path.exists(path):
            print(f"No recipe found at {path}")
            return
        recipe = SceneRecipe.load(path)
        if not recipe.objects:
            print("Recipe has no objects")
            return
        obj = recipe.objects[0]
        cube.set_pos(*obj.position)
        cube.set_hpr(*obj.hpr)
        cube.set_scale(*obj.scale)
        apply_style(obj.material_style)
        print(f"Loaded recipe from {path}")

    print("\nType commands in the terminal while the window is open:")
    print("  style <checker|stone|metal>     -> apply a material style")
    print("  export <path.json>              -> export recipe")
    print("  import <path.json>              -> import recipe")
    print("  prompt <free text>              -> infer style from text")
    print("  quit                            -> exit app\n")

    def cli_task(task):
        try:
            if os.name == "posix":
                import select, sys
                dr, _, _ = select.select([sys.stdin], [], [], 0.0)
                if dr:
                    line = sys.stdin.readline().strip()
                else:
                    line = None
            else:
                line = None
        except Exception:
            line = None

        if line:
            parts = line.split(" ", 1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""
            if cmd == "style":
                apply_style(arg.strip() or "checker")
                print(f"Applied style: {arg}")
            elif cmd == "export":
                export_recipe(arg.strip() or "scene.recipe.json")
            elif cmd == "import":
                import_recipe(arg.strip() or "scene.recipe.json")
            elif cmd == "prompt":
                style = infer_style_from_prompt(arg)
                apply_style(style)
                print(f"Inferred style '{style}' from prompt")
            elif cmd == "quit":
                from direct.task import Task
                print("Quitting...")
                app.userExit()
                return Task.done
            else:
                print("Unknown command. Try: style, export, import, prompt, quit")
        return task.cont

    app.taskMgr.add(cli_task, "cli-task")
    app.run()


if __name__ == "__main__":
    run()
