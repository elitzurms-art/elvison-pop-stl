#!/usr/bin/env python3
"""
Build a textured "photo box" from the REAL cropped photos of the ELVISON Pop:
the front figure on the front face, the BACK (E-logo) view on the back, and the
LEFT / RIGHT views on the sides. Rotating it in the web viewer shows the actual
photos from every angle. Exports elvison_photo.glb (+ a thin base).
"""
import numpy as np
import trimesh
from PIL import Image

P = "/Users/elitzurserver/Projects/אלויסון/"
front = Image.open("/tmp/v3_front.png").convert("RGB")
back  = Image.open("/tmp/v3_back.png").convert("RGB")
left  = Image.open("/tmp/v3_left.png").convert("RGB")
right = Image.open("/tmp/v3_right.png").convert("RGB")

# real print dimensions from the spec sheet: 7.5 x 6.5 x 12.0 cm
HT = 120.0                                   # height (mm)
W  = 75.0                                     # width  (mm)
D  = 65.0                                     # depth  (mm)

def face(center, normal, right_dir, hw, hh, image):
    n = np.array(normal, float)
    up = np.array([0, 0, 1.0])
    r = np.array(right_dir, float)
    C = np.array(center, float)
    tl = C + up*hh - r*hw
    tr = C + up*hh + r*hw
    br = C - up*hh + r*hw
    bl = C - up*hh - r*hw
    V = np.array([tl, tr, br, bl])
    F = np.array([[3, 2, 1], [3, 1, 0]])      # CCW seen from outside (+n)
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    m = trimesh.Trimesh(vertices=V, faces=F, process=False)
    mat = trimesh.visual.material.PBRMaterial(
        baseColorTexture=image, metallicFactor=0.0, roughnessFactor=1.0)
    m.visual = trimesh.visual.TextureVisuals(uv=uv, material=mat, image=image)
    return m

cz = HT/2
faces = [
    face([0,  D/2, cz], [0, 1, 0],  [-1, 0, 0], W/2, HT/2, front),   # FRONT +Y
    face([0, -D/2, cz], [0,-1, 0],  [ 1, 0, 0], W/2, HT/2, back),    # BACK  -Y
    face([ W/2, 0, cz], [1, 0, 0],  [ 0, 1, 0], D/2, HT/2, right),   # RIGHT +X
    face([-W/2, 0, cz], [-1,0, 0],  [ 0,-1, 0], D/2, HT/2, left),    # LEFT  -X
]

# dark top & bottom caps
cap_dark = [20, 20, 22, 255]
for z, nz in [(HT, 1), (0, -1)]:
    v = np.array([[-W/2,-D/2,z],[W/2,-D/2,z],[W/2,D/2,z],[-W/2,D/2,z]])
    f = np.array([[0,1,2],[0,2,3]]) if nz > 0 else np.array([[0,2,1],[0,3,2]])
    cap = trimesh.Trimesh(vertices=v, faces=f, process=False)
    cap.visual.face_colors = cap_dark
    faces.append(cap)

# base slab
base = trimesh.creation.box(extents=[W+14, D+14, 10])
base.apply_translation([0, 0, -5])
base.visual.face_colors = cap_dark
faces.append(base)

scene = trimesh.Scene(faces)
out = P + "elvison_photo.glb"
scene.export(out)
b = scene.bounds
print(f"Exported {out}")
print(f"size(mm) W={b[1][0]-b[0][0]:.0f} D={b[1][1]-b[0][1]:.0f} H={b[1][2]-b[0][2]:.0f}")
