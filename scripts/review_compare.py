# SPDX-License-Identifier: GPL-3.0-or-later

"""Side-by-side before/after sheets from two review_asset.py runs.

    python scripts/review_compare.py BEFORE_DIR AFTER_DIR OUTPUT_DIR [--zoom 2]
        [--crop X0 Y0 X1 Y1]      # enlarged region as fractions of the frame
        [--labels A B]            # names for the two sides (default before/after)

Pairs renders by file name, so run review_asset.py with identical settings
into both directories (render BEFORE_DIR before changing the asset). Writes
one sheet per pair -- before and after at native size, then the same crop of
each (the centre by default) enlarged with nearest-neighbour so texels stay
visible -- plus index.html to browse them. Requires Pillow; no network, and no changes to
either input directory or to any catalog image.
"""

import argparse
import html
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


def main(args):
    args.output.mkdir(parents=True, exist_ok=True)
    pairs = sorted(p.name for p in args.before.glob("*.png")
                   if (args.after / p.name).is_file())
    if not pairs:
        raise SystemExit("no renders with matching names in both directories")
    cards = []
    for name in pairs:
        with Image.open(args.before / name) as b, Image.open(args.after / name) as a:
            before, after = b.convert("RGB"), a.convert("RGB")
        if before.size != after.size:
            raise SystemExit("%s: sizes differ %s vs %s" % (name, before.size, after.size))
        diff = ImageChops.difference(before, after).convert("L")
        mean = sum(i * n for i, n in enumerate(diff.histogram())) / (diff.width * diff.height)
        out = "compare_" + name
        sheet(before, after, "%s  (mean abs difference %.1f / 255)" % (name, mean),
              args.zoom, args.crop, args.labels).save(args.output / out, optimize=True)
        cards.append((name, out, mean))
        print(out, "%.2f" % mean)
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
    main(p.parse_args())
