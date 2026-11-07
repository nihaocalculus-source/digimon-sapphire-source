#!/usr/bin/env python3
"""Second terminology pass: replaces leftover Pokemon terms in English game text.
Covers src (English blocks only), all data/*.s and data/**/*.inc. Never lengthens a
string in C sources except the checked trainer-class array ([13])."""
from pathlib import Path
import re, json, difflib
root = Path(__file__).resolve().parent / 'source'
R = [  # longest first
 ('POKéMANIAC','DIGIMANIAC'),('POKéMON','DIGIMON'),('POKEMON','DIGIMON'),('Pokémon','Digimon'),
 ('POKéDEX','DIGIDEX'),('Pokédex','DigiDex'),('POKéNAVS','DIGINAVS'),('POKéNAV','DIGINAV'),
 ('POKéBLOCKS','DIGIBLOCKS'),('POKéBLOCK','DIGIBLOCK'),('POKéBALLS','DIGIDISKS'),('POKéBALL','DIGIDISK'),
 ('POKé BALLS','DIGI DISKS'),('POKé BALL','DIGI DISK'),('POKéRUS','DIGIRUS'),('POKéFAN','DIGIFAN'),
 ('POKé MART','DIGI MART'),('POKé DOLL','DIGI DOLL'),('POKéB','DIGIB'),('POKé','DIGI'),
]
pattern = re.compile('|'.join(re.escape(a) for a,_ in R)); M = dict(R)
literal = re.compile(r'"(?:\\.|[^"\\])*"')
macro = re.compile(r'\b_\(\s*(?:"(?:\\.|[^"\\])*"\s*)+\)', re.S)
comment_token = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)
def lang(expr, kind):
    e = bool(re.search(r'\bENGLISH\b', expr)); g = bool(re.search(r'\bGERMAN\b', expr))
    r = True if e and not g else False if g and not e else None
    if kind == 'ifndef' and r is not None: r = not r
    return r
def allowed_lines(text):
    out=[]; stack=[]; allow=True
    for line in text.splitlines(True):
        out.append(allow)
        m = re.match(r'\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)', line)
        if not m: continue
        kind, expr = m.groups()
        if kind in ('if','ifdef','ifndef'):
            c = lang(expr, kind); stack.append((allow, c)); allow = allow and c is not False
        elif kind == 'elif' and stack:
            p,_ = stack[-1]; c = lang(expr,'if'); stack[-1]=(p,c); allow = p and c is not False
        elif kind == 'else' and stack:
            p,c = stack[-1]; allow = p and c is not True
        elif kind == 'endif' and stack: allow = stack.pop()[0]
    return out
def swap(s, allow_pkmn=False):
    parts = re.split(r'(\{[^}]*\})', s)
    for i in range(0, len(parts), 2): parts[i] = pattern.sub(lambda m: M[m.group()], parts[i])
    if allow_pkmn:
        parts = [('DIGI' if p == '{PKMN}' else p) for p in parts]
    return ''.join(parts)
report=[]; patches=[]
files = [p for p in sorted((root/'src').rglob('*')) if p.suffix in ('.c','.h')] + \
        [p for p in sorted((root/'data').rglob('*')) if p.suffix in ('.s','.inc')]
for p in files:
    rel = p.relative_to(root)
    if 'debug' in p.parts or 'debug' in p.name or p.stem.endswith('_de') or p.name.startswith('de_'): continue
    if p.name.startswith(('species_names','pokedex_entries')) or p.name in ('title_screen.c','pokemon_icon.c'): continue
    raw = p.read_bytes()
    try: before = raw.decode('utf-8'); enc='utf-8'
    except UnicodeDecodeError: before = raw.decode('latin-1'); enc='latin-1'
    after = before
    if p.suffix in ('.c','.h'):
        masked = comment_token.sub(lambda m: re.sub(r'[^\n]',' ',m.group()) if m.group().startswith(('//','/*')) else m.group(), before)
        allowed = allowed_lines(before); changes=[]
        pk = p.name == 'trainer_class_names_en.h'
        for m in macro.finditer(masked):
            if not allowed[before.count('\n',0,m.start())]: continue
            old = before[m.start():m.end()]
            new = literal.sub(lambda x: swap(x.group(), pk), old)
            if old != new:
                if not pk: assert len(new) <= len(old), (rel, old)
                changes.append((m.start(), m.end(), new))
        for s,e,n in reversed(changes): after = after[:s]+n+after[e:]
    else:
        lines=[]
        for line in before.splitlines(True):
            if re.match(r'\s*\.(string|braille)\s+"', line): line = literal.sub(lambda x: swap(x.group(), True), line)
            lines.append(line)
        after=''.join(lines)
    if after == before: continue
    p.write_bytes(after.encode(enc))
    n = sum(a!=b for a,b in zip(before.splitlines(), after.splitlines()))
    report.append({'file':str(rel),'changed_lines':n})
    patches.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), str(rel), str(rel)))
(root.parent/'wording-pass.diff').write_text(''.join(patches))
print(json.dumps({'files':len(report),'lines':sum(r['changed_lines'] for r in report)}))
for r in report: print(r)
