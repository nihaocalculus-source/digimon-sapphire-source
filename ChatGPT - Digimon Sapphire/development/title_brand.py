#!/usr/bin/env python3
"""Compile Digimon title lettering and portraits into the existing GBA asset layout.
Requires Pillow. Run beside source/ and MetalGarurumon.png / WarGreymon.png.
"""
from pathlib import Path
import struct
from PIL import Image, ImageDraw, ImageFont
import shutil
import re

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'source'
GFX = SRC / 'graphics/title_screen'
FONT = ROOT / 'title-font.ttf'
if not FONT.exists():
    shutil.copyfile(ROOT.parent.parent / 'outputs/Sapphire-Wednesday-Deluxe/assets/VT323-Regular.ttf', FONT)

def palette(path, colors):
    path.write_text('JASC-PAL\n0100\n%d\n' % len(colors) + ''.join('%d %d %d\n' % tuple(c) for c in colors))

def palimg(size, colors):
    out = Image.new('P', size, 0)
    out.putpalette(sum((list(c) for c in colors), []) + [0] * (768 - len(colors)*3))
    return out

colors = [(0,0,0), (8,24,57), (8,88,160), (24,184,232), (184,248,255), (255,255,255), (255,200,64)] + [(0,0,0)]*217
for version, label in [('sapphire', 'SAPPHIRE'), ('ruby', 'RUBY')]:
    c = colors[:]
    if version == 'ruby':
        c[2], c[3], c[4] = (144,32,56), (240,88,56), (255,224,168)
    logo = palimg((256,64), c)
    d = ImageDraw.Draw(logo)
    f = ImageFont.truetype(str(FONT), 58)
    b = d.textbbox((0,0), 'DIGIMON', font=f)
    x = 120 - (b[2]-b[0])//2
    y = 11-b[1]
    d.text((x,y+2), 'DIGIMON', font=f, fill=2, stroke_width=4, stroke_fill=1)
    d.text((x,y), 'DIGIMON', font=f, fill=5, stroke_width=2, stroke_fill=3)
    d.line((34,57,205,57), fill=3, width=1)
    for xx in [28,211]: d.rectangle((xx,55,xx+3,58), fill=6)
    logo.save(GFX / ('pokemon_'+version+'.png'), bits=8)
    banner = palimg((128,32), c)
    bd = ImageDraw.Draw(banner)
    bf = ImageFont.truetype(str(FONT), 23)
    bb = bd.textbbox((0,0), label, font=bf)
    bd.text((64-(bb[2]-bb[0])//2, 8-bb[1]), label, font=bf, fill=4, stroke_width=1, stroke_fill=1)
    # The existing two 64x32 sprites consume consecutive tile rows.
    packed = palimg((64,64), c)
    packed.paste(banner.crop((0,0,64,32)), (0,0))
    packed.paste(banner.crop((64,0,128,32)), (0,32))
    packed.save(GFX / (version+'version.png'), bits=8)
    palette(GFX / ('logo_'+version+'.pal'), c)
    logo.convert('RGBA').save(ROOT / ('title-'+version+'-logo.png'))

# Keep the first tile blank; it fills the unused portion of the affine map.
(SRC / 'graphics/unknown/unknown_E9F7E4.bin').write_bytes(bytes(range(256)) + bytes(768))

def cutout(path):
    im = Image.open(path).convert('RGBA')
    # Some archived GIFs have an opaque white matte. Remove edge-connected matte only.
    if im.getextrema()[3][0] == 255:
        px = im.load(); bg = px[0,0][:3]
        todo = [(x,0) for x in range(im.width)] + [(x,im.height-1) for x in range(im.width)] + [(0,y) for y in range(im.height)] + [(im.width-1,y) for y in range(im.height)]
        seen = set()
        while todo:
            x,y = todo.pop()
            if (x,y) in seen or not (0<=x<im.width and 0<=y<im.height): continue
            seen.add((x,y))
            if px[x,y][:3] != bg: continue
            px[x,y] = (*bg,0)
            todo.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
    return im.crop(im.getbbox())

for legacy, art, backdrop, tint in [('kyogre','MetalGarurumon','water',(8,48,72)), ('groudon','WarGreymon','lava',(64,24,32))]:
    portrait = cutout(ROOT / (art+'.png'))
    portrait.thumbnail((100,64), Image.Resampling.NEAREST)
    canvas = Image.new('RGBA',(128,128))
    canvas.alpha_composite(portrait, ((128-portrait.width)//2, 52+(64-portrait.height)//2))
    rgb = canvas.convert('RGB')
    q = rgb.quantize(colors=14, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = [(0,0,0)] + [tuple(q.getpalette()[i*3:i*3+3]) for i in range(14)] + [(0,248,248)]
    out = palimg((128,128), pal)
    data = [0 if alpha==0 else idx+1 for idx,alpha in zip(q.getdata(),canvas.getchannel('A').getdata())]
    out.putdata(data)
    # Reserve final tile for the scrolling digital grid, shown through transparent pixels.
    dr = ImageDraw.Draw(out)
    dr.rectangle((120,120,127,127),fill=0)
    dr.line((120,120,127,120),fill=1)
    dr.line((120,120,120,127),fill=1)
    out.save(GFX/(legacy+'.png'), bits=4)
    palette(GFX/(legacy+'_dark.pal'), pal)
    palette(GFX/(legacy+'_glow.pal'), [(0,0,0),tint]+[(0,0,0)]*14)
    # Map the 128x128 portrait at x=56,y=16. Palette 14 is the portrait palette.
    tilemap = [0xE000] * (32*20)
    for yy in range(15):
        for xx in range(16): tilemap[(yy+2)*32+xx+7]=0xE000+yy*16+xx
    (GFX/(legacy+'_map.bin')).write_bytes(struct.pack('<640H',*tilemap))
    # Palette 15 supplies a subtle grid, behind the full-colour monster.
    (GFX/(backdrop+'_map.bin')).write_bytes(struct.pack('<1024H',*([0xF0FF]*1024)))
    preview = Image.new('RGBA',(240,160),(5,11,24,255))
    preview.alpha_composite(canvas,(56,16))
    preview.save(ROOT/('title-'+legacy+'-portrait.png'))

# Minimal source edits; original save initialization and copyright attribution are preserved.
p = SRC/'src/intro.c'
s=p.read_text()
s=s.replace('        CreateTask(Task_IntroLoadPart1Graphics, 0);\n        SetMainCallback2(MainCB2_Intro);', '        /* Jump to our title after the original save and copyright setup. */\n        SetMainCallback2(MainCB2_Intro);')
# Keep the referenced callback while avoiding unused static-function warnings.
s=re.sub(r'static void MainCB2_Intro\(void\)\n\{.*?\n\}', 'static void MainCB2_Intro(void)\n{\n    SetMainCallback2(MainCB2_EndIntro);\n}', s, count=1, flags=re.S)
p.write_text(s)
p = SRC/'src/title_screen.c'; s=p.read_text()
s=s.replace('#define VERSION_BANNER_LEFT_X 98','#define VERSION_BANNER_LEFT_X 88').replace('#define VERSION_BANNER_RIGHT_X 162','#define VERSION_BANNER_RIGHT_X 152')
s=s.replace('REG_BG2X = -29 * 256;', 'REG_BG2X = 0;')
s=s.replace('CreatePressStartBanner(START_BANNER_X, 108);', 'CreatePressStartBanner(START_BANNER_X, 136);')
s=s.replace('    REG_BLDCNT = 0x2142;\n    REG_BLDALPHA = 0x1F0F;', '    REG_BLDCNT = 0;\n    REG_BLDALPHA = 0;')
# Grid sits behind the portrait; BG0 is the monster and BG1 is the backdrop.
s=s.replace('REG_BG0CNT = BGCNT_PRIORITY(3)', 'REG_BG0CNT = BGCNT_PRIORITY(2)').replace('REG_BG1CNT = BGCNT_PRIORITY(2)', 'REG_BG1CNT = BGCNT_PRIORITY(3)')
p.write_text(s)
p=SRC/'config.mk'; s=p.read_text().replace('POKEMON RUBY','DIGIMON RUBY').replace('POKEMON SAPP','DIGIMON SAPP').replace('GAME_CODE  := DGR','GAME_CODE  := AXV').replace('GAME_CODE  := DGS','GAME_CODE  := AXP'); p.write_text(s)
print('Generated Digimon logos, version banners, title portraits, tilemaps and cartridge branding.')
