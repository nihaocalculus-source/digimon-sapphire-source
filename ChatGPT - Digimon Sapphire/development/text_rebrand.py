from pathlib import Path
import re,json,difflib
root=Path(__file__).resolve().parent/'source'
replacements={'POKéMON':'DIGIMON','POKEMON':'DIGIMON','Pokémon':'Digimon','Pokemon':'Digimon','POKéDEX':'DIGIDEX','POKEDEX':'DIGIDEX','Pokédex':'DigiDex','Pokedex':'DigiDex','POKé BALL':'DIGI DISK','POKE BALL':'DIGI DISK','Poké Ball':'Digi Disk','Poke Ball':'Digi Disk','POKéBALL':'DIGIDISK','POKEBALL':'DIGIDISK','Pokéball':'DigiDisk','Pokeball':'DigiDisk'}
for a,b in replacements.items():assert len(b)<=len(a),(a,b)
pattern=re.compile('|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True)))
literal=re.compile(r'"(?:\\.|[^"\\])*"')
macro=re.compile(r'\b_\(\s*(?:"(?:\\.|[^"\\])*"\s*)+\)',re.S)
comment_token=re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',re.S)

def lang(expr,kind):
 e=bool(re.search(r'\bENGLISH\b',expr));g=bool(re.search(r'\bGERMAN\b',expr))
 result=True if e and not g else False if g and not e else None
 if kind=='ifndef' and result is not None:result=not result
 return result

def allowed_lines(text):
 out=[];stack=[];allow=True
 for line in text.splitlines(True):
  out.append(allow)
  m=re.match(r'\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)',line)
  if not m:continue
  kind,expr=m.groups()
  if kind in ('if','ifdef','ifndef'):
   cond=lang(expr,kind);stack.append((allow,cond));allow=allow and cond is not False
  elif kind=='elif' and stack:
   parent,_=stack[-1];cond=lang(expr,'if');stack[-1]=(parent,cond);allow=parent and cond is not False
  elif kind=='else' and stack:
   parent,cond=stack[-1];allow=parent and cond is not True
  elif kind=='endif' and stack:allow=stack.pop()[0]
 return out

def swap(s):
 parts=re.split(r'(\{[^}]*\})',s)
 for i in range(0,len(parts),2):parts[i]=pattern.sub(lambda m:replacements[m.group()],parts[i])
 result=''.join(parts)
 assert re.findall(r'\{[^}]*\}|\\.',s)==re.findall(r'\{[^}]*\}|\\.',result)
 assert len(result)<=len(s)
 return result

report=[];patches=[]
for top in [root/'src',root/'data/maps',root/'data/text']:
 for p in sorted(top.rglob('*')):
  if p.suffix not in ('.c','.h','.inc'):continue
  relative=p.relative_to(root)
  if any(x in p.parts for x in ('graphics','debug')) or p.name in ('title_screen.c','pokemon_icon.c','evolution.h') or p.name.startswith(('species_names','pokedex_entries')) or p.stem.endswith('_de') or p.name.startswith('de_'):continue
  raw=p.read_bytes()
  try:before=raw.decode('utf-8');encoding='utf-8'
  except UnicodeDecodeError:before=raw.decode('latin-1');encoding='latin-1'
  after=before
  if p.suffix in ('.c','.h'):
   masked=comment_token.sub(lambda m:re.sub(r'[^\n]',' ',m.group()) if m.group().startswith(('//','/*')) else m.group(),before)
   allowed=allowed_lines(before)
   changes=[]
   for m in macro.finditer(masked):
    if not allowed[before.count('\n',0,m.start())]:continue
    old=before[m.start():m.end()]
    new=literal.sub(lambda x:swap(x.group()),old)
    if old!=new:changes.append((m.start(),m.end(),new))
   for start,end,new in reversed(changes):after=after[:start]+new+after[end:]
  else:
   lines=[]
   for line in before.splitlines(True):
    if re.match(r'\s*\.(string|braille)\s+"',line):line=literal.sub(lambda x:swap(x.group()),line)
    lines.append(line)
   after=''.join(lines)
  if before==after:continue
  assert len(before.splitlines())==len(after.splitlines()),relative
  changes=sum(a!=b for a,b in zip(before.splitlines(),after.splitlines()))
  p.write_bytes(after.encode(encoding))
  report.append({'file':str(relative),'changed_lines':changes})
  patches.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(relative)+' (before)',tofile=str(relative)+' (after)'))
(root.parent/'text-rebrand-report.json').write_text(json.dumps(report,indent=2)+'\n')
(root.parent/'text-rebrand.diff').write_text(''.join(patches))
print(json.dumps({'changed_files':len(report),'changed_lines':sum(r['changed_lines'] for r in report),'src_files':[r for r in report if r['file'].startswith('src/')]} ,indent=2))
