# RastPy — a software 3D rasterizer in Python

RastPy is a 3D **software rasterizer** written from scratch in Python. It loads
models from Wavefront `.obj` files and renders them to 2D images, implementing
the entire classic rasterization pipeline — vertex transforms, perspective
projection, a z-buffer, and shading — with **no GPU and no OpenGL**. It leans
only on NumPy for the vector math and Pillow for writing the final image.

The quickest way to understand what it does: **it is the inverse of a ray
tracer.** A ray tracer shoots a ray through every pixel and asks *"which
triangle do I hit?"*. A rasterizer walks every triangle and asks *"which pixels
do I cover?"*. Same geometry, opposite direction.

---

## Features

- **`.obj` loader** — reads vertices and faces, fan-triangulates n-gons, handles
  the `v/vt/vn` face format and negative indices.
- **Full Model / View / Projection pipeline** — every vertex travels from local
  space to the screen through composable matrices.
- **`look_at` camera** — positioned and aimed with `eye` / `target` / `up`, so
  you can place the camera anywhere and orbit the model.
- **Perspective-correct z-buffer** — depth is interpolated as `1/z`, not
  linearly, so overlapping surfaces resolve correctly.
- **Barycentric coordinates** — used to interpolate depth and normals across
  each triangle.
- **Three shading modes** — flat (one color per face), Phong (per-pixel
  interpolated normals), and a Blinn-Phong specular highlight.
- **JSON scene configuration** — camera, light, model, material and output are
  all described in a single file; no code changes to switch scenes.
- **`.crtscene` converter** — turns a Chaos ray-tracer scene into a RastPy
  `.obj` + JSON pair.
- **Turntable animation** — render a 360° rotation and stitch the frames into a
  GIF.
- **76 unit tests** covering the pure geometry and shading functions.

---

## The pipeline

A single vertex passes through four spaces on its way to becoming a pixel. Each
step is one matrix:

```
local space ──[ Model ]──▶ world space ──[ View ]──▶ camera space ──[ Projection ]──▶ screen
```

- **Model** answers *where the object is* — scale, then rotate, then translate
  (`T · R · S`). This places the mesh in the scene.
- **View** answers *where the camera is*. Built by `look_at`, it does not move
  the camera; it moves the whole world so the camera sits at the origin looking
  down the `-z` axis. The `eye`/`target`/`up` basis it uses is exactly the one a
  ray tracer builds to shoot camera rays — only used in reverse.
- **Projection** answers *how perspective looks* — divides by depth so distant
  points shrink toward the center, then maps to pixels.

Once a triangle is in screen space, the rasterizer finds its bounding box, tests
each pixel for coverage, computes barycentric weights, resolves depth against the
z-buffer, and shades the surviving pixels.

One subtlety worth knowing: **normals are transformed with the inverse-transpose
of the matrix**, not the matrix itself. For pure rotation the two are identical,
but under non-uniform scaling only the inverse-transpose keeps a normal
perpendicular to its surface — otherwise the lighting skews.

---

## Project structure

```
project/
├── src/
│   ├── main.py            # entry point: render frames / assemble the GIF
│   ├── rasterizer.py      # the pipeline: barycentrics, depth, draw, render_model
│   ├── transforms.py      # rotation / translation / scaling / look_at / point & normal transforms
│   ├── camera.py          # perspective projection (project_point)
│   ├── shader.py          # Blinn-Phong lighting + smooth vertex normals
│   ├── scene_parser.py    # JSON scene -> typed dataclasses
│   ├── obj_loader.py      # Wavefront .obj parser
│   ├── triangle.py        # Triangle: normal, area, point-in-triangle test
│   ├── bbox.py            # axis-aligned bounding box
│   ├── framebuffer.py     # RGB pixel buffer -> PNG
│   └── exceptions/
│       └── CollinearTriangleBaseVectorsException.py
├── tests/                 # one test_*.py per module (unittest)
└── assets/
    ├── .obj files/        # input meshes
    ├── json_files/        # scene configs
    └── results/           # rendered output
```

---

## Requirements

- Python 3.11+
- [NumPy](https://numpy.org/)
- [Pillow](https://python-pillow.org/)

```bash
pip install numpy pillow
```

---

## Usage

Rendering is driven entirely by a JSON scene file. The minimal call is:

```python
from scene_parser import load_scene
from rasterizer import render_model

scene = load_scene("../assets/json_files/blender_cube.json")
render_model(scene)   # writes the PNG to the path in the scene's "output"
```

Run it from inside `src/` (the asset paths in the scenes are relative to it):

```bash
cd src
python main.py
```

---

## Scene format

A scene is a single JSON file with four sections — image, camera, light, model:

```json
{
  "image":  { "width": 800, "height": 600, "output": "../assets/results/cube.png" },
  "camera": { "eye": [0, 0, 5], "target": [0, 0, 0], "up": [0, 1, 0], "fov": 60 },
  "light":  { "direction": [0.6, 0.8, 1.0], "ambient": 0.15 },
  "model": {
    "path": "../assets/.obj files/cube.obj",
    "shading": "flat",
    "base_color": [80, 160, 220],
    "shininess": 32,
    "specular_color": [255, 255, 255],
    "transform": {
      "translation": [0, 0, 0],
      "rotation": [25, 35, 0],
      "scale": [1, 1, 1]
    }
  }
}
```

- **camera** — `eye` is the position, `target` the point it looks at, `up` the
  up direction, `fov` the vertical field of view in degrees.
- **light** — `direction` points toward the light; `ambient` is the floor
  brightness a surface keeps when facing away from it.
- **model.transform** — `rotation` is in degrees (x, y, z); optional fields
  default to identity (no move, no rotation, unit scale).
- **model.material** — `base_color`, `shininess` and `specular_color` control
  the surface appearance.

Change `fov`, `eye`, `base_color` or the resolution and the render follows — the
JSON drives everything.

---

## Shading modes

Pick the mode with `"shading"` in the model block:

- **`flat`** — one lit color per triangle from its face normal. Best for shapes
  with sharp edges (a cube): the faces stay crisp.
- **`phong`** — interpolates per-vertex normals across the triangle and lights
  every pixel, giving smooth gradients. Best for curved shapes (a sphere).

Both add a Blinn-Phong specular highlight controlled by `shininess`. Rule of
thumb: **cube → flat, sphere → phong.**

---

## Rendering an animation

`main.py` contains a turntable loop: rotate the model 30° per frame for 12
frames, render each to a PNG, then stitch them into a looping GIF with Pillow.
Uncomment the render loop to regenerate the frames, then run the GIF assembly.

---

## Tests

The suite covers the pure geometry and shading functions — the parts with a
single provable right answer (barycentric weights, perspective-correct depth,
`look_at`, projection, normals, `.obj` parsing). Run from the project root:

```bash
python -m unittest discover -s tests -v
```

---

## Scope

RastPy implements the classic pipeline end to end, but deliberately stops short
of a production renderer. It does **not** do near-plane clipping (vertices very
close to the camera are kept out of frame by the camera offset instead), shadows,
or anti-aliasing, and it uses a fixed distant-viewer direction for the specular
term. These are conscious simplifications, not missing pieces.

---

## Author

**Nikolay Georgiev** — Software Engineering, Sofia University (FMI)
GitHub: [NGeorgiev12](https://github.com/NGeorgiev12)