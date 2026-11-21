# SPDX-License-Identifier: GPL-3.0-or-later

"""tiilimuuri_run_5m: a 5 m straight run of the brick perimeter wall, its pier
on its -X joint plane.

Everything but which piece this is belongs to scripts/boundary_wall.py: the
shared atlas, the joint rule, the geometry of every tier, the layout checks
and the facts. Rebuild from the repository root, textures first (system
Python with scipy and Pillow), then the tiers in Blender:

    python3 scripts/boundary_wall.py export props/boundary/tiilimuuri_run_5m
    blender --background --python props/boundary/tiilimuuri_run_5m/build.py

or, to rewrite only the facts sidecar against the files in export/:

    blender --background --python props/boundary/tiilimuuri_run_5m/build.py -- facts
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import boundary_wall  # noqa: E402

ASSET = "tiilimuuri_run_5m"
PIECE = boundary_wall.Run(5.0)
BUILD, build_all, facts = boundary_wall.piece_asset(ASSET, HERE, PIECE)

if __name__ == "__main__":
    BUILD.main(build_all, facts)
