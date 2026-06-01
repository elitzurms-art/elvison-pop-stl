#!/usr/bin/env python3
"""
Build a STANDEE / photo-cutout from the front render of the ELVISON figure:
  - extract the figure silhouette from front_render.png (alpha)
  - extrude it into a flat board (printable)
  - map the image as a texture onto the board (colored GLB)
  - add a base slot so it stands up

Outputs:
  elvison_standee.glb  (colored, textured)
  elvison_standee.stl  (printable geometry: board + base)
"""
import numpy as np
import trimesh
from PIL import Image
from skimage import measure
from shapely.geometry import Polygon
from shapely.ops import unary_union

SRC = "/Users/elitzurserver/Projects/אלויסון/front_render.png"
TARGET_H = 150.0      # figure height in mm
THICK = 6.0           # board thickness in mm

# ---- 1. silhouette from alpha ---------------------------------------------
img = Image.open(SRC).convert("RGBA")
W, H = img.size
alpha = np.array(img)[:, :, 3]
mask = (alpha > 40).astype(float)

contours = measure.find_contours(mask, 0.5)
contours = sorted(contours, key=len, reverse=True)

# build polygons (row=y_down, col=x); convert to mm, flip Y so up is +
scale = TARGET_H / H
polys = []
for c in contours[:6]:
    if len(c) < 30:
        continue
    pts = [(col * scale, (H - row) * scale) for row, col in c]
    p = Polygon(pts)
    if p.is_valid and p.area > 4:
        polys.append(p)

sil = unary_union(polys).buffer(0.6).buffer(-0.4)   # close tiny gaps
if sil.geom_type == "MultiPolygon":
    sil = max(sil.geoms, key=lambda g: g.area)
sil = sil.simplify(0.4, preserve_topology=True)
print(f"silhouette area={sil.area:.0f}mm^2  verts={len(sil.exterior.coords)}")

# ---- 2. extrude into a board ----------------------------------------------
board = trimesh.creation.extrude_polygon(sil, height=THICK)
# board: X=width, Y=height, Z=thickness -> reorient to X=width, Z=height, Y=depth
board.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))

# ---- 3. planar UVs + texture for the GLB ----------------------------------
v = board.vertices
minx, maxx = sil.bounds[0], sil.bounds[2]
miny, maxy = sil.bounds[1], sil.bounds[3]
# after rotation: world X = poly X ; world Z = poly Y
u = (v[:, 0] - minx) / (maxx - minx)
w = 1.0 - (v[:, 2] - miny) / (maxy - miny)   # v=0 at image top
uv = np.column_stack([u, w])
mat = trimesh.visual.material.PBRMaterial(
    baseColorTexture=img, metallicFactor=0.0, roughnessFactor=0.9,
    alphaMode="MASK", alphaCutoff=0.5)
board.visual = trimesh.visual.TextureVisuals(uv=uv, material=mat, image=img)

# ---- 4. base (oval slab the board plugs into) -----------------------------
base = trimesh.creation.cylinder(radius=34, height=10, sections=64)
base.apply_transform(trimesh.transformations.scale_matrix(1.0))
base.apply_translation([(minx + maxx) / 2 - (minx + maxx) / 2, 0, 0])
# place base under the board, centered on X, board sits on top
bcx = (minx + maxx) / 2
base.apply_translation([bcx, 0, 5])
base.visual.face_colors = [20, 20, 22, 255]

# drop the board so its bottom rests on the base top (z=10)
board.apply_translation([0, 0, 10 - board.bounds[0][2]])

# ---- 5. export -------------------------------------------------------------
scene = trimesh.Scene([board, base])
glb = "/Users/elitzurserver/Projects/אלויסון/elvison_standee.glb"
scene.export(glb)

# printable STL: merge geometry (board prism + base), drop texture
solid = trimesh.util.concatenate([board.copy(), base.copy()])
try:
    u2 = trimesh.boolean.union([board.copy(), base.copy()])
    if u2 is not None and not u2.is_empty:
        solid = u2
except Exception:
    pass
stl = "/Users/elitzurserver/Projects/אלויסון/elvison_standee.stl"
solid.export(stl)

e = scene.bounds
print(f"Exported:\n  {glb}\n  {stl}")
print(f"size(mm) X={e[1][0]-e[0][0]:.0f} Y={e[1][1]-e[0][1]:.0f} Z={e[1][2]-e[0][2]:.0f}")
