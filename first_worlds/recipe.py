"""recipe.py

A simple, reproducible scene recipe format (JSON).

We store a list of objects and their material styles. This is intentionally
minimal for clarity and educational purposes.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json


@dataclass
class ObjectRecipe:
    name: str
    model_path: str | None
    position: tuple[float, float, float]
    hpr: tuple[float, float, float]
    scale: tuple[float, float, float]
    material_style: str


@dataclass
class SceneRecipe:
    objects: List[ObjectRecipe]

    def to_json(self) -> str:
        return json.dumps({
            "objects": [asdict(o) for o in self.objects]
        }, indent=2)

    @staticmethod
    def from_json(data: str) -> "SceneRecipe":
        obj = json.loads(data)
        objects = [ObjectRecipe(
            name=o.get("name", "object"),
            model_path=o.get("model_path"),
            position=tuple(o.get("position", [0, 0, 0])),
            hpr=tuple(o.get("hpr", [0, 0, 0])),
            scale=tuple(o.get("scale", [1, 1, 1])),
            material_style=o.get("material_style", "checker"),
        ) for o in obj.get("objects", [])]
        return SceneRecipe(objects=objects)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @staticmethod
    def load(path: str) -> "SceneRecipe":
        with open(path, "r", encoding="utf-8") as f:
            return SceneRecipe.from_json(f.read())
