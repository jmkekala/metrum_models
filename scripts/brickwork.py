# SPDX-License-Identifier: GPL-3.0-or-later

"""The catalog's facing brick: one module and its stretcher bond, painted on
an atlas.Canvas. Called by texture generators.

The module is a 0.25 m stretcher on a 0.078125 m course: 16 x 5 px at 64
texels/m, so 64 bricks span a 1024 atlas and a band of whole courses ends on
a whole pixel. Alternate courses shift half a brick. Bed and perpend joints
are JOINT px wide and recessed, the brick faces BRICK_FACE proud of them.

    bond()    the bond's geometry over a field's sample grids: each sample's
              course, its brick's index (periodic in U) and the bed and
              perpend joint masks. For a painter that tones its bricks its
              own way.
    paint()   two-tone brick over a rect: a hashed tone per brick, about one
              brick in six the darker id, the mortar its own id. Courses
              count from the rect's foot; tone repeats every *tone_courses*
              courses and at the atlas wrap in U, so a band painted with it
              tiles and its rows can be sampled again higher up.

An asset keeps its layout (rows, ids, seed, tone period) and its palette;
this module keeps the module and how it is laid. It imports numpy and atlas
(itself numpy only), so a build.py can import a generator that imports it.

    import brickwork
    brickwork.paint(c, 0, ATLAS, y0, top, (ID_BRICK, ID_BRICK2, ID_MORTAR),
                    tone_courses=48, seed=17)

A painter on another module (a chimney's radial header bond, another course
pitch, integer-rounded bricks) stays with its asset.
"""

import numpy as np

import atlas

COURSE = 0.078125       # course pitch, metres: 5 px at 64 px/m
BRICK_L = 0.25          # stretcher length, metres: 16 px at 64 px/m
BRICK_FACE = 0.006      # brick face proud of the recessed mortar, metres
JOINT = 1.0             # joint width, px


def bond(Y, X, y0, course, blen, period, joint=JOINT):
    """Stretcher bond over sample grids Y, X (atlas.Canvas.field()).

    Courses *course* px tall count from row *y0*, bricks *blen* px long from
    column 0, odd courses shifted half a brick. Returns (r, b, bed, perp):
    the course index, the brick index modulo *period*, and the masks of the
    bed and perpend joints, each *joint* px wide.
    """
    r = np.floor((Y - y0) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - off) / blen).astype(np.int64) % period
    bed = (Y - y0 - r * course) < joint
    perp = ((X - off) % blen) < joint
    return r, b, bed, perp


def paint(c, x0, x1, y0, y1, ids, tone_courses, seed=17):
    """Two-tone stretcher-bond brick over [x0, x1) x [y0, y1), courses from
    row y0, in the catalog module at the canvas's ppm.

    *ids* is (brick, darker brick, mortar). Each brick's tone is hashed from
    its index modulo the atlas width in bricks and its course modulo
    *tone_courses*, with *seed*; the darker id with *seed* + 12. Mortar is
    flat, a little occluded, and BRICK_FACE below the brick faces.
    """
    brick, brick2, mortar = ids
    c.paint(x0, x1, y0, y1, brick, 1.0, 1.0)
    course, blen = COURSE * c.ppm, BRICK_L * c.ppm
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    r, b, bed, perp = bond(Y, X, y0, course, blen, int(c.size / blen))
    rr = r % tone_courses
    joint = bed | perp
    tone = 0.90 + 0.20 * atlas.hash_unit(b, rr, seed)
    dark = atlas.hash_unit(b, rr, seed + 12) < 0.17
    c.mid[sy, sx] = np.where(joint, mortar, np.where(dark, brick2, brick))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)
