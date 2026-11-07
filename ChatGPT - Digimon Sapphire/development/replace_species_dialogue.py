"""Replace printed species names; never modify identifiers, labels or control codes."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'source'
rows=json.loads((ROOT/'roster.json').read_text())
words={r['original']:r['short_name'] for r in rows}
words.update({'POKéNAV':'DIGINAV','POKENAV':'DIGINAV','POKéFAN':'DIGIFAN','POKéMANIAC':'DIGIMANIAC','POKéBLOCK':'DIGIBLOCK','POKéCENTER':'DIGICENTER'})
pattern=re.compile(r'(?<![A-Za-z0-9_])('+'|'.join(re.escape(w) for w in sorted(words,key=len,reverse=True))+r')(?![A-Za-z0-9_])')
quoted=re.compile(r'"(?:\\.|[^"\\])*"')
macro=re.compile(r'\b_\(\s*(?:"(?:\\.|[^"\\])*"\s*)+\)',re.S)
report=[]
def replace_literal(m):
 chunks=re.split(r'(\{[^}]*\})',m[0])
 for i in range(0,len(chunks),2):chunks[i]=pattern.sub(lambda n:words[n[0]],chunks[i])
 return ''.join(chunks)
for top in ['src','data/maps','data/text']:
 for p in (SRC/top).rglob('*'):
  if p.suffix not in ['.h','.c','.inc'] or any(k in p.parts for k in ['graphics','debug']):continue
  if p.name.startswith(('species_names','pokedex_entries')) or p.name in ['title_screen.c','intro.c'] or p.name.endswith('_de.h'):continue
  raw=p.read_bytes()
  try:s=raw.decode('utf-8');enc='utf-8'
  except UnicodeDecodeError:s=raw.decode('latin-1');enc='latin-1'
  if p.suffix=='.inc':
   new=''.join(quoted.sub(replace_literal,line) if re.match(r'\s*\.(string|braille)\s+"',line) else line for line in s.splitlines(True))
  else:new=macro.sub(lambda m:quoted.sub(replace_literal,m[0]),s)
  if new!=s:p.write_bytes(new.encode(enc));report.append(str(p.relative_to(SRC)))
(ROOT/'species-dialogue-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Updated printed names in',len(report),'files')
