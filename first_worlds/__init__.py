"""FirstWorlds (Python)

A minimal, beginner-friendly world modeling sandbox implemented with Panda3D.
This package focuses on clarity and pedagogy over features and performance.

Key modules:
- engine: Thin wrapper around Panda3D scene setup.
- textures: Small image generators (checkerboard, noise) for PBR-like maps.
- materials: Helper for applying textures/parameters to Panda3D nodes.
- commands: Tiny text-to-action mapping for materials.
- recipe: Save/load scene configuration in a reproducible JSON format.
- history: Undo/redo stack for editor actions.

Run the app:
    python -m first_worlds.app

Run tests:
    pytest -q
"""

__all__ = [
    "__version__",
]

__version__ = "0.1.0"
