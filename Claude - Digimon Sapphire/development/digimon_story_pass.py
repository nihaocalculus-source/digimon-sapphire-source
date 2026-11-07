#!/usr/bin/env python3
"""Main-story pass: TEAM MAGMA -> TEAM VIRUS, TEAM AQUA -> TEAM ABYSS, and rewrites of the
leader/lore messages so the villain plot fits the glitch-world + Dark Masters story."""
from pathlib import Path
import re
root = Path(__file__).resolve().parent / 'source'
lit = re.compile(r'"(?:\\.|[^"\\])*"')
def team(s):
    s = re.sub(r'\bMAGMA\b(?! ARMOR)', 'VIRUS', s)
    return re.sub(r'\bAQUA\b', 'ABYSS', s)
# 1) renames in all English data strings (not ability names)
for p in (root/'data').rglob('*'):
    if p.suffix not in ('.s','.inc') or p.name == 'ability_names.inc': continue
    t = p.read_text(encoding='utf-8', errors='surrogateescape')
    nt = ''.join(lit.sub(lambda m: team(m.group()), l) if re.match(r'\s*\.string\s+"', l) else l for l in t.splitlines(True))
    if nt != t: p.write_text(nt, encoding='utf-8', errors='surrogateescape')
for name, pairs in {
    'src/strings.c': [('gExpandedPlaceholder_Aqua[] = _("AQUA");\nconst u8 gExpandedPlaceholder_Magma[] = _("MAGMA");',
                       'gExpandedPlaceholder_Aqua[] = _("ABYSS");\nconst u8 gExpandedPlaceholder_Magma[] = _("VIRUS");')],
    'src/data/text/trainer_class_names_en.h': [('_("AQUA LEADER")','_("ABYSS LEADER")'),('_("TEAM AQUA")','_("TEAM ABYSS")'),('_("AQUA ADMIN")','_("ABYSS ADMIN")'),
                       ('_("MAGMA LEADER")','_("VIRUS LEADER")'),('_("TEAM MAGMA")','_("TEAM VIRUS")'),('_("MAGMA ADMIN")','_("VIRUS ADMIN")')],
}.items():
    p = root/name; t = p.read_text(encoding='utf-8')
    for a, b in pairs:
        assert t.count(a) >= 1 or t.count(b) >= 1, (name, a); t = t.replace(a, b, 1)  # first = ENGLISH block
    p.write_text(t, encoding='utf-8')

