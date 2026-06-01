# ELVISON — Blocky Pop Figure (STL)

A procedurally-generated, blocky/voxel-style 3D-printable figure of the
**ELVISON** YouTuber Pop, inspired by reference renders. Built with Python +
[`trimesh`](https://trimesh.org/).

> ⚠️ This is a **stylized interpretation**, not a 1:1 copy of the commercial render.
> STL files carry geometry only — no color. Paint by hand or via multi-material printing.

## 📥 Downloads

### Single piece
- **`elvison.stl`** / **`כלוד 1.stl`** — the whole figure as one watertight solid
  (height ≈ 164 mm). Ready to slice & print.

### Split into parts (`parts/`) — easy to color/edit in Tinkercad
All parts share world coordinates, so importing them together lines them up automatically.

| File | Part |
|------|------|
| `parts/elvison_base.stl` | Base + Play button |
| `parts/elvison_legs.stl` | Legs + shoes |
| `parts/elvison_body.stl` | Torso + arms |
| `parts/elvison_camera.stl` | Camera + lens |
| `parts/elvison_head.stl` | Head + neck |
| `parts/elvison_hair.stl` | Hair |

## 🔧 Rebuild from source

```bash
pip install trimesh numpy manifold3d
python3 build_elvison.py        # single-piece STL
python3 build_elvison_parts.py  # split-parts STLs
```

Edit the proportion constants at the top of either script to tweak the figure.

## 🖨️ Tinkercad
1. Create a new design, rename it (e.g. **כלוד 1**).
2. **Import** the STL(s) — drag the files in.
3. Color each part, then optionally **Group** them.
