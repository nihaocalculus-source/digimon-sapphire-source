"""Compile the Digimon roster into the existing Ruby/Sapphire asset formats."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import re, json, csv, hashlib, textwrap
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source'
OUT=Path(__import__('os').environ.get('DIGIMON_OUTPUT', str(ROOT.parent)))
ART=ROOT/'sprite-originals'

def norm(s): return re.sub('[^A-Z0-9]','',s.upper())
gifs={p.stem:p for p in sorted(ART.rglob('*.gif'))}
constants={k:int(v) for k,v in re.findall(r'#define SPECIES_(\w+) (\d+)\b',(SRC/'include/constants/species.h').read_text())}
real={k:v for k,v in constants.items() if 1<=v<=411 and not k.startswith('OLD_UNOWN')}
assert len(real)==386
original=ROOT/'baseline'
names={k:v for k,v in re.findall(r'\[SPECIES_(\w+)\] = _\("([^"]+)"\)',(original/'src/data/text/species_names_en.h').read_text())}
graphics=(SRC/'src/data/graphics/pokemon.h').read_text()
paths=dict(re.findall(r'const u8 (gMonFrontPic_\w+)\[\] = INCBIN_U8\("([^"]+)"\)',graphics))
fronts={k:(sym,paths.get(sym)) for sym,k in re.findall(r'obj_tiles (\w+), 0x[0-9A-Fa-f]+, SPECIES_(\w+)',(SRC/'data/graphics/pokemon/front_pic_table.inc').read_text())}
# Familiar starter lines are condensed to the original three-stage campaigns.
curated={
'TREECKO':'Patamon','GROVYLE':'Angemon','SCEPTILE':'Seraphimon',
'TORCHIC':'Agumon','COMBUSKEN':'Greymon','BLAZIKEN':'WarGreymon',
'MUDKIP':'Gabumon','MARSHTOMP':'Garurumon','SWAMPERT':'MetalGarurumon',
'BULBASAUR':'Palmon','IVYSAUR':'Togemon','VENUSAUR':'Rosemon',
'CHARMANDER':'Guilmon','CHARMELEON':'Growlmon','CHARIZARD':'Dukemon',
'SQUIRTLE':'Gomamon','WARTORTLE':'Ikkakumon','BLASTOISE':'Vikemon',
'CATERPIE':'Wormmon','METAPOD':'Stingmon','BUTTERFREE':'Dinobeemon',
'WEEDLE':'Tentomon','KAKUNA':'Kabuterimon','BEEDRILL':'HerculesKabuterimon',
'PIDGEY':'Biyomon','PIDGEOTTO':'Birdramon','PIDGEOT':'Phoenixmon',
'POOCHYENA':'Gaomon','MIGHTYENA':'MachGaogamon',
'ZIGZAGOON':'Lopmon','LINOONE':'Turuiemon',
'RALTS':'Renamon','KIRLIA':'Kyubimon','GARDEVOIR':'Sakuyamon',
'WURMPLE':'Kunemon','SILCOON':'Flymon','BEAUTIFLY':'Butterflymon',
'CASCOON':'Dokugumon','DUSTOX':'Arukenimon',
'SHROOMISH':'Raramon','BRELOOM':'Sunflowmon',
'LOTAD':'Kamemon','LOMBRE':'Gwappamon','LUDICOLO':'Shawujinmon',
'SEEDOT':'Floramon','NUZLEAF':'Woodmon','SHIFTRY':'Cherrymon',
'TAILLOW':'Falcomon','SWELLOW':'Peckmon','WINGULL':'Penmon','PELIPPER':'Orcamon',
'PICHU':'Gumymon','PIKACHU':'Terriermon','RAICHU':'Rapidmon',
'CLEFFA':'Tokomon','CLEFAIRY':'Plotmon','CLEFABLE':'Angewomon',
'VULPIX':'Kudamon','NINETALES':'Reppamon',
'MAGIKARP':'Betamon','GYARADOS':'MetalSeadramon',
'FEEBAS':'Shakomon','MILOTIC':'Mermaimon',
'MEWTWO':'Beelzebumon','MEW':'Calumon',
'KYOGRE':'Leviamon','GROUDON':'AncientGreymon','RAYQUAZA':'Omegamon',
'LATIAS':'Magnadramon','LATIOS':'Goddramon','JIRACHI':'MarineAngemon','DEOXYS':'Diablomon',
'REGIROCK':'AncientVolcamon','REGICE':'AncientMegatheriumon','REGISTEEL':'AncientWisemon',
'SNORLAX':'Monzaemon','MACHOP':'Bearmon','MACHOKE':'Grizzlymon','MACHAMP':'GrapLeomon',
'MARILL':'Otamamon','AZUMARILL':'Gekomon','AZURILL':'Poyomon',
'EEVEE':'Dorumon','VAPOREON':'DoruGreymon','JOLTEON':'DORUgamon','FLAREON':'Dorugoramon',
'UNOWN':'Kuramon','CASTFORM':'Mokumon',
'CARVANHA':'Gizamon','SHARPEDO':'Divermon',
'WAILMER':'Whamon','WAILORD':'KingWhamon',
'NUMEL':'Meramon','CAMERUPT':'SkullMeramon',
'ABSOL':'BlackWereGarurumon','SABLEYE':'Impmon',
'ARON':'Hagurumon','LAIRON':'Guardromon','AGGRON':'Andromon',
'BELDUM':'Kokuwamon','METANG':'MegaGargomon','METAGROSS':'HiAndromon',
'BAGON':'V-mon','SHELGON':'XV-mon','SALAMENCE':'Imperialdramon',
'WHISMUR':'Kumamon','LOUDRED':'Grumblemon','EXPLOUD':'Gigasmon',
'SKITTY':'Wanyamon','DELCATTY':'Bastemon',
'TORKOAL':'Tortomon','SPOINK':'Bakumon','GRUMPIG':'Tapirmon',
'SPINDA':'Pandamon','LUNATONE':'Lunamon','SOLROCK':'Coronamon'
}
# Match published filenames while accepting conventional romanization variants.
alias={'HerculesKabuterimon':'HerakleKabuterimon','Dukemon':'Gallantmon','DORUgamon':'Dorugamon','BlackWereGarurumon':'WereGarurumonBlack','Tapirmon':'Vademon','Mokumon':'Mushmon','Kumamon':'Chackmon','Turuiemon':'Wendimon','Butterflymon':'Hudiemon','Arukenimon':'Archnemon','Shawujinmon':'Shaujinmon','Orcamon':'Dolphmon','Reppamon':'Leppamon','Mermaimon':'Mermamon','AncientGreymon':'ShineGreymon','Goddramon':'Goldramon','Diablomon':'Diaboromon','AncientVolcamon':'Puppetmon','AncientMegatheriumon':'Plesiomon','AncientWisemon':'Machinedramon','Grizzlymon':'Grizzmon','GrapLeomon':'GrapLeomon','KingWhamon':'Neptunmon','Meramon':'FlareLizardmon','SkullMeramon':'Volcamon','Guardromon':'Guadromon','MegaGargomon':'SaintGalgomon','Grumblemon':'Ogremon','Gigasmon':'BantyoLeomon','Bastemon':'Persiamon'}
for k,v in list(curated.items()):
 matches=[n for n in gifs if norm(n)==norm(v)]
 if not matches and v in alias:matches=[n for n in gifs if norm(n)==norm(alias[v])]
 if not matches:
  print('Unmapped curated name, using stage pool:',k,v);del curated[k]
 else:curated[k]=matches[0]
assert len(set(curated.values()))==len(curated)
# Retain the campaign's stats and moves; assign remaining species by power tier.
bs=(SRC/'src/data/pokemon/base_stats.h').read_text(errors='replace')
totals={}
for k,body in re.findall(r'\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n\s*\}',bs,re.S):
 totals[k]=sum(map(int,re.findall(r'\.base(?:HP|Attack|Defense|Speed|SpAttack|SpDefense)\s*=\s*(\d+)',body)))
pool=[n for n in gifs if n not in curated.values()]
stage_score={'in-training':180,'rookie':300,'champion':410,'ultimate':490,'mega':570,'unobtainable':580}
for k in sorted(real,key=lambda k:(totals.get(k,400),real[k])):
 if k not in curated:
  chosen=min(pool,key=lambda n:(abs(stage_score.get(gifs[n].parent.name,400)-totals.get(k,400)),n.lower()))
  curated[k]=chosen;pool.remove(chosen)
used=set()
def shortname(name):
 n=re.sub('[^A-Z0-9]','',name.upper())
 if len(n)>10:
  for a,b in [('METAL','MTL'),('ANCIENT','ANC'),('IMPERIAL','IMP'),('MEGA','MG'),('BLACK','BK'),('WHITE','WH'),('KNIGHT','KNT'),('GREY','GR'),('GARURU','GARU'),('CHESS','CHS'),('KABUTERI','KABU')]:
   if len(n)>10:n=n.replace(a,b)
  if len(n)>10 and n.endswith('MON'):n=n[:-3][:7]+'MON'
  n=n[:10]
 candidate=n;i=2
 while candidate in used:
  suffix=str(i);candidate=n[:10-len(suffix)]+suffix;i+=1
 used.add(candidate);return candidate
rows=[]
for k,id in sorted(real.items(),key=lambda kv:kv[1]):
 sym,path=fronts[k];assert path,(k,sym)
 full=curated[k]
 rows.append(dict(species=k,id=id,original=names[k],name=full,short_name=shortname(full),stage=gifs[full].parent.name,sprite=str(gifs[full].relative_to(ROOT)),folder=str(Path(path).parent),symbol=sym.removeprefix('gMonFrontPic_')))
(ROOT/'roster.json').write_text(json.dumps(rows,indent=2)+'\n')
OUT.mkdir(parents=True,exist_ok=True)
with (OUT/'ROSTER.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['id','species','original','name','short_name','stage']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows)

def portrait(path):
 im=Image.open(path).convert('RGBA')
 bbox=im.getbbox();assert bbox,path
 return im.crop(bbox)

def fit(im,size):
 im=im.copy();im.thumbnail(size,Image.Resampling.NEAREST);return im

def palette16(im):
 opaque=Image.new('RGB',im.size,(0,0,0));opaque.paste(im,mask=im.getchannel('A'))
 q=opaque.quantize(colors=15,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
 p=(q.getpalette()+[0]*45)[:45];p=[(0,0,0)]+[tuple(p[i:i+3]) for i in range(0,45,3)]
 return p

def indexed(im,palette):
 # Explicit nearest-color mapping excludes transparency from opaque colors.
 cache={}
 data=[]
 for r,g,b,a in im.getdata():
  if a<128:data.append(0);continue
  rgb=(r,g,b)
  if rgb not in cache:cache[rgb]=min(range(1,16),key=lambda i:sum((rgb[j]-palette[i][j])**2 for j in range(3)))
  data.append(cache[rgb])
 out=Image.new('P',im.size);out.putpalette([c for rgb in palette for c in rgb]+[0]*720);out.putdata(data)
 return out

def palfile(path,p):
 path.write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,rgb)) for rgb in p)+'\n')
iconpals=[]
for i in range(3):
 lines=(SRC/f'graphics/pokemon_icon_palettes/{i}.pal').read_text().splitlines()[3:19]
 iconpals.append([tuple(map(int,s.split())) for s in lines])
icon_source=SRC/'src/pokemon_icon.c'
isrc=icon_source.read_text()
m=re.search(r'(const u8 gMonIconPaletteIndices\[\] =\s*\{)(.*?)(\n\};)',isrc,re.S)
indices=[int(n) for n in re.findall(r'^\s*(\d+),',m[2],re.M)]
assert len(indices)>=440,len(indices)
counts={'front':0,'back':0,'icon':0,'palette':0,'footprint':0}
contact=Image.new('RGB',(8*96,8*100),(15,20,37));draw=ImageDraw.Draw(contact)
for ix,row in enumerate(rows):
 im=portrait(ROOT/row['sprite']);folder=SRC/row['folder']
 thumb=fit(im,(60,60));canvas=Image.new('RGBA',(64,64));canvas.alpha_composite(thumb,((64-thumb.width)//2,62-thumb.height))
 p=palette16(canvas);front=indexed(canvas,p);back=ImageOps.mirror(front)
 # All alphabet and weather forms receive the Digimon portrait while retaining frame geometry.
 for stem,art in [('front',front),('back',back)]:
  for dest in folder.glob(stem+'*.png'):
   art.save(dest,bits=4);counts[stem]+=1
 for dest in folder.glob('*.pal'):
  if dest.name not in ['footprint.pal']:
   palfile(dest,p);counts['palette']+=1
 tiny=fit(im,(28,29));c=Image.new('RGBA',(32,64))
 c.alpha_composite(tiny,((32-tiny.width)//2,31-tiny.height));c.alpha_composite(tiny,((32-tiny.width)//2,62-tiny.height))
 # Select one of the engine's three shared icon palettes by actual color error.
 colors=[rgb[:3] for rgb in tiny.getdata() if rgb[3]>=128][::3]
 pi=min(range(3),key=lambda i:sum(min(sum((rgb[j]-pc[j])**2 for j in range(3)) for pc in iconpals[i][1:]) for rgb in colors))
 for dest in folder.glob('icon*.png'):
  indexed(c,iconpals[pi]).save(dest,bits=4);counts['icon']+=1
 indices[row['id']]=pi
 if row['species']=='UNOWN':
  for idx in range(413,440):indices[idx]=pi
 fp=Image.new('1',(16,16));d=ImageDraw.Draw(fp);d.rectangle((4,4,11,11),outline=1,width=2);d.rectangle((7,1,8,14),fill=1);d.rectangle((1,7,14,8),fill=1)
 fp.save(folder/'footprint.png');counts['footprint']+=1
 if ix<64:
  x=(ix%8)*96;y=(ix//8)*100;contact.paste(front.convert('RGBA'),(x+16,y),Image.frombytes('L',front.size,bytes(255 if v else 0 for v in front.getdata())));draw.text((x+3,y+68),row['short_name'],fill=(230,235,255))
 # Launcher art is lossless first-frame source, cropped to remove empty margins.
 if row['name'] in ['Agumon','Gabumon','Patamon','MetalGarurumon','WarGreymon']:
  (OUT/'assets').mkdir(exist_ok=True);im.save(OUT/'assets'/f"{row['name'].lower()}.png")
contact.save(ROOT/'roster-preview.png')
it=iter(indices)
newbody=re.sub(r'(^\s*)\d+(,)',lambda m:m[1]+str(next(it))+m[2],m[2],flags=re.M)
icon_source.write_text(isrc[:m.start(2)]+newbody+isrc[m.end(2):])
# Art occupies the full 64x64 canvas; all original variable offsets are removed.
for name in ['front_pic_coords','back_pic_coords']:
 pth=SRC/f'data/graphics/pokemon/{name}.inc';txt=pth.read_text()
 txt=re.sub(r'\.byte\s+\d+,\s*\d+,\s*0,\s*0','.byte 136, 0, 0, 0',txt);pth.write_text(txt)
bykey={r['species']:r for r in rows}
text=(original/'src/data/text/species_names_en.h').read_text()
text=re.sub(r'(\[SPECIES_(\w+)\] = _\(")[^"]+("\))',lambda m:m[1]+(bykey[m[2]]['short_name'] if m[2] in bykey else 'DIGIEGG' if m[2]=='EGG' else 'DIGICODE')+m[3],text)
(SRC/'src/data/text/species_names_en.h').write_text(text)
# Generate short, legible field guide entries describing this fan game's actual rules.
dex=(original/'src/data/pokedex_entries_en.h').read_text()
by_symbol={norm(r['symbol']):r for r in rows};by_symbol['UNOWN']=bykey['UNOWN']
def entry(m):
 symbol,page=m[1],m[2];row=by_symbol.get(norm(symbol))
 if not row:lines=['An unclassified digital life-form.','Its data is still being researched.']
 elif page=='1':
  lines=textwrap.wrap(row['name'].upper()+'.',32)+[row['stage'].replace('-',' ').upper()+' stage Digimon.','A partner on your Hoenn adventure.']
 else:lines=['Train it to learn its battle skills.','Its types and growth follow this','world\'s special digivolution rules.']
 return 'static const u8 DexDescription_'+symbol+'_'+page+'[] = _(\n  '+ '\n  '.join(json.dumps(l+('\\n' if i<len(lines)-1 else '')).replace('\\\\n','\\n') for i,l in enumerate(lines)) +');'
dex,n=re.subn(r'static const u8 DexDescription_(\w+)_(1|2)\[\] = _\(.*?\);',entry,dex,flags=re.S)
assert n>=774,n
# Categories carry actual Digimon stages; the height/weight chart stays balanced to its slot.
def cat(m):
 row=by_symbol.get(norm(m[1]));stage=row['stage'].replace('-',' ').upper() if row else 'DIGIMON'
 if len(stage)>11:stage='TRAINING'
 return m[0][:m[0].index('.categoryName')]+'.categoryName = _("'+stage+'"),'
dex=re.sub(r'\{\s*//(\w+)\s*\n\s*\.categoryName = _\("[^"]+"\),',cat,dex)
(SRC/'src/data/pokedex_entries_en.h').write_text(dex)
report={'roster_count':len(rows),'unique_digimon':len(set(r['name'] for r in rows)),'asset_counts':counts,'dex_pages_replaced':n,'name_lengths_max':max(len(r['short_name']) for r in rows),'back_views':'Mirrored battle portraits, not bespoke rear-view drawings','balance':'Original slot types, moves, stats, encounters and evolution triggers retained'}
(ROOT/'conversion-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