# 2) message rewrites (label -> new text in .string escape form)
R = {}
R['MtChimney_Text_1B37BB'] = r"The data inside this METEORITE...\pPumped through this machine, it will\nmake MT. CHIMNEY's code overflow...\pFufufu... Molten data will pour out\nand harden into brand-new land,\land the sea's code will shrink away...$"
R['MtChimney_Text_1B38B3'] = r"MAXIE: You again...\pListen. This world is broken.\nThe glitch is tearing HOENN apart.\pThe sea's data spreads like rot,\nand the land shrinks day by day.\pThat is why we of TEAM VIRUS will\nrewrite this world as solid ground.\pA voice in the glitch promised me a\nnew world built on that ground...\pI can't allow a child like you to\nget in our way.\pI, MAXIE, will show you the\nconsequences of meddling!$"
R['MtChimney_Text_1B2DEE'] = r"The data inside this METEORITE...\pPumped through this machine, it will\nfreeze MT. CHIMNEY's fire code...\pFufufu... The cold crater will fill\nwith rain, and the sea's code will\lspread over the land...$"
R['MtChimney_Text_1B2ED9'] = r"ARCHIE: You again...\pListen. This world is broken.\nThe glitch is tearing HOENN apart.\pThe land's data has cracked and\nrotted, and all life suffers for it.\pThat is why we of TEAM ABYSS will\nwash this world clean with the sea.\pA voice in the glitch promised me a\nnew world born from that sea...\pI can't allow a child like you to\nget in our way.\pI, ARCHIE, will show you the\nconsequences of meddling!$"
R['SlateportCity_OceanicMuseum_2F_Text_MaxieWarning'] = r"I am TEAM VIRUS's MAXIE.\pWhy on earth do you feel compelled\nto mess up TEAM VIRUS's plans?\pThis glitch-torn world is breaking.\nOnly solid ground can save it.\pThat's why TEAM VIRUS will rewrite\nthe sea's code into new land.\pDon't you agree? What we are doing\nis a magnificent undertaking.\pWell, no matter...\nYou're young.\pYour inability to understand our\nnoble cause can't be helped...\pBut, if you were to impede us ever\nagain, you'll see no mercy from us!\pKeep that firmly in mind!\nFarewell!$"
R['SlateportCity_OceanicMuseum_2F_Text_ArchieWarning'] = r"I am TEAM ABYSS's ARCHIE.\pTell me, why do you meddle in the\nnoble affairs of TEAM ABYSS?\pThis glitch-torn world is breaking.\nOnly the sea can wash it clean.\pSo, TEAM ABYSS will rewrite the\nland's code into open sea.\pDon't you agree? What we are doing\nis a magnificent undertaking.\pAh, fine...\nYou're still too young.\pIt can't be helped that you do not\nunderstand our ideals.\pBut, if you ever oppose us again,\nthere will be consequences!\pHeed my warning!\nFarewell!$"
pyre = r"MT. PYRE is where the data of DIGIMON\nthat were deleted comes to rest...\pHere it waits in peace until it is\nreborn as a DIGI-EGG.\pThis is a high place where one can\nsee all of HOENN...\pEven the glitch cannot disturb the\nquiet up here...\pIs it coincidence that you are here...\pWill you hear out my tale? A tale long\ntold in the HOENN region?$"
R['MtPyre_Summit_Text_1B64B3'] = pyre
R['UnknownString_81B586F'] = pyre
R['MtPyre_Summit_Text_1B65D6'] = r"It happened long, long ago, when this\nworld was first being written...\pTwo ancient DIGIMON fought over its\ncode, one of land and one of sea.\pThe DIGIMON of the land raised\nmountains and blazed like the sun...\pThe DIGIMON of the sea raised huge\nwaves and carved out oceans...\pTheir duel raged without end, and the\nworld's data began to break apart.\pThe RED ORB and the BLUE ORB were\nmade to seal that broken code.\pLight poured from the two ORBS and\nbecalmed the enraged adversaries.\pThe pair, sealed away, burrowed deep\nunder the ground where eventually\lthey disappeared...$"
R['UnknownString_81B5992'] = r"It happened long, long ago, when this\nworld was first being written...\pTwo ancient DIGIMON fought over its\ncode, one of sea and one of land.\pThe DIGIMON of the sea raised huge\nwaves and carved out oceans...\pThe DIGIMON of the land raised\nmountains and blazed like the sun...\pTheir duel raged without end, and the\nworld's data began to break apart.\pThe BLUE ORB and the RED ORB were\nmade to seal that broken code.\pLight poured from the two ORBS and\nbecalmed the enraged adversaries.\pThe pair, sealed away, dove deep into\nthe sea where eventually they\ldisappeared...$"
R['MtPyre_Summit_Text_1B6848'] = r"MAXIE: You...\nSo you stopped SHINEGRMON...\pI shouldn't be surprised...\pThat voice in the glitch... It never\nwanted a new world for us.\pIt wanted HOENN broken, so that\nsomething darker could rebuild itself.\pHumans cannot freely control the\nbalance between land and sea...\pSo I have come to return the\nBLUE ORB...\pBeware the DARK MASTERS, child...\nFarewell...$"
R['UnknownString_81B5BFC'] = r"ARCHIE: You...\nSo you stopped LEVIAMON...\pI shouldn't be surprised...\pThat voice in the glitch... It never\nwanted a new world for us.\pIt wanted HOENN broken, so that\nsomething darker could rebuild itself.\pHumans cannot freely control the\nbalance between land and sea...\pSo I have come to return the\nRED ORB...\pBeware the DARK MASTERS, child...\nFarewell...$"
R['Route128_Text_17210B'] = r"{GOOD_LEADER}: This defies belief...\pAn ancient MEGA DIGIMON, torn out\nof its seal in the world's code...\pIts power is unbelievable.\nIt is breaking HOENN apart...$"

def body(text):
    parts = re.split(r'(?<=\\[npl])', text)
    return ''.join(f'\t.string "{x}"\n' for x in parts if x)
done = set()
for p in list((root/'data').rglob('*.inc')) + list((root/'data').glob('*.s')):
    t = p.read_text(encoding='utf-8', errors='surrogateescape'); nt = t
    for lab, txt in R.items():
        m = re.search(r'^(' + re.escape(lab) + r':+[^\n]*\n)((?:[ \t]*\.string[^\n]*\n)+)', nt, re.M)
        if m:
            nt = nt[:m.start(2)] + body(txt) + nt[m.end(2):]; done.add(lab)
    if nt != t: p.write_text(nt, encoding='utf-8', errors='surrogateescape')
missing = set(R) - done
print('rewrote', len(done), 'missing', sorted(missing))
