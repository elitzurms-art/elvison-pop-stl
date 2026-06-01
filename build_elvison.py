#!/usr/bin/env python3
"""
Procedural blocky (Minecraft/voxel-style) figure of the "ELVISON" YouTuber Pop,
inspired by the reference renders. This is a stylized interpretation, not a 1:1
copy of the commercial render. Outputs a printable STL.

Coordinate system: Z = up, X = right, Y = depth (forward = +Y).
Units = millimeters.
"""
import numpy as np
import trimesh

parts = []


def box(size, center):
    """Axis-aligned box with given (sx, sy, sz) centered at (cx, cy, cz)."""
    b = trimesh.creation.box(extents=size)
    b.apply_translation(center)
    return b


def add(size, center):
    parts.append(box(size, center))


# ----------------------------------------------------------------------------
# BASE — round disc with a small "play button" tab in front
# ----------------------------------------------------------------------------
base = trimesh.creation.cylinder(radius=36, height=9, sections=64)
base.apply_translation([0, 0, 4.5])
parts.append(base)

# YouTube play-button tab in front of the base (rounded block)
add((20, 12, 14), (-18, -34, 9))            # red play button body
# triangle "play" notch is left as a flat face; printable as a block

# ----------------------------------------------------------------------------
# LEGS — two blocky legs standing on the base
# ----------------------------------------------------------------------------
leg_h = 34
leg_w = 17
leg_d = 18
leg_z = 9 + leg_h / 2
add((leg_w, leg_d, leg_h), (-11, 0, leg_z))   # left leg
add((leg_w, leg_d, leg_h), (+11, 0, leg_z))   # right leg

# shoes (slightly wider, white soles in the render -> just a lip here)
shoe_z = 9 + 5
add((leg_w + 4, leg_d + 6, 10), (-11, -2, shoe_z))
add((leg_w + 4, leg_d + 6, 10), (+11, -2, shoe_z))

# ----------------------------------------------------------------------------
# TORSO — main body block
# ----------------------------------------------------------------------------
torso_h = 44
torso_w = 46
torso_d = 26
torso_z = 9 + leg_h + torso_h / 2
add((torso_w, torso_d, torso_h), (0, 0, torso_z))

torso_top = 9 + leg_h + torso_h

# ----------------------------------------------------------------------------
# ARMS — left arm down, right arm raised holding camera
# ----------------------------------------------------------------------------
arm_w = 13
arm_d = 14

# Left arm (figure's left = +X here), hanging straight down
left_arm_h = 40
add((arm_w, arm_d, left_arm_h),
    (torso_w / 2 + arm_w / 2 - 2, 0, torso_top - left_arm_h / 2))

# Right arm (figure's right = -X), raised: upper segment + forearm up to camera
upper_h = 22
add((arm_w, arm_d, upper_h),
    (-(torso_w / 2 + arm_w / 2 - 2), 0, torso_top - upper_h / 2))
# forearm rising toward the camera near the head
fore_h = 26
add((arm_w, arm_d, fore_h),
    (-(torso_w / 2 + arm_w / 2 - 2), 4, torso_top + fore_h / 2 - 6))

# ----------------------------------------------------------------------------
# CAMERA — held up near the right side, by the head
# ----------------------------------------------------------------------------
cam_x = -(torso_w / 2 + arm_w / 2 - 2)
cam_z = torso_top + 22
add((20, 22, 18), (cam_x, 8, cam_z))                 # camera body
# lens barrel pointing forward (+Y)
lens = trimesh.creation.cylinder(radius=7, height=14, sections=32)
lens.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
lens.apply_translation([cam_x, 8 + 11 + 5, cam_z])
parts.append(lens)
add((6, 6, 8), (cam_x + 4, 4, cam_z + 13))           # top mic / accessory

# ----------------------------------------------------------------------------
# NECK + HEAD — oversized square Funko head
# ----------------------------------------------------------------------------
neck_h = 6
add((20, 16, neck_h), (0, 0, torso_top + neck_h / 2))

head_w = 60
head_d = 54
head_h = 56
head_z = torso_top + neck_h + head_h / 2
add((head_w, head_d, head_h), (0, 0, head_z))

head_top = torso_top + neck_h + head_h

# ----------------------------------------------------------------------------
# HAIR — blocky slabs sitting on top and sides of the head (jagged fringe)
# ----------------------------------------------------------------------------
hair_z = head_top + 7
add((head_w + 4, head_d + 4, 16), (0, 0, hair_z))            # main hair cap
# side burns / sides
add((10, head_d + 2, 26), (-(head_w / 2 + 1), 0, head_top - 6))
add((10, head_d + 2, 26), (+(head_w / 2 + 1), 0, head_top - 6))
# jagged fringe blocks over the forehead (front face, +Y)
fringe_y = head_d / 2 - 4
for i, x in enumerate(np.linspace(-22, 22, 5)):
    h = 14 if i % 2 == 0 else 9
    add((11, 8, h), (x, fringe_y, head_top - h / 2 + 2))

# ----------------------------------------------------------------------------
# Assemble + export
# ----------------------------------------------------------------------------
print(f"Combining {len(parts)} parts...")

mesh = None
try:
    # Try a proper boolean union for a clean watertight solid.
    mesh = trimesh.boolean.union(parts)
    if mesh is None or mesh.is_empty:
        raise RuntimeError("empty union")
    print("Boolean union succeeded.")
except Exception as e:
    print(f"Boolean union unavailable ({e}); concatenating instead "
          "(overlaps are handled by the slicer).")
    mesh = trimesh.util.concatenate(parts)

# Center on origin in X/Y, sit flat on Z=0
mesh.apply_translation([-mesh.bounds.mean(axis=0)[0],
                        -mesh.bounds.mean(axis=0)[1],
                        -mesh.bounds[0][2]])

out = "/Users/elitzurserver/Projects/אלויסון/elvison.stl"
mesh.export(out)

ext = mesh.extents
print(f"Exported: {out}")
print(f"Bounding box (mm): X={ext[0]:.1f}  Y={ext[1]:.1f}  Z(height)={ext[2]:.1f}")
print(f"Watertight: {mesh.is_watertight}  | Triangles: {len(mesh.faces)}")
