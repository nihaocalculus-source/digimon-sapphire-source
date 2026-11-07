#!/usr/bin/env python3
"""Ball item family -> DISK in English text (item names, descriptions, dialogue)."""
from pathlib import Path
import re, importlib.util
spec = importlib.util.spec_from_file_location('w', Path(__file__).with_name('digimon_wording_pass.py'))
root = Path(__file__).resolve().parent / 'source'
ball = re.compile(r'\b(MASTER|ULTRA|GREAT|SAFARI|NET|DIVE|NEST|REPEAT|TIMER|LUXURY|PREMIER) BALL(S?)\b')
literal = re.compile(r'"(?:\\.|[^"\\])*"')
def fix(s): return ball.sub(lambda m: f'{m.group(1)} DISK{m.group(2)}', s)
count=0
for p in [p for p in (root/'data').rglob('*') if p.suffix in ('.s','.inc')]:
    t = p.read_text(encoding='utf-8', errors='surrogateescape'); lines = t.splitlines(True); out=[]; prev=''
    for line in lines:
        if re.match(r'\s*\.string\s+"', line):
            new = literal.sub(lambda x: fix(x.group()), line)
            if re.search(r'DIGI\\n"\s*$', prev): new = re.sub(r'(\.string\s+")BALL', r'\1DISK', new)
            if new != line: count+=1
            line = new
        out.append(line); prev = line
    nt=''.join(out)
    if nt!=t: p.write_text(nt, encoding='utf-8', errors='surrogateescape')
for name in ('src/data/items_en.h','src/data/item_descriptions_en.h','src/decoration.c'):
    p = root/name
    if not p.exists(): continue
    t = p.read_text(encoding='utf-8'); nt = literal.sub(lambda x: fix(x.group()), t)
    nt = nt.replace('"the shape of a DIGI\\n"\n    "BALL.")', '"the shape of a DIGI\\n"\n    "DISK.")').replace('"printed with DIGI\\n"\n    "BALLS.")','"printed with DIGI\\n"\n    "DISKS.")')
    if nt!=t: p.write_text(nt, encoding='utf-8'); count+=sum(a!=b for a,b in zip(t.splitlines(), nt.splitlines()))
print('changed lines', count)
