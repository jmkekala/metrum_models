# SPDX-License-Identifier: GPL-3.0-or-later

"""Generate temporary atlas mips for explicit filtering stress renders.

    python scripts/review_atlas_mips.py ASSET_DIR OUTPUT_DIR --levels 3 4

Use review_asset.py --texture-dir OUTPUT_DIR/mip3 to render a chosen mip.
This is a controlled whole-atlas minification test, not a consumer sampler
implementation. Albedo is averaged in linear light; ORM channels are linear.
Original PNGs remain untouched. Shipping mipmaps belong to the consumer.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main(args):
    export = (args.asset / 'export').resolve()
    if args.output.resolve().is_relative_to(export):
        raise ValueError('Diagnostic mips must stay outside export/.')
    for path in export.glob('*.png'):
        arr = np.asarray(Image.open(path).convert('RGB'), dtype=np.float64) / 255
        colour = '_albedo_' in path.name or '_emission' in path.name
        if colour:
            arr = np.where(arr <= 0.04045, arr / 12.92, ((arr + 0.055) / 1.055) ** 2.4)
        for level in args.levels:
            block = 2 ** level
            h, w, _ = arr.shape
            if h % block or w % block:
                raise ValueError(f'{path}: level {level} does not divide image dimensions')
            mip = arr.reshape(h // block, block, w // block, block, 3).mean(axis=(1, 3))
            if '_normal' in path.name:
                normal = mip * 2 - 1
                normal /= np.maximum(np.linalg.norm(normal, axis=2, keepdims=True), 1e-12)
                mip = normal * 0.5 + 0.5
            if colour:
                mip = np.where(mip <= 0.0031308, 12.92 * mip, 1.055 * mip ** (1 / 2.4) - 0.055)
            directory = args.output / f'mip{level}'
            directory.mkdir(parents=True, exist_ok=True)
            Image.fromarray(np.rint(np.clip(mip, 0, 1) * 255).astype(np.uint8)).save(directory / path.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('asset', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--levels', type=int, nargs='+', default=[3, 4])
    main(p.parse_args())
