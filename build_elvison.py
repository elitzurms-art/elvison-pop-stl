#!/usr/bin/env python3
"""
Procedural blocky (Minecraft/voxel-style) figure of the "ELVISON" YouTuber Pop,
tuned to resemble the reference renders AND fully colored.

Outputs:
  - elvison.stl        : watertight geometry (single color) for normal printing
  - elvison_color.glb  : COLORED model (viewer / multi-color printing)

Coordinate system: Z = up, X = right, Y = depth (forward = +Y). Units = mm.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon

# ---- palette (RGBA 0-255) — exact values from the spec-sheet COLOR PALETTE --
#   #00E5FF cyan | #0D0D0D / #1A1A1A blacks | #8B4513 brown | #F5C78E skin
#   #E60000 red  | #FFFFFF white
SKIN   = [245, 199, 142, 255]    # #F5C78E
BLACK  = [13, 13, 13, 255]       # #0D0D0D  black suit / base
EYE    = [13, 13, 13, 255]       # #0D0D0D  glossy black eyes
BROWN  = [139, 69, 19, 255]      # #8B4513  hair
BROW   = [110, 54, 15, 255]      # darker brown brows
CYAN   = [0, 229, 255, 255]      # #00E5FF  suit pixels + E logo
WHITE  = [255, 255, 255, 255]    # #FFFFFF  shoe soles
RED    = [230, 0, 0, 255]        # #E60000  play button
GREY   = [26, 26, 26, 255]       # #1A1A1A  camera

GROUPS = {}      # color-key -> (rgba, [meshes])


def put(rgba, mesh):
    key = tuple(rgba)
    GROUPS.setdefault(key, (rgba, []))[1].append(mesh)


def box(size, center):
    b = trimesh.creation.box(extents=size)
    b.apply_translation(center)
    return b


def add(rgba, size, center):
    put(rgba, box(size, center))


def disc(radius, thick, center, axis="y", sections=40):
    c = trimesh.creation.cylinder(radius=radius, height=thick, sections=sections)
    if axis == "y":
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    elif axis == "x":
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation(center)
    return c


# ============================================================================
# BASE — black disc + red play-button tab + white triangle
# ============================================================================
base = trimesh.creation.cylinder(radius=38, height=10, sections=72)
base.apply_translation([0, 0, 5])
put(BLACK, base)

add(RED, (26, 16, 16), (0, -34, 10))
tri = Polygon([(-4, -4), (-4, 4), (5, 0)])
play = trimesh.creation.extrude_polygon(tri, height=6)
play.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
play.apply_translation([0, -34 - 8.5, 10])
put(WHITE, play)

# ============================================================================
# LEGS + white soles
# ============================================================================
leg_h, leg_w, leg_d = 32, 18, 19
leg_z = 10 + leg_h / 2
add(BLACK, (leg_w, leg_d, leg_h), (-11, 0, leg_z))
add(BLACK, (leg_w, leg_d, leg_h), (+11, 0, leg_z))
add(WHITE, (leg_w + 4, leg_d + 7, 7), (-11, -2, 10 + 4))
add(WHITE, (leg_w + 4, leg_d + 7, 7), (+11, -2, 10 + 4))

# ============================================================================
# TORSO + arms (black suit)
# ============================================================================
torso_h, torso_w, torso_d = 40, 48, 27
torso_z = 10 + leg_h + torso_h / 2
torso_top = 10 + leg_h + torso_h
add(BLACK, (torso_w, torso_d, torso_h), (0, 0, torso_z))

arm_w, arm_d = 14, 15
add(BLACK, (arm_w, arm_d, 38), (torso_w / 2 + arm_w / 2 - 2, 0, torso_top - 19))
rx = -(torso_w / 2 + arm_w / 2 - 2)
add(BLACK, (arm_w, arm_d, 20), (rx, 0, torso_top - 10))
add(BLACK, (arm_w, arm_d, 26), (rx, 5, torso_top + 8))
# skin hands
add(SKIN, (arm_w + 1, arm_d + 1, 7), (torso_w / 2 + arm_w / 2 - 2, 0, torso_top - 38 + 3))
add(SKIN, (arm_w + 1, arm_d + 1, 7), (rx, 6, torso_top + 8 + 13))

# raised cyan pixel pattern on the suit ------------------------------------
fy = torso_d / 2
px = 5.5
pat = [(-1, 2), (0, 1), (1, 1), (1, 0), (0, 0), (-1, -1), (0, -1), (-2, 0), (2, -1)]
for gx, gz in pat:
    add(CYAN, (px, 2.5, px), (gx * px * 1.15, fy, torso_z + gz * px * 1.15))
for (lx, gz) in [(-11, 1), (-11, -1), (11, 0), (11, -2)]:
    add(CYAN, (px, 2.5, px), (lx + 3, leg_d / 2, leg_z + gz * px * 1.2))

# ============================================================================
# CAMERA (grey/black) in the raised hand
# ============================================================================
cam_x, cam_z = rx, torso_top + 24
add(GREY, (22, 24, 19), (cam_x, 9, cam_z))
put(BLACK, disc(8, 15, (cam_x, 9 + 18, cam_z), axis="y", sections=36))
add(RED, (7, 7, 9), (cam_x + 4, 5, cam_z + 13))
add(GREY, (10, 4, 7), (cam_x, 9, cam_z + 12))

# ============================================================================
# NECK + HEAD (skin)
# ============================================================================
neck_h = 5
add(SKIN, (22, 17, neck_h), (0, 0, torso_top + neck_h / 2))

head_w, head_d, head_h = 64, 58, 60
head_z = torso_top + neck_h + head_h / 2
head_top = torso_top + neck_h + head_h
put(SKIN, box((head_w, head_d, head_h), (0, 0, head_z)))
fy_head = head_d / 2

# ---- FACE: eyes, brows, nose ----------------------------------------------
eye_z = head_z - 2
for ex in (-15, 15):
    put(EYE, disc(9.5, 4, (ex, fy_head - 0.5, eye_z), axis="y", sections=44))
add(BROW, (13, 3, 4), (-15, fy_head, eye_z + 13))
add(BROW, (11, 3, 3), (15, fy_head, eye_z + 12))
nose = Polygon([(-3, 0), (3, 0), (0, -6)])
n = trimesh.creation.extrude_polygon(nose, height=4)
n.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
n.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
n.apply_translation([0, fy_head, eye_z - 7])
put(SKIN, n)

# ============================================================================
# HAIR (brown, swept blocky fringe)
# ============================================================================
hair_top_z = head_top + 7
add(BROWN, (head_w + 5, head_d + 5, 16), (0, 0, hair_top_z))
add(BROWN, (11, head_d + 3, 30), (-(head_w / 2 + 1), 0, head_top - 8))
add(BROWN, (11, head_d + 3, 30), (+(head_w / 2 + 1), 0, head_top - 8))
heights = [22, 17, 12, 9, 7]
for i, gx in enumerate(np.linspace(-26, 26, 5)):
    h = heights[i]
    add(BROWN, (12.5, 9, h), (gx, fy_head - 3, head_top - h / 2 + 3))
add(BROWN, (14, 14, 9), (-12, 6, hair_top_z + 9))
add(BROWN, (11, 11, 7), (10, -4, hair_top_z + 8))

# ============================================================================
# "E" logo on the BACK of the head (cyan)
# ============================================================================
by = -(head_d / 2)
e_cx, e_cz, t = 0, head_z + 2, 5
add(CYAN, (t, 3, 30), (e_cx - 9, by, e_cz))
add(CYAN, (22, 3, t), (e_cx, by, e_cz + 13))
add(CYAN, (18, 3, t), (e_cx - 2, by, e_cz))
add(CYAN, (22, 3, t), (e_cx, by, e_cz - 13))

# ============================================================================
# Assemble colored + geometry outputs
# ============================================================================
colored_parts, all_geom = [], []
for key, (rgba, meshes) in GROUPS.items():
    m = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]
    m.visual.face_colors = rgba
    colored_parts.append(m)
    all_geom.append(m.copy())

colored = trimesh.util.concatenate(colored_parts)

# center X/Y, flat on Z=0
shift = [-colored.bounds.mean(axis=0)[0], -colored.bounds.mean(axis=0)[1], -colored.bounds[0][2]]
colored.apply_translation(shift)

# scale to the spec-sheet print height: 12.0 cm = 120 mm
TARGET_H = 120.0
s = TARGET_H / colored.extents[2]
colored.apply_scale(s)

P = "/Users/elitzurserver/Projects/אלויסון/"
glb = P + "elvison_color.glb"
colored.export(glb)
# colored OBJ (+mtl) for editors that read vertex/material color
colored.export(P + "elvison_color.obj")
# colored 3MF for color 3D printing
try:
    colored.export(P + "elvison_color.3mf")
    mf = "elvison_color.3mf"
except Exception as ex:
    mf = f"3mf skipped ({ex})"

# watertight single-color STL via boolean union, scaled to 120 mm
print("Union for watertight STL...")
solid = trimesh.boolean.union(all_geom)
if solid is None or solid.is_empty:
    solid = trimesh.util.concatenate(all_geom)
solid.apply_translation(shift)
solid.apply_scale(TARGET_H / solid.extents[2])
stl = P + "elvison.stl"
solid.export(stl)
solid.export(P + "elvison.obj")

print(f"Exported: elvison_color.glb / .obj / {mf} ; elvison.stl / .obj")
e = colored.extents
print(f"BBox(mm) W={e[0]:.1f} D={e[1]:.1f} H={e[2]:.1f} | colors={len(GROUPS)} | "
      f"glb_faces={len(colored.faces)} | stl_watertight={solid.is_watertight}")
