# SPDX-License-Identifier: GPL-3.0-or-later

"""Side-by-side before/after sheets from two review_asset.py runs.

    python scripts/review_compare.py BEFORE_DIR AFTER_DIR OUTPUT_DIR [--zoom 2]
        [--crop X0 Y0 X1 Y1]      # enlarged region as fractions of the frame
        [--labels A B]            # names for the two sides (default before/after)
        [--ignore-distance]       # pair names that differ only in the NN.Nm token
        [--pad [--pad-colour R G B]]  # centre differing sizes on one canvas

Pairs renders by file name, so run review_asset.py with identical settings
into both directories (render BEFORE_DIR before changing the asset). Writes
one sheet per pair -- before and after at native size, then the same crop of
each (the centre by default) enlarged with nearest-neighbour so texels stay
visible -- plus index.html to browse them. Requires Pillow; no network, and no changes to
either input directory or to any catalog image.

A change that moves an asset's bounds changes what review_asset.py fits to
them: the fitted distance in --day-cycle and --six-views file names
(asset_oblique_31.2m_noon_...), and the size of a cropped distance render.
By default such pairs do not match, and a pair whose sizes differ stops the
run. --ignore-distance pairs files by everything but the distance token
(view, light, emission state, tier, variant); where one key holds several
distances on both sides they pair in ascending order. --pad centres both
images of a pair on a common canvas of the larger width and height, filled
with --pad-colour (neutral grey by default), instead of stopping:

    python scripts/review_compare.py review/x/before review/x/after \
        review/x/compare --ignore-distance --pad
"""

