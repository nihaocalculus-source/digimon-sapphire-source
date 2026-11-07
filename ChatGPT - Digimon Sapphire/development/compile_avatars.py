"""Compile the included Tai/Matt atlases to indexed native frame sheets.
Run with a Python installation containing Pillow, then Build Games.command.
This changes only avatar graphics and palettes, never game events or save data.
"""
from pathlib import Path
from PIL import Image, ImageOps
import shutil
P=Path(__file__).resolve().parent.parent
D=P/'development'; S=D/'source'; A=D/'campaign_assets'; G=S/'graphics/digimon'
ATLAS={name:A/(name+'-atlas.png') for name in ('tai','matt')}
def palette(im):
 q=im.convert('RGB').quantize(colors=15,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
 raw=(q.getpalette()+[0]*45)[:45];return [(0,0,0)]+[tuple(raw[i:i+3]) for i in range(0,45,3)]
def indexed(im,pal):
 cache={};data=[]
 for px in im.getdata():
  if px[3]<128:data.append(0);continue
  rgb=px[:3]
  if rgb not in cache:cache[rgb]=min(range(1,16),key=lambda k:sum((rgb[c]-pal[k][c])**2 for c in range(3)))
  data.append(cache[rgb])
 out=Image.new('P',im.size);out.putpalette([v for c in pal for v in c]+[0]*720);out.putdata(data);return out

def palfile(path,pal):path.write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in pal)+'\n')
def frame(im,size,limit=None):
 im=im.crop(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox());im.thumbnail(limit or (size[0]-2,size[1]-2),Image.Resampling.NEAREST)
 out=Image.new('RGBA',size);out.alpha_composite(im,((size[0]-im.width)//2,size[1]-1-im.height));return out
actors={};rules=[]
for who,path in ATLAS.items():
 saved=A/(who+'-atlas.png')
 if not saved.exists():shutil.copy2(path,saved)
 atlas=Image.open(saved).convert('RGBA');cells=[]
 for y in range(3):
  for x in range(3):
   cell=atlas.crop((x*atlas.width//3,y*atlas.height//3,(x+1)*atlas.width//3,(y+1)*atlas.height//3));cells.append(cell.crop(cell.getbbox()))
 pal=palette(atlas);actors[who]=(cells,pal);folder=G/who;folder.mkdir(exist_ok=True);palfile(folder/'normal.pal',pal)
 # Native normal-animation frame order: down/up/left idle, then paired steps.
 order=[0,1,2,3,6,4,7,5,8,0,1,2,3,6,4,7,5,8]
 for original in (S/'graphics/object_events/pics/people/brendan').glob('*.png'):
  old=Image.open(original);fw=16 if original.stem in ('normal','decorating') else 32;fh=32
  sheet=Image.new('RGBA',old.size)
  for i in range(old.width//fw*(old.height//fh)):
   cell=frame(cells[order[i%18]],(fw,fh),(16,26));sheet.alpha_composite(cell,((i%(old.width//fw))*fw,(i//(old.width//fw))*fh))
  indexed(sheet,pal).save(folder/original.name,bits=4)
  rules.append(f'graphics/digimon/{who}/{original.stem}.4bpp: %.4bpp: %.png\n\t$(GBAGFX) $< $@ -mwidth {fw//8} -mheight 4\n')
 # Native front/back trainer sheets retain their original animation geometry.
 for mode,cellid in [('front',0),('back',1)]:
  source=S/'graphics/trainers'/('brendan.png' if mode=='front' else 'brendan_back.png');old=Image.open(source)
  sheet=Image.new('RGBA',old.size)
  for yy in range(0,old.height,64):
   for xx in range(0,old.width,64):sheet.alpha_composite(frame(cells[cellid],(64,64),(54,60)),(xx,yy))
  indexed(sheet,pal).save(folder/('trainer_'+mode+'.png'),bits=4)

print("Compiled Tai/Matt avatar source sheets.")
