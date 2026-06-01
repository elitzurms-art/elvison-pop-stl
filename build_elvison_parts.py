#!/usr/bin/env python3
"""
Same blocky ELVISON figure, but exported SPLIT INTO SEPARATE PARTS so each can
be imported/colored/edited independently in Tinkercad.

Each part is unioned into its own watertight body and written to its own STL.
All parts share the same world coordinates, so importing them all into one
Tinkercad design lines them up perfectly.
"""
import os
import numpy as np
import trimesh

OUT_DIR = "/Users/elitzurserver/Projects/אלויסון/parts"
os.makedirs(OUT_DIR, exist_ok=True)


def box(size, center):
    b = trimesh.creation.box(extents=size)
    b.apply_translation(center)
    return b


# ---- geometry constants (shared with the single-piece version) -------------
leg_h, leg_w, leg_d = 34, 17, 18
torso_h, torso_w, torso_d = 44, 46, 26
arm_w, arm_d = 13, 14
neck_h = 6
head_w, head_d, head_h = 60, 54, 56

leg_z = 9 + leg_h / 2
torso_z = 9 + leg_h + torso_h / 2
torso_top = 9 + leg_h + torso_h
head_z = torso_top + neck_h + head_h / 2
head_top = torso_top + neck_h + head_h
cam_x = -(torso_w / 2 + arm_w / 2 - 2)
cam_z = torso_top + 22

# ---- part groups -----------------------------------------------------------
groups = {}

# BASE + play button
base = trimesh.creation.cylinder(radius=36, height=9, sections=64)
base.apply_translation([0, 0, 4.5])
groups["base"] = [base, box((20, 12, 14), (-18, -34, 9))]

# LEGS + shoes
groups["legs"] = [
    box((leg_w, leg_d, leg_h), (-11, 0, leg_z)),
    box((leg_w, leg_d, leg_h), (+11, 0, leg_z)),
    box((leg_w + 4, leg_d + 6, 10), (-11, -2, 14)),
    box((leg_w + 4, leg_d + 6, 10), (+11, -2, 14)),
]

# TORSO + arms
groups["body"] = [
    box((torso_w, torso_d, torso_h), (0, 0, torso_z)),
    box((arm_w, arm_d, 40), (torso_w / 2 + arm_w / 2 - 2, 0, torso_top - 20)),
    box((arm_w, arm_d, 22), (-(torso_w / 2 + arm_w / 2 - 2), 0, torso_top - 11)),
    box((arm_w, arm_d, 26), (-(torso_w / 2 + arm_w / 2 - 2), 4, torso_top + 7)),
]

# CAMERA
cam_lens = trimesh.creation.cylinder(radius=7, height=14, sections=32)
cam_lens.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
cam_lens.apply_translation([cam_x, 8 + 16, cam_z])
groups["camera"] = [
    box((20, 22, 18), (cam_x, 8, cam_z)),
    cam_lens,
    box((6, 6, 8), (cam_x + 4, 4, cam_z + 13)),
]

# HEAD + neck
groups["head"] = [
    box((20, 16, neck_h), (0, 0, torso_top + neck_h / 2)),
    box((head_w, head_d, head_h), (0, 0, head_z)),
]

# HAIR
hair = [
    box((head_w + 4, head_d + 4, 16), (0, 0, head_top + 7)),
    box((10, head_d + 2, 26), (-(head_w / 2 + 1), 0, head_top - 6)),
    box((10, head_d + 2, 26), (+(head_w / 2 + 1), 0, head_top - 6)),
]
for i, x in enumerate(np.linspace(-22, 22, 5)):
    h = 14 if i % 2 == 0 else 9
    hair.append(box((11, 8, h), (x, head_d / 2 - 4, head_top - h / 2 + 2)))
groups["hair"] = hair

# ---- export each group -----------------------------------------------------
summary = []
for name, parts in groups.items():
    try:
        mesh = trimesh.boolean.union(parts)
        if mesh is None or mesh.is_empty:
            raise RuntimeError("empty")
    except Exception:
        mesh = trimesh.util.concatenate(parts)
    path = os.path.join(OUT_DIR, f"elvison_{name}.stl")
    mesh.export(path)
    summary.append((name, mesh.extents[2], mesh.is_watertight, len(mesh.faces)))

print(f"Exported {len(summary)} parts to {OUT_DIR}/")
for name, h, wt, f in summary:
    print(f"  elvison_{name:7s}.stl  height={h:6.1f}mm  watertight={wt}  faces={f}")
