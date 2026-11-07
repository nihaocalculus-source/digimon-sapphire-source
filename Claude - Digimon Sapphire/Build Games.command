#!/bin/zsh
set -eu
cd -- "${0:A:h}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
cd development/source
make -j8 sapphire
make -j8 ruby
# Preserve the original hardware codes: mGBA uses them to select FLASH1M saves.
tools/gbafix/gbafix pokesapphire.gba -t"DIGIMON SAPP" -cAXPE --silent
tools/gbafix/gbafix pokeruby.gba -t"DIGIMON RUBY" -cAXVE --silent
cp pokesapphire.gba ../../roms/digimon-sihappiere.gba
cp pokeruby.gba ../../roms/digimon-ruby.gba
cd ../..
/usr/bin/python3 - <<'PY'
from pathlib import Path
import hashlib,re
p=Path('player.html')
tag=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path('roms').glob('*.gba')))).hexdigest()[:12]
p.write_text(re.sub(r'\.gba\?build=[A-Za-z0-9-]+', '.gba?build='+tag, p.read_text()))
print('Rebuilt both Digimon cartridges. Restart the player to load the new build.')
PY
