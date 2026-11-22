# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for rintamamiestalo_gable_entry, and
the layout build.py maps into.

The atlas is the rintamamiestalo family's (scripts/rintamamiestalo.py): its
bands, regions, palettes, painting and weathering are the type's, shared with
the other three houses. This one differs from the family's default layout in
four ways:

- the gable band is taller, because the gables' belt board sits at the attic
  floor, Z_BELT = 3.85 m, the eave fascia's lower edge, so the fascia's line
  carries on across each gable as the belt (at the default Z_EAVE the
  balcony doors would cut through it); S2 reaches 4.60 m above it;
- the roof band is shorter to make room: 232 rows over the slope, 37 px/m
  along it against the walls' 64, which only the snow guard, the ridge
  flashing and the drip edge vary along;
- the balcony door is a pair of glazed leaves, and there is no bathroom
  window;
- the deck and railing strips are added over the unique row, for the
  terrace's and the balcony's deck boards and their railings' balusters.

LAYOUT is the single source of the numbers build.py shares with the atlas, so
the pixel layout and the UVs cannot drift apart.

    python3 facade_atlas.py export      # writes every map into ./export
    python3 facade_atlas.py             # checks the region layout
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import rintamamiestalo  # noqa: E402

LAYOUT = rintamamiestalo.Layout("rintamamiestalo_gable_entry", balcony_door="pair",
                                bath=False, strips=True, z_belt=3.85, s2_span=4.60,
                                roof=(590.0, 232.0))


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
