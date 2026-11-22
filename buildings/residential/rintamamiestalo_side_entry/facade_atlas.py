# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for rintamamiestalo_side_entry, and
the layout build.py maps into.

The atlas is the rintamamiestalo family's (scripts/rintamamiestalo.py): its
bands, regions, palettes, painting and weathering are the type's, shared with
the other three houses. This house carries the family's default layout, as
the porch house does; only its massing differs. LAYOUT is the single source
of the numbers build.py shares with the atlas, so the pixel layout and the
UVs cannot drift apart.

    python3 facade_atlas.py export      # writes every map into ./export
    python3 facade_atlas.py             # checks the region layout
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import rintamamiestalo  # noqa: E402

LAYOUT = rintamamiestalo.Layout("rintamamiestalo_side_entry")


def export(out_dir, ss=rintamamiestalo.atlas.SS):
    return rintamamiestalo.export(LAYOUT, out_dir, ss)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        LAYOUT.check_regions()
        print(__doc__)
