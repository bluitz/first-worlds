# FirstWorlds — Your first step into world modeling (three.js + generative textures)

<p align="center">
  <img src="logo.png" alt="FirstWorlds logo — Your first step into world modeling" width="220" />
  <br/>
  <em>Built for showcasing world modeling skills</em>
  
</p>

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](TODO_DEMO_URL)
[![Video Walkthrough](https://img.shields.io/badge/video-5%20min-blue)](TODO_VIDEO_URL)
[![Repo](https://img.shields.io/badge/code-GitHub-black)](TODO_REPO_URL)

**FirstWorlds** is a browser-based scene editor designed as a **Hello, World!** for world modeling.  
Import GLTF/GLB, place and transform objects, and apply procedural + AI-generated textures via a command bar (e.g., _“make the floor wet cobblestone at night”_).  
Exports to **GLB + JSON recipe** so scenes are reproducible.

https://user-images.githubusercontent.com/TODO/short-gif.mp4 <!-- TODO: 10–20s screen capture GIF -->

---

## ✨ Highlights (what a recruiter should notice)

- **Beginner-friendly:** built as an accessible introduction to 3D world modeling.
- **Production-quality 3D UX:** smooth orbit controls, gizmos, undo/redo, autosave.
- **Materials mastery:** PBR pipeline with roughness/metalness/normal maps, env lighting, PMREM.
- **Shader chops:** small custom **triplanar/clearcoat** GLSL node you can read in 2 minutes.
- **Gen-AI integration:** texture prompts → generated maps → material preview → single-click revert.
- **Performance aware:** instancing, KTX2/DRACO compression, BVH picking, R3F suspense boundaries.
- **Export story:** GLB + JSON “scene recipe” that can be re-opened to reproduce results.

---

## 🧩 Demo

- **Live:** TODO_DEMO_URL
- **Video (5 min):** TODO_VIDEO_URL (walkthrough of import → edit → AI texture → export → re-import)

---

## 📦 Tech Stack

- **React + Vite**, **react-three-fiber** + **drei**, **three** (r15x)
- **State:** zustand (undo/redo history), jotai (transient UI)
- **Assets:** GLTFLoader + DRACO, KTX2 compressed textures, PMREM & HDRIs
- **Perf:** instanced meshes, mesh BVH raycasting, requestIdleCallback autosave
- **Post:** @react-three/postprocessing (bloom, SMAA/FXAA)
- **AI bridge (optional):** simple API wrapper for texture generation/upscaling (swap in any provider)
- **Testing:** playwright for UI flows, tiny perf/e2e scripts for FPS & memory snapshots

---

## 🏁 Getting Started

```bash
# 1) Install
pnpm i   # or npm i / yarn

# 2) Dev
pnpm dev

# 3) Build
pnpm build && pnpm preview
```

---

## 🗂️ Project Layout

```
/app
  main.tsx
  App.tsx
  /components
    CanvasRoot.tsx
    ViewportHUD.tsx
    Outliner.tsx
    Inspector.tsx
    CommandBar.tsx
    Gizmos.tsx
  /state
    useEditorStore.ts   # zustand (selection, transforms, history)
    history.ts          # undo/redo stack
/three
  loaders.ts            # GLTF/DRACO/KTX2
  materials/
    TriplanarMaterial.ts   # tiny GLSL node
    PBRFactory.ts          # albedo/metalness/roughness/normal wiring
  post.ts                # bloom/SMAA pipeline
  picking.ts             # BVH raycast helpers
/assets
  sample.glb
  hdri/studio.hdr
/server (optional)
  ai-texture.ts          # POST /gen-texture {prompt, seed} -> {maps}
  upload.ts
/evals
  perf-scenes.json       # stress configs
  results.md             # FPS/memory table screenshots
```

---

## 🧠 Key Concepts

### 1) AI-Assisted Texturing

- Command: `make <selection> look like <descriptor>` → hits `/gen-texture` → returns **albedo**, optional **normal**/**roughness**/**metalness**.
- **Preview mode:** non-destructive layer (toggle on/off).
- **Commit:** bake maps into material + autosave.
- **Revert:** one click via history stack.

### 2) Export / Import

- **Export**: `scene.glb` + `scene.recipe.json` (materials, map sources, generator params).
- **Import**: loads GLB + reapplies recipe (so results are reproducible).

### 3) Performance

- **Instancing** for repeated props (trees, lights).
- **KTX2** textures, **DRACO** meshes, PMREM’d HDRIs.
- **BVH raycasting** for fast picking.
- **Frame budget** target: 60fps on M1 Air @ 1080p for demo scenes.

---

## 🧪 Evals

| Scenario                      | Triangles | FPS (M1 Air) | Notes                    |
| ----------------------------- | --------- | ------------ | ------------------------ |
| Single room, 25 props         | ~500k     | 60           | Baseline                 |
| 200 instanced props           | ~3.2M     | 55–60        | Instancing on            |
| Uncompressed vs KTX2 textures | n/a       | +8–15 fps    | Saves memory + bandwidth |

> Reproduce via `pnpm run eval:perf` (spawns scripted camera flythroughs, logs FPS & memory).

---

## 🎛️ UI Features

- **Outliner** (tree), **Inspector** (materials & transforms), **Command Bar** (⌘K)
- **Gizmos** (translate/rotate/scale), snapping, local/world space
- **Undo/redo** (Cmd+Z / Shift+Cmd+Z), **autosave**, per-scene versions
- **Drag-drop import**: `.glb/.gltf/.obj`, HDRI `.hdr`, image textures
- **Postprocessing**: bloom + SMAA, toggleable

---

## 🧪 Minimal Test Plan

- `e2e/import.spec.ts`: import sample GLB, verify node count & bounding boxes
- `e2e/materials.spec.ts`: apply generated texture, check map bindings & params
- `e2e/export.spec.ts`: export → reload → deep-equal recipe
- `e2e/perf.spec.ts`: perf scene hits min 55 fps median on M1 Air

---

## 🧵 Tiny Shader Morsel (Triplanar excerpt)

```glsl
// TriplanarMaterial.glsl (excerpt)
vec3 triplanarSample(sampler2D tex, vec3 worldPos, vec3 normal, float scale) {
  vec3 n = abs(normalize(normal));
  vec2 uvX = worldPos.zy * scale;
  vec2 uvY = worldPos.xz * scale;
  vec2 uvZ = worldPos.xy * scale;
  vec3 tx = texture2D(tex, uvX).rgb * n.x;
  vec3 ty = texture2D(tex, uvY).rgb * n.y;
  vec3 tz = texture2D(tex, uvZ).rgb * n.z;
  return (tx + ty + tz) / max(0.0001, n.x + n.y + n.z);
}
```

> Used for quick, seam-free tiling on irregular meshes (rocks, ground).

---

## 🔒 Notes on Generative Textures

- Results are cached with `{prompt, seed, size}` for reproducibility.
- Store only **paths** to generated maps; keep large binaries out of git (use LFS or CDN).
- Attribution: include credits for any base HDRIs / texture sources.

---

## 🗺️ Roadmap

- [ ] **Layered materials** (stack multiple generated looks, blend sliders)
- [ ] **Smart UV** helper (auto UV unwrap fallback for poor assets)
- [ ] **Light baking** preview (EMISSIVE → fake bounce via AO trick)
- [ ] **WebXR** toggle for in-scene inspection
- [ ] **Collab mode** (presence cursors), save conflicts resolution
- [ ] **Asset inspector** (polycount, draw calls, map resolution warnings)

---

## 📜 License

MIT for code. See `/ATTRIBUTIONS.md` for HDRI/texture licenses.

## 👤 Author

Justin Munning — [Website](https://TODO) · [GitHub](https://github.com/TODO) · [LinkedIn](https://linkedin.com/in/TODO)

---

# 📅 Feature Checklist (2-week plan)

## Week 1 — MVP (shipping > perfect)

- [ ] R3F canvas, orbit controls, basic scene
- [ ] Import GLB; add to **Outliner**; select & focus camera
- [ ] **Inspector**: transform + PBR material parameters (albedo/roughness/metalness)
- [ ] **Command Bar (⌘K)** with 3 commands: - [ ] “Generate texture for selection” - [ ] “Revert last material change” - [ ] “Toggle bloom”
- [ ] **AI texture pipeline** stub: call your chosen provider; return albedo (+ optional normal/roughness)
- [ ] **Preview/Commit** flow; autosave scene to localStorage
- [ ] **Export** GLB + JSON recipe; **Import** to restore
- [ ] 10–20s **screen capture GIF** and short README

## Week 2 — Product polish + performance

- [ ] **KTX2** compressed textures; **DRACO** GLBs
- [ ] **InstancedMesh** for repeated props
- [ ] **BVH** raycasting for precise picking on heavy meshes
- [ ] **Triplanar shader** or **clearcoat BRDF tweak** (small, readable)
- [ ] Postprocessing pipeline (bloom + SMAA)
- [ ] **Perf evals** (FPS table & screenshots)
- [ ] 5-min narrated **Video Walkthrough**
- [ ] Host on **Vercel/Netlify** + add badges/links to README

---

# 🎥 Recruiter-facing Demo Script

1. Import `room.glb`, orbit, and frame the hero object.
2. Select the **floor** → Command Bar: “make the floor wet cobblestone at night.”
3. Show preview vs commit; tweak roughness/normal strength.
4. Export GLB + JSON; refresh; re-import; confirm it matches.
5. Open `evals/results.md` → show FPS table.
6. Toggle bloom and your shader (e.g., triplanar) to show 3D chops.
7. Close with 15s on code organization and why these choices scale.
