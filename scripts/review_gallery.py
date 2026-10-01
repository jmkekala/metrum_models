# SPDX-License-Identifier: GPL-2.0-only

"""Build local day/night contact sheets and an interactive review gallery.

    python scripts/review_gallery.py review/review_YYYY_MM_DD

Reads cycle/*_settings.json from review_asset.py. Requires Pillow. Keeps the
original render files and labels camera-fitted sheets separately from native
pixel LOD comparisons. No network dependencies or changes to catalog previews.
"""

import argparse
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main(root):
    lights = ['morning', 'noon', 'dusk', 'night']
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 22)
    except OSError:
        font = ImageFont.load_default(size=22)
    cards = []
    for path in sorted((root / 'cycle').glob('*_settings.json')):
        data = json.loads(path.read_text())
        asset = Path(data['asset']).name
        files = {r['light']: 'cycle/' + r['file'] for r in data['renders']}
        if not all(light in files for light in lights):
            raise ValueError(f'{asset}: incomplete day/night cycle')
        sheet = Image.new('RGB', (1440, 1140), (24, 27, 32))
        draw = ImageDraw.Draw(sheet)
        draw.text((20, 12), asset.replace('_', ' ') + ' — day/night lighting', font=font, fill='white')
        for i, light in enumerate(lights):
            with Image.open(root / files[light]) as source:
                im = source.copy()
            im.thumbnail((720, 510), Image.Resampling.LANCZOS)
            x, y = (i % 2) * 720, 55 + (i // 2) * 542
            sheet.paste(im, (x + (720 - im.width) // 2, y + 28))
            draw.text((x + 20, y), light.title(), font=font, fill='white')
        sheet_name = f'{asset}_day_night.png'
        sheet.save(root / sheet_name)
        attributes = ' '.join(f'data-{k}="{html.escape(v)}"' for k, v in files.items())
        cards.append(f'<article><h2>{html.escape(asset.replace("_", " "))}</h2>'
                     f'<a class="full" href="{files["noon"]}"><img {attributes} '
                     f'src="{files["noon"]}" alt="{asset}, noon lighting"></a>'
                     f'<p><a href="{sheet_name}">Four-view sheet</a> · '
                     f'<a href="cycle/{path.name}">Render settings</a></p></article>')
    extra = []
    for name, title in [('house_corner_before_after.png', 'House corners: before and after'),
                        ('house_lod_comparison.png', 'House corner paint across LODs'),
                        ('house_lod3_comparison.png', 'House LOD3 at 125 m'),
                        ('clock_window_comparison.png', 'Clocktower windows at 65 m'),
                        ('clock_later_comparison.png', 'Clocktower windows at 145 m'),
                        ('atlas_filtering_comparison.png', 'House atlas mip filtering checks'),
                        ('clock_filtering.png', 'Clocktower atlas mip filtering checks')]:
        if (root / name).is_file():
            extra.append(f'<li><a href="{name}">{title}</a></li>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Metrum — day/night asset review</title>
<style>
:root{color-scheme:dark;font:16px/1.5 system-ui;background:#14191f;color:#e9eef4}
body{margin:0 auto;max-width:1500px;padding:24px}h1{font-size:2rem;margin-bottom:8px}
p{color:#bcc8d4}a{color:#9dcbff}nav{display:flex;flex-wrap:wrap;gap:10px;position:sticky;
top:0;padding:16px 0;background:#14191fee;z-index:1}button{font:inherit;cursor:pointer;
border:1px solid #607087;border-radius:7px;background:#222d3a;color:white;padding:8px 18px}
button[aria-pressed=true]{background:#bed9f8;color:#142232}main{display:grid;
grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:24px}
article{background:#1d252f;border:1px solid #384453;border-radius:10px;overflow:hidden}
h2{font-size:1.1rem;margin:16px 18px}article p{margin:12px 18px}img{width:100%;display:block}
</style><h1>Day &amp; night</h1>
<p>Five existing assets, morning through night. Every asset keeps one camera, material set,
and exposure across its four views. Blender lighting scenarios; game rendering remains to be checked.
Night uses moonlight and ambient light, with no illuminated-window mask.</p>
<nav aria-label="Time of day">''' + ''.join(
        f'<button type="button" data-time="{t}" aria-pressed="{str(t == "noon").lower()}">{t.title()}</button>'
        for t in lights) + '''<button type="button" id="play" aria-pressed="false">Play cycle</button>
</nav><main>''' + ''.join(cards) + '</main><h2>Distance and filtering comparisons</h2><ul>' + ''.join(extra) + '''</ul>
<script>
const times=['morning','noon','dusk','night'];let current='noon',timer=null;
function show(t){current=t;document.querySelectorAll('[data-time]').forEach(b=>
b.setAttribute('aria-pressed',String(b.dataset.time===t)));
document.querySelectorAll('article img').forEach(im=>{im.src=im.dataset[t];
im.closest('a').href=im.src;im.alt=im.closest('article').querySelector('h2').textContent+', '+t+' lighting';});}
document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>show(b.dataset.time));
document.getElementById('play').onclick=function(){if(timer){clearInterval(timer);timer=null;}
else{timer=setInterval(()=>show(times[(times.indexOf(current)+1)%4]),2500);}
this.textContent=timer?'Pause cycle':'Play cycle';this.setAttribute('aria-pressed',String(!!timer));};
</script></html>'''
    (root / 'index.html').write_text(page)
    print(root / 'index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    main(parser.parse_args().directory)
