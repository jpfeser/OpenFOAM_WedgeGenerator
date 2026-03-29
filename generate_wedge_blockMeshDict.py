#!/usr/bin/env python3
"""
Generate an OpenFOAM blockMeshDict for a single-wedge (axisymmetric) pipe geometry.

The wedge uses a 5-degree total opening angle (2.5 degrees each side of the
xz-plane), which matches the standard OpenFOAM wedge convention and the
reference blockMeshDict this script was modeled after.

Vertex layout (looking down the +z axis, y is "up"):

        1 (front, +y side)          2,5 are the z=L copies of 1,4
       /
      / half_angle
  0 -------- axis (x)
      \\ half_angle
       \\
        4 (back, -y side)

Vertices:
  0: origin                  (0, 0, 0)
  1: outer wall, front, z=0  (R, +Ry, 0)
  2: outer wall, front, z=L  (R, +Ry, L)
  3: origin at z=L           (0, 0, L)
  4: outer wall, back, z=0   (R, -Ry, 0)
  5: outer wall, back, z=L   (R, -Ry, L)

Usage:
    python generate_wedge_blockMeshDict.py --diameter 0.1898 --length 1.1 --nr 19 --nz 300
    python generate_wedge_blockMeshDict.py -D 0.05 -L 0.5 -nr 20 -nz 100 -o blockMeshDict
"""

import argparse
import math
import os


WEDGE_ANGLE_DEG = 5.0  # total wedge opening angle (degrees)


def generate_blockMeshDict(diameter, length, nr, nz, convert_to_meters=1):
    """Return the blockMeshDict file contents as a string."""

    R = diameter / 2.0
    half_angle = math.radians(WEDGE_ANGLE_DEG / 2.0)

    # Vertex coordinates
    Rx = R * math.cos(half_angle)   # x-component at outer radius
    Ry = R * math.sin(half_angle)   # y-component at outer radius

    vertices = [
        (0.0,  0.0,   0.0),       # 0  – axis, z = 0
        (Rx,   Ry,    0.0),       # 1  – outer, front (+y), z = 0
        (Rx,   Ry,    length),    # 2  – outer, front (+y), z = L
        (0.0,  0.0,   length),    # 3  – axis, z = L
        (Rx,  -Ry,    0.0),       # 4  – outer, back  (-y), z = 0
        (Rx,  -Ry,    length),    # 5  – outer, back  (-y), z = L
    ]

    def fmt_vertex(v):
        """Format a vertex tuple to match the reference file style."""
        return f"({v[0]:.6g} {v[1]:.6g} {v[2]:.6g})"

    vertex_block = "\n".join(fmt_vertex(v) for v in vertices)

    contents = f"""\
FoamFile
{{
    version         2.0;
    format          ascii;
 
    root            "";
    case            "";
    instance        "";
    local           "";
 
    class           dictionary;
    object          blockMeshDict;
}}
 
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
 
convertToMeters {convert_to_meters};
 
vertices
(
{vertex_block}
);
 
blocks
(
hex (0 4 1 0 3 5 2 3) ({nr}  1 {nz}) simpleGrading (1 1 1)
);
 
edges
(
);
 
boundary
(
     front
     {{ 
           type wedge;
           faces  
           (
               (0 1 2 3)
           );
      }}
     back
     {{ 
           type wedge;
           faces  
           (
               (0 3 5 4)
           );
      }}
     tankWall
     {{ 
           type wall;
           faces  
           (
               (1 4 5 2)
           );
      }}
     inlet
     {{ 
           type patch;
           faces  
           (
               (0 4 1 0)
           );
      }}
     outlet
     {{ 
           type patch;
           faces  
           (
               (3 5 2 3)
           );
      }}
     axis
     {{ 
           type empty;
           faces  
           (
               (0 3 3 0)
           );
      }}
);
 
mergePatchPairs
(
);
"""
    return contents


def main():
    parser = argparse.ArgumentParser(
        description="Generate an OpenFOAM blockMeshDict for a wedge (axisymmetric) pipe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Reproduce the reference case (D=0.1898 m, L=1.1 m, 19x300 cells):
  python %(prog)s -D 0.1898 -L 1.1 -nr 19 -nz 300

  # A smaller pipe, output to a custom path:
  python %(prog)s -D 0.05 -L 0.5 -nr 25 -nz 150 -o constant/polyMesh/blockMeshDict
""",
    )
    parser.add_argument(
        "-D", "--diameter", type=float, required=True,
        help="Pipe inner diameter (in convertToMeters units).",
    )
    parser.add_argument(
        "-L", "--length", type=float, required=True,
        help="Pipe length along z-axis.",
    )
    parser.add_argument(
        "-nr", "--nr", type=int, required=True,
        help="Number of cells in the radial direction.",
    )
    parser.add_argument(
        "-nz", "--nz", type=int, required=True,
        help="Number of cells in the axial (z) direction.",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="blockMeshDict",
        help="Output file path (default: blockMeshDict in current directory).",
    )
    parser.add_argument(
        "--convert-to-meters", type=float, default=1,
        help="convertToMeters scaling factor (default: 1).",
    )

    args = parser.parse_args()

    contents = generate_blockMeshDict(
        diameter=args.diameter,
        length=args.length,
        nr=args.nr,
        nz=args.nz,
        convert_to_meters=args.convert_to_meters,
    )

    # Make sure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w") as f:
        f.write(contents)

    print(f"Written: {args.output}")
    print(f"  Diameter = {args.diameter}")
    print(f"  Radius   = {args.diameter / 2.0}")
    print(f"  Length   = {args.length}")
    print(f"  Cells    = {args.nr} (radial) x 1 (circumferential) x {args.nz} (axial)")
    print(f"  Wedge    = {WEDGE_ANGLE_DEG}° total ({WEDGE_ANGLE_DEG/2}° half-angle)")


if __name__ == "__main__":
    main()
