#!/usr/bin/env python3
"""Compile roster portraits into the existing GBA object-event frame layouts.

Shared field palettes are intentionally preserved. These are portrait animations,
not bespoke four-direction walking sprites. Run after convert_roster.py.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import argparse
import json
import re
from collections import deque

BASE = Path(__file__).resolve().parent


def normalized(name):
    return re.sub(r'[^a-z0-9]', '', name.lower().replace('species_', ''))


def read_roster(path):
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get('roster', data.get('species', data.get('entries', data)))
    if isinstance(data, dict):
        data = [dict(value, species=key) for key, value in data.items()]
    result = {}
    for row in data:
        key = row.get('species') or row.get('original') or row.get('pokemon') or row.get('constant')
        name = row.get('digimon') or row.get('digimon_name') or row.get('full_name') or row.get('name')
        assert key and name, row
        result[normalized(key)] = name
    return result


def source_frames(path):
    """Preserve GIF transparency; remove only connected corner background if absent."""
    image = Image.open(path)
    frames = []
    for index in range(getattr(image, 'n_frames', 1)):
        image.seek(index)
        frame = image.convert('RGBA')
        if frame.getextrema()[3][0] == 255:
            pixels = frame.load()
            bg = pixels[0, 0]
            queue = deque([(0, 0), (frame.width-1, 0), (0, frame.height-1), (frame.width-1, frame.height-1)])
            visited = set()
            while queue:
                x, y = queue.popleft()
                if (x, y) in visited or not (0 <= x < frame.width and 0 <= y < frame.height):
                    continue
                visited.add((x, y))
                if pixels[x, y] != bg:
                    continue
                pixels[x, y] = (0, 0, 0, 0)
                queue.extend(((x-1, y), (x+1, y), (x, y-1), (x, y+1)))
        frames.append(frame)
    boxes = [frame.getbbox() for frame in frames if frame.getbbox()]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    return [frame.crop(box) for frame in frames]


def indexed(image, palette):
    colors = [tuple(palette[i:i+3]) for i in range(0, 48, 3)]
    mapped = {}
    values = []
    for color in image.getdata():
        if color[3] < 128:
            values.append(0)
        else:
            if color[:3] not in mapped:
                mapped[color[:3]] = min(range(1, 16), key=lambda n: sum((a-b)**2 for a, b in zip(color[:3], colors[n])))
            values.append(mapped[color[:3]])
    output = Image.new('P', image.size)
    output.putpalette(palette[:48])
    output.putdata(values)
    return output


def palette_file(path):
    lines = path.read_text().splitlines()[3:19]
    return [int(channel) for line in lines for channel in line.split()]


def make_sheet(path, gif, palette=None, template=None, parcel=False, doll=False):
    old = Image.open(template or path)
    original_size = old.size
    palette = palette or old.getpalette()
    # Every supported sheet is one horizontal row of square frames.
    side = original_size[1]
    assert original_size[0] % side == 0
    count = original_size[0] // side
    frames = source_frames(gif)
    max_side = side-2 if side <= 16 else side-4
    scale = min(max_side/frames[0].width, max_side/frames[0].height)
    new_size = (max(1, round(frames[0].width*scale)), max(1, round(frames[0].height*scale)))
    sheet = Image.new('RGBA', original_size)
    for frame_index in range(count):
        frame = frames[frame_index % len(frames)].resize(new_size, Image.Resampling.NEAREST)
        if count >= 3 and frame_index % 3 == 2:
            frame = ImageOps.mirror(frame)
        x = frame_index*side + (side-frame.width)//2
        y = side-frame.height-1
        sheet.alpha_composite(frame, (x, y))
        if parcel:
            # Keep the moving-home scene legible with a small shipping box.
            draw = ImageDraw.Draw(sheet)
            left = frame_index*side+side//2-5
            draw.rectangle((left, side-11, left+10, side-2), fill=(213,164,106,255), outline=(49,49,57,255))
            draw.line((left+5, side-10, left+5, side-3), fill=(255,213,106,255))
    result = indexed(sheet, palette)
    result.save(path, bits=4)
    assert result.size == original_size
    assert max(result.getdata()) <= 15
    assert result.getpalette()[:48] == palette[:48]
    return {'file': str(path), 'gif': str(gif), 'dimensions': list(original_size), 'frames': count}


def add_block(path, label, content):
    text = path.read_text()
    start = '// BEGIN DIGIMON '+label
    end = '// END DIGIMON '+label
    text = re.sub(re.escape(start)+r'.*?'+re.escape(end)+r'\n?', '', text, flags=re.S)
    block = start+'\n'+content+'\n'+end+'\n'
    if '#endif' in text:
        position = text.rfind('#endif')
        text = text[:position]+block+'\n'+text[position:]
    else:
        text += '\n'+block
    path.write_text(text)


def split_shared(root):
    """Give formerly palette-swapped creatures separate portrait pixel data."""
    base = root/'src/data/object_events'
    pic_text = (base/'object_event_pic_tables.h').read_text()
    groups = [('LatiasLatios', ['Latias', 'Latios']), ('Regi', ['Regirock', 'Regice', 'Registeel'])]
    graphics = []
    tables = []
    info_path = base/'object_event_graphics_info.h'
    info = info_path.read_text()
    for old, names in groups:
        table = re.search(r'const struct SpriteFrameImage gObjectEventPicTable_'+old+r'\[\] = \{.*?\n\};', pic_text, re.S).group()
        for name in names:
            symbol = 'Digimon'+name
            graphics.append('const u32 gObjectEventPic_'+symbol+'[] = INCBIN_U32("graphics/object_events/pics/pokemon/digimon_'+name.lower()+'.4bpp");')
            tables.append(table.replace('gObjectEventPicTable_'+old, 'gObjectEventPicTable_'+symbol).replace('gObjectEventPic_'+old, 'gObjectEventPic_'+symbol))
            pattern = r'(const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+name+r' = \{)(.*?)(\n\};)'
            info = re.sub(pattern, lambda m: m[1]+re.sub(r'\.images = \w+', '.images = gObjectEventPicTable_'+symbol, m[2])+m[3], info, flags=re.S)
    add_block(base/'object_event_graphics.h', 'PORTRAIT DATA', '\n'.join(graphics))
    add_block(base/'object_event_pic_tables.h', 'PORTRAIT TABLES', '\n\n'.join(tables))
    info_path.write_text(info)
    rules_path = root/'spritesheet_rules.mk'
    rules = rules_path.read_text()
    rules = re.sub(r'# BEGIN DIGIMON PORTRAITS.*?# END DIGIMON PORTRAITS\n?', '', rules, flags=re.S)
    rules += '\n# BEGIN DIGIMON PORTRAITS\n'
    for _, names in groups:
        for name in names:
            rules += '$(OBJEVENTGFXDIR)/pokemon/digimon_'+name.lower()+'.4bpp: %.4bpp: %.png\n\t$(GBAGFX) $< $@ -mwidth 4 -mheight 4\n\n'
    rules += '# END DIGIMON PORTRAITS\n'
    rules_path.write_text(rules)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=BASE/'source')
    parser.add_argument('--roster', type=Path, default=BASE/'roster.json')
    parser.add_argument('--sprites', type=Path, default=BASE/'sprite-originals')
    args = parser.parse_args()
    root = args.root
    roster = read_roster(args.roster)
    gifs = {normalized(p.stem): p for p in args.sprites.rglob('*.gif')}
    report = []
    pics = root/'graphics/object_events/pics'

    def convert(path, species, **kwargs):
        name = roster[normalized(species)]
        result = make_sheet(path, gifs[normalized(name)], **kwargs)
        result.update(species=species, digimon=name)
        result['file'] = str(path.relative_to(root))
        result['gif'] = str(gifs[normalized(name)].relative_to(args.sprites))
        report.append(result)

    aliases = {'latias_latios': 'latias', 'regi': 'regirock', 'machoke_carrying_box': 'machoke', 'machoke_facing_away': 'machoke'}
    for path in sorted((pics/'pokemon').glob('*.png')):
        if path.stem.startswith('digimon_'):
            continue
        convert(path, aliases.get(path.stem, path.stem), parcel='carrying_box' in path.stem)
    for path in sorted((pics/'dolls').glob('*.png')):
        species = re.sub(r'^(big_|unused_)', '', path.stem).removesuffix('_doll')
        convert(path, species, doll=True)
    for filename, species in [('pika_cushion', 'pikachu'), ('zigzag_cushion', 'zigzagoon')]:
        convert(pics/'cushions'/(filename+'.png'), species, doll=True)
    # Use the palette selected by each object's runtime descriptor, not the
    # palette of the previously shared source sheet.
    for species, template, palette in [('latias','latias_latios',1), ('latios','latias_latios',0), ('regirock','regi',1), ('regice','regi',2), ('registeel','regi',3)]:
        convert(pics/'pokemon'/('digimon_'+species+'.png'), species,
                template=pics/'pokemon'/(template+'.png'),
                palette=palette_file(root/'graphics/object_events/palettes'/f'{palette:02}.pal'))
    split_shared(root)
    (BASE/'overworld-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'sheets':len(report), 'frames':sum(r['frames'] for r in report), 'report':str(BASE/'overworld-report.json')}))


if __name__ == '__main__':
    main()
