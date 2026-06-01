#!/usr/bin/env python3
"""
Figure-SHAPED cutout/standee (NOT a box): silhouette cut to the figure outline.
Front plate = front photo, back plate = back photo, on a base.
Outputs elvison_standee.glb (textured) + elvison_standee.stl (printable).
"""
import numpy as np
import trimesh
from PIL import Image
from skimage import measure
from shapely.geometry import Polygon
from shapely.ops import unary_union

P = "/Users/elitzurserver/Projects/אלויסון/"
front_rgba = np.asarray(Image.open(P + "front_cutout.png"))
mask = front_rgba[:, :, 3] > 100
H, W = mask.shape

# ---- silhouette polygon in PIXEL coords (x=col, y=row, y down) -------------
cs = sorted(measure.find_contours(mask.astype(float), 0.5), key=len, reverse=True)
polys = []
for c in cs[:5]:
    if len(c) < 40:
        continue
    pts = [(col, row) for row, col in c]
    pg = Polygon(pts)
    if pg.is_valid and pg.area > 10:
        polys.append(pg)
sil = unary_union(polys)
if sil.geom_type == "MultiPolygon":
    sil = max(sil.geoms, key=lambda g: g.area)
sil = sil.buffer(1.5).buffer(-1.5).simplify(1.0, preserve_topology=True)

colmin, rowmin, colmax, rowmax = sil.bounds
TARGET_H = 120.0
s = TARGET_H / (rowmax - rowmin)                  # mm per pixel
print(f"figure px: {colmax-colmin:.0f}x{rowmax-rowmin:.0f} -> "
      f"{(colmax-colmin)*s:.0f}x{TARGET_H:.0f} mm  verts={len(sil.exterior.coords)}")

front_img = Image.open(P + "front_cutout.png").convert("RGB")
back_img = Image.open(P + "back_cutout.png").convert("RGB")
T = 3.0


def plate(image, y_shift, flip_u):
    m = trimesh.creation.extrude_polygon(sil, height=T)
    V = m.vertices.copy()
    col, row, z = V[:, 0], V[:, 1], V[:, 2]
    u = col / W
    w = row / H
    if flip_u:
        u = 1.0 - u
    uv = np.column_stack([u, w])
    # reorient: X=width, Z=height(up, bottom at 0), Y=thickness
    m.vertices = np.column_stack([(col - colmin) * s, z + y_shift, (rowmax - row) * s])
    mat = trimesh.visual.material.PBRMaterial(
        baseColorTexture=image, metallicFactor=0.0, roughnessFactor=1.0)
    m.visual = trimesh.visual.TextureVisuals(uv=uv, material=mat, image=image)
    return m

front_plate = plate(front_img, y_shift=T, flip_u=False)
back_plate = plate(back_img, y_shift=0.0, flip_u=True)

w_mm = (colmax - colmin) * s
base = trimesh.creation.box(extents=[w_mm * 0.85, 2 * T + 16, 9])
base.apply_translation([w_mm / 2, 0, -4.5])
base.visual.face_colors = [13, 13, 13, 255]

scene = trimesh.Scene([front_plate, back_plate, base])
scene.export(P + "elvison_standee.glb")
solid = trimesh.util.concatenate([front_plate.copy(), back_plate.copy(), base.copy()])
solid.export(P + "elvison_standee.stl")
b = scene.bounds
print(f"Exported elvison_standee.glb / .stl")
print(f"size(mm) W={b[1][0]-b[0][0]:.0f} D={b[1][1]-b[0][1]:.0f} H={b[1][2]-b[0][2]:.0f}")
