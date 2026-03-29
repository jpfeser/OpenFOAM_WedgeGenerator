# OpenFOAM Wedge blockMeshDict Generator

A Python script that generates OpenFOAM `blockMeshDict` files for axisymmetric (wedge-type) pipe simulations. The output uses a single hex block with a 5° wedge opening angle, matching the standard OpenFOAM convention for 2D axisymmetric cases.

## Requirements

- Python 3.6+
- No external dependencies (uses only `math`, `argparse`, and `os` from the standard library)

## Inputs

The script accepts the following command-line arguments:

| Argument | Flag | Required | Description |
|---|---|---|---|
| `--diameter` | `-D` | Yes | Pipe inner diameter, in the units set by `convertToMeters` |
| `--length` | `-L` | Yes | Pipe length along the z-axis |
| `--nr` | `-nr` | Yes | Number of cells in the radial direction |
| `--nz` | `-nz` | Yes | Number of cells in the axial (z) direction |
| `--output` | `-o` | No | Output file path (default: `blockMeshDict` in the current directory) |
| `--convert-to-meters` | — | No | `convertToMeters` scaling factor (default: `1`) |

## Output

The script writes a complete `blockMeshDict` file containing:

- **6 vertices** defining a single wedge-shaped hex block along the z-axis
- **1 hex block** with `simpleGrading (1 1 1)` (uniform cell distribution)
- **6 boundary patches:**
  - `front` — wedge face (+y side)
  - `back` — wedge face (−y side)
  - `tankWall` — outer pipe wall
  - `inlet` — upstream face at z = 0
  - `outlet` — downstream face at z = L
  - `axis` — centreline (type `empty`)

The circumferential cell count is always 1, as required for a single-wedge axisymmetric setup.

## Geometry

The wedge is oriented with the pipe axis along **z**, the radial direction along **x**, and the wedge opening in the **y** direction. The total wedge angle is **5°** (2.5° above and below the xz-plane), which is the standard for OpenFOAM wedge boundary conditions.

```
        vertex 1 (+y)
       /
      /  2.5°
  0 ———————————— x  (radial)
      \  2.5°
       \
        vertex 4 (-y)

  z (axial) points into the page
```

## Usage Examples

Generate a blockMeshDict for a pipe with D = 0.1898 m, L = 1.1 m, 19 radial cells, and 300 axial cells:

```bash
python generate_wedge_blockMeshDict.py -D 0.1898 -L 1.1 -nr 19 -nz 300
```

Write the output directly into an OpenFOAM case directory:

```bash
python generate_wedge_blockMeshDict.py -D 0.05 -L 0.5 -nr 25 -nz 150 \
    -o myCase/constant/polyMesh/blockMeshDict
```

Use millimetre inputs with `convertToMeters 0.001`:

```bash
python generate_wedge_blockMeshDict.py -D 50 -L 500 -nr 25 -nz 150 \
    --convert-to-meters 0.001
```

After generating, run `blockMesh` from your OpenFOAM case directory as usual:

```bash
blockMesh
```