import argparse
import html
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def sheet(before, after, title, zoom, crop=None, labels=("before", "after")):
    """Before | after on top; an enlarged crop of each below."""
    f, pad, head = font(20), 12, 34
    w, h = before.size
    if crop:
        box = (int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))
    else:
        cw, ch = w // (2 * zoom), h // (2 * zoom)
        box = ((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)
    cw, ch = box[2] - box[0], box[3] - box[1]
    zoom = max(1, min(zoom, w // max(1, cw)))      # keep each crop in its column
    crops = [im.crop(box).resize((cw * zoom, ch * zoom), Image.NEAREST)
             for im in (before, after)]
    out = Image.new("RGB", (2 * w + 3 * pad, head + h + head + ch * zoom + 2 * pad),
                    (24, 27, 32))
    d = ImageDraw.Draw(out)
    d.text((pad, 6), title, font=f, fill="white")
    for i, (label, im, enlarged) in enumerate(((labels[0], before, crops[0]),
                                               (labels[1], after, crops[1]))):
        x = pad + i * (w + pad)
        out.paste(im, (x, head))
        d.text((x + 8, head + 6), label, font=f, fill="yellow")
        y = head + h + head
        d.text((x, y - 26), "%s, %s %dx" % (label, "crop" if crop else "centre", zoom),
               font=f, fill="yellow")
        out.paste(enlarged, (x, y))
        d.rectangle([x + box[0], head + box[1], x + box[2], head + box[3]],
                    outline=(255, 210, 0))
    return out


# review_asset.py's distance token: _<metres with one decimal>m_
DISTANCE = re.compile(r"_(\d+(?:\.\d+)?)m_")


def pair_names(before_dir, after_dir, ignore_distance=False):
    """(before name, after name, output name) for every matching render.

    By exact name, or with *ignore_distance* by the name with its distance
    token masked, pairing several distances under one key in ascending
    order on both sides."""
    if not ignore_distance:
        return [(p.name, p.name, p.name) for p in sorted(before_dir.glob("*.png"))
                if (after_dir / p.name).is_file()]

    def groups(folder):
        out = {}
        for p in folder.glob("*.png"):
            m = DISTANCE.search(p.name)
            key = DISTANCE.sub("_*m_", p.name, count=1) if m else p.name
            out.setdefault(key, []).append((float(m.group(1)) if m else 0.0, p.name))
        return {k: [n for _, n in sorted(v)] for k, v in out.items()}

    gb, ga = groups(before_dir), groups(after_dir)
    pairs = []
    for key in sorted(set(gb) & set(ga)):
        if len(gb[key]) != len(ga[key]):
            print("skipped %s: %d distances before, %d after"
                  % (key, len(gb[key]), len(ga[key])))
            continue
        for b, a in zip(gb[key], ga[key]):
            mb, ma = DISTANCE.search(b), DISTANCE.search(a)
            out = b if b == a or not (mb and ma) else DISTANCE.sub(
                "_%sm-%sm_" % (mb.group(1), ma.group(1)), b, count=1)
            pairs.append((b, a, out))
    return pairs


def pad_pair(before, after, colour):
    """Both images centred on one canvas of their larger width and height."""
    w, h = max(before.width, after.width), max(before.height, after.height)
    out = []
    for im in (before, after):
        canvas = Image.new("RGB", (w, h), tuple(colour))
        canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
        out.append(canvas)
    return out


def main(args):
    args.output.mkdir(parents=True, exist_ok=True)
    pairs = pair_names(args.before, args.after, args.ignore_distance)
    if not pairs:
        raise SystemExit("no renders with matching names in both directories")
    cards = []
    for bname, aname, name in pairs:
        with Image.open(args.before / bname) as b, Image.open(args.after / aname) as a:
            before, after = b.convert("RGB"), a.convert("RGB")
        note = ""
        if before.size != after.size:
            if not args.pad:
                raise SystemExit("%s: sizes differ %s vs %s (--pad centres both on "
                                 "one canvas)" % (name, before.size, after.size))
            note = ", padded from %dx%d / %dx%d" % (before.size + after.size)
            before, after = pad_pair(before, after, args.pad_colour)
        diff = ImageChops.difference(before, after).convert("L")
        mean = sum(i * n for i, n in enumerate(diff.histogram())) / (diff.width * diff.height)
        out = "compare_" + name
        title = name if bname == aname else "%s  vs  %s" % (bname, aname)
        sheet(before, after, "%s  (mean abs difference %.1f / 255%s)" % (title, mean, note),
              args.zoom, args.crop, args.labels).save(args.output / out, optimize=True)
        cards.append((title + note, out, mean))
        print(out, "%.2f" % mean + note)
    rows = "\n".join(
        '<figure><figcaption>%s &mdash; mean abs difference %.1f</figcaption>'
        '<a href="%s"><img src="%s" loading="lazy"></a></figure>'
        % (html.escape(n), m, html.escape(o), html.escape(o)) for n, o, m in cards)
    (args.output / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Before / after</title>"
        "<style>body{background:#181b20;color:#ddd;font:14px sans-serif;margin:16px}"
        "img{max-width:100%%;height:auto}figure{margin:0 0 28px}</style>"
        "<h1>%s / %s</h1><p>%s vs %s</p>%s\n"
        % (html.escape(args.labels[0]), html.escape(args.labels[1]),
           html.escape(str(args.before)), html.escape(str(args.after)), rows))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("before", type=Path)
    p.add_argument("after", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--zoom", type=int, default=2)
    p.add_argument("--crop", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"),
                   help="region to enlarge, as fractions of the frame (top-left origin)")
    p.add_argument("--labels", nargs=2, default=("before", "after"),
                   metavar=("A", "B"), help="names for the two sides")
    p.add_argument("--ignore-distance", action="store_true",
                   help="pair renders whose names differ only in the fitted distance")
    p.add_argument("--pad", action="store_true",
                   help="centre a pair of different sizes on one canvas instead of stopping")
    p.add_argument("--pad-colour", type=int, nargs=3, default=(128, 128, 128),
                   metavar=("R", "G", "B"), help="padding colour, 0-255 (default neutral grey)")
    main(p.parse_args())
