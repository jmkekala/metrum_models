# SPDX-License-Identifier: GPL-3.0-or-later

"""Sign lettering: the catalog's one alphabet, a plain geometric sans drawn
as stroked centrelines, and the functions that set it on an atlas.Canvas.
Called by texture generators.

No font file is read: every letterform is drawn here, so a bake has no
external dependency and the artwork carries no third party's licence. The
canvas is supersampled, so the strokes come out anti-aliased without a
separate coverage pass.

Glyphs live on a unit em: y = 0 the baseline, y = 1 the cap line. Each is
(advance, polylines), and its ink runs from x = 0 to its advance (the I is a
lone stem at x = 0 and so has no advance), so spacing and centring measured
on the boxes hold on the ink. Only the letters some sign needs exist; a new
sign adds its missing letters to GLYPHS in the same style, and every sign
sets the same shapes: an asset keeps no letterforms of its own.

    text()        sets a word, baseline at y, left edge at x; returns its
                  centreline width in pixels
    text_width()  that width without drawing, for centring
    centred_text()  a word centred on a rect, horizontally on its pen path
                  and its cap height vertically
    arc()         points along an elliptical arc, for glyphs and for an
                  asset's own marks

*tracking* is the gap between one letter's ink and the next's, in em, at any
*weight* (the stroke in pixels). *join* is a set of letter pairs set with no
gap at all, so a logotype's touching strokes become one: it belongs to the
word that asks for it and is never applied by default. Imports numpy only.

    import lettering
    w = lettering.text_width("KIOSKI", cap, 0.30, weight)
    lettering.text(c, "KIOSKI", x, y, cap, weight, ID_INK, 0.30, shade=1.0,
                   ao=1.0, height=0.004)
"""

import numpy as np


def arc(cx, cy, rx, ry, a0, a1, n=16):
    """Points along an elliptical arc from a0 to a1 degrees, n segments."""
    a = np.radians(np.linspace(a0, a1, n + 1))
    return list(zip(cx + rx * np.cos(a), cy + ry * np.sin(a)))


GLYPHS = {
    " ": (0.34, []),
    # The crossbar sits where the diagonals actually are at y = 0.30, so the
    # three strokes meet instead of the bar overshooting into white space.
    "A": (0.70, [[(0.00, 0.00), (0.35, 1.00), (0.70, 0.00)],
                 [(0.105, 0.30), (0.595, 0.30)]]),
    # Arms from the stem; the middle one shorter.
    "E": (0.60, [[(0.60, 1.00), (0.00, 1.00), (0.00, 0.00), (0.60, 0.00)],
                 [(0.00, 0.50), (0.48, 0.50)]]),
    "I": (0.00, [[(0.00, 0.00), (0.00, 1.00)]]),
    # Arm and leg are one polyline through a vertex on the stem: at any weight
    # a sign uses, 0.02 em is inside the stem's own half-width, so the
    # junction closes without a separate joining stroke.
    "K": (0.64, [[(0.00, 1.00), (0.00, 0.00)],
                 [(0.62, 1.00), (0.02, 0.44), (0.64, 0.00)]]),
    "M": (0.86, [[(0.00, 0.00), (0.00, 1.00), (0.43, 0.30), (0.86, 1.00),
                  (0.86, 0.00)]]),
    "O": (0.78, [arc(0.39, 0.50, 0.39, 0.50, 0, 360, 36)]),
    # Stem, upper bowl and waist in one polyline: the bowl closes on the stem
    # just above half height.
    "P": (0.62, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)]]),
    "R": (0.64, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)],
                 [(0.28, 0.51), (0.64, 0.00)]]),
    "S": (0.60, [arc(0.30, 0.75, 0.28, 0.25, 25, 270, 14)
                 + arc(0.30, 0.25, 0.30, 0.25, 90, -150, 14)]),
    "T": (0.68, [[(0.00, 1.00), (0.68, 1.00)], [(0.34, 1.00), (0.34, 0.00)]]),
    "U": (0.66, [[(0.00, 1.00), (0.00, 0.24)]
                 + arc(0.33, 0.24, 0.33, 0.24, 180, 360, 12)
                 + [(0.66, 1.00)]]),
    "1": (0.40, [[(0.06, 0.78), (0.36, 1.00), (0.36, 0.00)]]),
    "4": (0.66, [[(0.50, 0.00), (0.50, 1.00), (0.00, 0.30), (0.66, 0.30)]]),
}


def _step(prev, ch, tracking, ratio, join):
    """How far the pen moves before setting *ch*, in em.

    The glyphs are stroked, so each one's ink overruns its box by half a
    stroke at both ends, and spacing measured on centrelines would tighten as
    the weight goes up -- horizontals on the cap line (an E's arm, a T's bar,
    an R's shoulder) fuse into one bar. Adding the stroke-to-cap *ratio* back
    in makes *tracking* the gap between inks at any weight. A pair in *join*
    is set with no gap: one letter's last stroke is the next one's first.
    """
    if prev is None:
        return 0.0
    if (prev, ch) in join:
        return GLYPHS[prev][0]
    return GLYPHS[prev][0] + tracking + ratio


def text(c, word, x, y, cap, weight, mid, tracking, shade=None, ao=None,
         clip=None, height=None, join=()):
    """Set *word* with its baseline at y and its left edge at x, *cap* pixels
    per em, each stroke *weight* pixels wide; the channels as
    atlas.Canvas.stroke() sets them (None leaves a channel alone). Returns
    the word's centreline width in pixels."""
    cx, prev, ratio = float(x), None, weight / float(cap)
    for ch in word:
        cx += _step(prev, ch, tracking, ratio, join) * cap
        for poly in GLYPHS[ch][1]:
            for (ax, ay), (bx, by) in zip(poly, poly[1:]):
                c.stroke((cx + ax * cap, y + ay * cap), (cx + bx * cap, y + by * cap),
                         weight, mid=mid, shade=shade, ao=ao, clip=clip, height=height)
        prev = ch
    return cx + GLYPHS[prev][0] * cap - x if prev else 0.0


def text_width(word, cap, tracking, weight, join=()):
    """Centreline width of *word* in pixels; its ink is *weight* wider."""
    if not word:
        return 0.0
    ratio = weight / float(cap)
    w = sum(_step(word[i - 1], word[i], tracking, ratio, join)
            for i in range(1, len(word)))
    return (w + GLYPHS[word[-1]][0]) * cap


def centred_text(c, word, rect, cap, weight, mid, tracking, **kw):
    """Set *word* centred on rect (x, y, w, h): its pen path across the
    width, its cap height up the height. Keywords go to text()."""
    x, y, w, h = rect
    wide = text_width(word, cap, tracking, weight, kw.get("join", ()))
    return text(c, word, x + (w - wide) / 2.0, y + (h - cap) / 2.0, cap, weight, mid,
                tracking, **kw)
