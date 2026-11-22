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
    paint()   toned brick over a rect: a hashed tone per brick, about one
              brick in six the darker id, the mortar its own id. Courses
              count from the rect's foot; tone repeats every *tone_courses*
              courses and at the atlas wrap in U, so a band painted with it
              tiles and its rows can be sampled again higher up.

paint()'s keyword options, each off or at the value every caller had before
it existed unless asked for:

    y_ref=        the row the courses count from, instead of the rect's foot.
                  A region anchored at its top (a chimney under its cap)
                  passes the cap's row, so the course under the cap is whole
                  and the cut course falls at the rect's foot.
    ids           (brick, darker, mortar); darker or mortar may be None. With
                  no darker id every brick takes the brick id; with no mortar
                  id the joints keep the brick id, told apart by joint_shade,
                  AO and their recess alone.
    tone=         (low, span): a brick's shade is low + span * its hash,
                  default (0.90, 0.20).
    joint_shade=  the joints' shade, default 0.94 (on a mortar id of its own;
                  a joint on the brick id wants it darker, e.g. 0.80).
    arris=        how far, in metres, a brick's face rounds down at its edges
                  over ARRIS_W px, a quarter round: a worn arris for brick
                  seen close, such as a house chimney. 0 (the default) keeps
                  the square edge; at most BRICK_FACE.

An asset keeps its layout (rows, ids, seed, tone period) and its palette;
this module keeps the module and how it is laid. It imports numpy and atlas
(itself numpy only), so a build.py can import a generator that imports it.

    import brickwork
    brickwork.paint(c, 0, ATLAS, y0, top, (ID_BRICK, ID_BRICK2, ID_MORTAR),
                    tone_courses=48, seed=17)
    brickwork.paint(c, x0, x1, y0, cap, (ID_BRICK, None, ID_MORTAR),
                    tone_courses=24, seed=5, y_ref=cap, arris=0.003)

A painter on another module (a chimney's radial header bond, another course
pitch, integer-rounded bricks) stays with its asset.
"""

import numpy as np

import atlas

COURSE = 0.078125       # course pitch, metres: 5 px at 64 px/m
BRICK_L = 0.25          # stretcher length, metres: 16 px at 64 px/m
BRICK_FACE = 0.006      # brick face proud of the recessed mortar, metres
JOINT = 1.0             # joint width, px
ARRIS_W = 1.0           # width of a rounded arris (paint(arris=)), px


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


def paint(c, x0, x1, y0, y1, ids, tone_courses, seed=17, *, y_ref=None,
          tone=(0.90, 0.20), joint_shade=0.94, arris=0.0):
    """Toned stretcher-bond brick over [x0, x1) x [y0, y1), in the catalog
    module at the canvas's ppm, courses counted from row *y_ref* (default
    y0; it may lie anywhere, above the rect included).

    *ids* is (brick, darker brick, mortar), darker and mortar each optional
    (None). Each brick's tone is low + span * a hash of its index modulo
    the atlas width in bricks and its course modulo *tone_courses*, with
    *seed*, (low, span) = *tone*; the darker id goes to about one brick in
    six, hashed with *seed* + 12. Joints are flat, shaded *joint_shade*,
    occluded, and BRICK_FACE below the brick faces, whose edges round down
    by *arris* metres over ARRIS_W px when it is above 0.
    """
    brick, brick2, mortar = ids
    if not 0.0 <= arris <= BRICK_FACE:
        raise ValueError("arris %r m is outside 0 .. BRICK_FACE" % (arris,))
    ref = y0 if y_ref is None else y_ref
    c.paint(x0, x1, y0, y1, brick, 1.0, 1.0)
    course, blen = COURSE * c.ppm, BRICK_L * c.ppm
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    r, b, bed, perp = bond(Y, X, ref, course, blen, int(c.size / blen))
    rr = r % tone_courses
    joint = bed | perp
    low, span = tone
    shade = low + span * atlas.hash_unit(b, rr, seed)
    face = brick
    if brick2 is not None:
        dark = atlas.hash_unit(b, rr, seed + 12) < 0.17
        face = np.where(dark, brick2, brick)
    c.mid[sy, sx] = np.where(joint, brick if mortar is None else mortar, face)
    c.shade[sy, sx] = np.where(joint, joint_shade, shade)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    if arris > 0.0:
        # distance in px from each sample to its brick's nearest edge, the
        # joints' far sides: bed below, next course's bed above, perpends
        ly = Y - ref - r * course
        lx = (X - (r % 2) * blen * 0.5) % blen
        d = np.minimum(np.minimum(ly - JOINT, course - ly),
                       np.minimum(lx - JOINT, blen - lx))
        t = np.clip(d / ARRIS_W, 0.0, 1.0)
        top = BRICK_FACE - arris * (1.0 - np.sqrt(1.0 - (1.0 - t) ** 2))
        c.height[sy, sx] = np.where(joint, 0.0, top)
    else:
        c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)
