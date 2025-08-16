"""engine.py

Minimal Panda3D engine wrapper for learning.

- Creates a basic ShowBase with orbit-like mouse controls.
- Provides helpers to add a primitive cube and load a GLTF/GLB model.
- Applies simple PBR using simplepbr.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from panda3d.core import Vec3, Filename, NodePath, AmbientLight, DirectionalLight
from direct.showbase.ShowBase import ShowBase
import simplepbr

try:
    from panda3d_gltf import GLTFLoader
    HAVE_GLTF = True
except Exception:
    HAVE_GLTF = False


@dataclass
class EngineConfig:
    window_title: str = "FirstWorlds (Python)"
    background_color: tuple[float, float, float] = (0.05, 0.05, 0.07)


class Engine(ShowBase):
    def __init__(self, config: EngineConfig | None = None) -> None:
        self._config = config or EngineConfig()
        ShowBase.__init__(self)
        self.disableMouse()  # we set a simple orbit camera manually
        self.win.set_clear_color(self._config.background_color)

        # Initialize simple PBR pipeline
        simplepbr.init(base=self, use_normal_maps=False)

        # Setup camera and basic lights
        self.cam.set_pos(6, -10, 6)
        self.cam.look_at(0, 0, 0)
        self._setup_lights()

        # Simple mouse-drag orbit
        self._is_dragging = False
        self._last_mouse = None
        self.accept("mouse1", self._on_mouse1_down)
        self.accept("mouse1-up", self._on_mouse1_up)
        self.taskMgr.add(self._mouse_task, "mouse-task")

    def _setup_lights(self) -> None:
        amb = AmbientLight("ambient")
        amb.set_color((0.35, 0.35, 0.4, 1))
        amb_np = self.render.attach_new_node(amb)
        self.render.set_light(amb_np)

        sun = DirectionalLight("sun")
        sun.set_color((0.9, 0.9, 0.85, 1))
        sun_np = self.render.attach_new_node(sun)
        sun_np.set_hpr(45, -45, 0)
        self.render.set_light(sun_np)

    def _on_mouse1_down(self) -> None:
        self._is_dragging = True
        self._last_mouse = None

    def _on_mouse1_up(self) -> None:
        self._is_dragging = False
        self._last_mouse = None

    def _mouse_task(self, task):
        if self._is_dragging and self.mouseWatcherNode.has_mouse():
            mpos = self.mouseWatcherNode.get_mouse()
            if self._last_mouse is None:
                self._last_mouse = (mpos.get_x(), mpos.get_y())
            else:
                dx = mpos.get_x() - self._last_mouse[0]
                dy = mpos.get_y() - self._last_mouse[1]
                self._last_mouse = (mpos.get_x(), mpos.get_y())
                self._orbit_camera(dx, dy)
        return task.cont

    def _orbit_camera(self, dx: float, dy: float) -> None:
        cam = self.cam
        pivot = Vec3(0, 0, 0)
        vec = cam.get_pos() - pivot
        # yaw around Z, pitch around X
        cam.set_pos((vec.x - dx * 5, vec.y, vec.z + dy * 5))
        cam.look_at(pivot)

    def add_unit_cube(self, name: str = "cube") -> NodePath:
        from panda3d.core import GeomNode, GeomVertexData, GeomVertexFormat, GeomVertexWriter, GeomTristrips, Geom, GeomVertexReader
        # For simplicity, use built-in model
        cube = self.loader.loadModel("models/box")
        np = cube.reparent_to(self.render)
        np.set_name(name)
        return np

    def load_model(self, path: str, name: Optional[str] = None) -> Optional[NodePath]:
        if HAVE_GLTF and path.lower().endswith((".gltf", ".glb")):
            node = GLTFLoader.load_model(Filename.from_os_specific(path))
        else:
            try:
                node = self.loader.loadModel(path)
            except Exception:
                node = None
        if node is None:
            return None
        np = node.reparent_to(self.render)
        if name:
            np.set_name(name)
        return np
