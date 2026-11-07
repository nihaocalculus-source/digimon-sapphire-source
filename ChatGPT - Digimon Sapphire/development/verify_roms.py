"""Verify the actual linked cartridges against source assets and the roster."""
from pathlib import Path
import json,re,subprocess,hashlib,struct
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'source'
rows=json.loads((ROOT/'roster.json').read_text())
graphics=(SRC/'src/data/graphics/pokemon.h').read_text()
assets=dict(re.findall(r'const u8 (\w+)\[\] = INCBIN_U8\("([^"]+)"\)',graphics))
results=[]
for edition,code,title in [('sapphire',b'AXPE',b'DIGIMON SAPP'),('ruby',b'AXVE',b'DIGIMON RUBY')]:
 rom=(SRC/f'poke{edition}.gba').read_bytes()
 symbols={name:int(addr,16) for addr,kind,name in (line.split() for line in subprocess.check_output(['arm-none-eabi-nm',str(SRC/f'poke{edition}.elf')],text=True).splitlines() if len(line.split())==3)}
 assert len(rom)==16777216
 assert rom[0xac:0xb0]==code,(edition,rom[0xac:0xb0])
 assert rom[0xa0:0xac].rstrip(b'\0')==title
 assert rom[0xbd]==(-sum(rom[0xa0:0xbd])-0x19)&255
 checked=0
 for sym,path in assets.items():
  if sym not in symbols:continue
  payload=(SRC/path).read_bytes();offset=symbols[sym]-0x8000000
  assert rom[offset:offset+len(payload)]==payload,(edition,sym,path)
  checked+=1
 names=symbols['gSpeciesNames']-0x8000000
 enc=lambda s:bytes(ord(c)-ord('A')+0xbb if 'A'<=c<='Z' else ord(c)-ord('0')+0xa1 for c in s)+b'\xff'
 table=symbols['gMonFrontPicTable']-0x8000000
 for row in rows:
  expected=enc(row['short_name']);off=names+row['id']*11
  assert rom[off:off+len(expected)]==expected,(edition,row['name'],'name')
  ptr,size,tag=struct.unpack_from('<IHH',rom,table+row['id']*8)
  assert ptr==symbols['gMonFrontPic_'+row['symbol']] and tag==row['id'],(edition,row['name'],'front pointer')
  assert size==2048 or row['species']=='CASTFORM',(edition,row['name'],'size')
 results.append({'edition':edition,'romBytes':len(rom),'sha256':hashlib.sha256(rom).hexdigest(),'headerChecksum':'pass','saveHardwareCode':code.decode(),'speciesNamesVerified':len(rows),'frontPointersVerified':len(rows),'compiledGraphicsArraysVerified':checked})
report={'status':'pass','roms':results,'scope':'Binary/header/asset/name/pointer checks; not a campaign playthrough'}
(ROOT/'rom-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
