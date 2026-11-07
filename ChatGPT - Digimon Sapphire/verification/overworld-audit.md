# Digimon Sihappiere field-art conversion audit

Converted 63 indexed PNG sheets containing 100 frames. These cover all 15 files in the original `graphics/object_events/pics/pokemon` directory, all 41 doll sheets, the Pikachu- and Zigzagoon-shaped cushions, and five new sheets separating the formerly shared Latias/Latios and Regirock/Regice/Registeel graphics.

The replacement identities come from `roster.json`. Each frame is a scaled Digimon portrait from the supplied sprite collection, with GIF animation frames used where space allows. These are not bespoke four-direction walking or rear-view sprites. The house-moving character retains a small shipping parcel drawn over its portrait.

The existing 16-color field palettes, transparency index 0, frame dimensions, frame counts, and event movement rules are preserved. Dedicated picture tables now distinguish the five formerly palette-swapped species. No shared NPC palettes are changed. Some field colors therefore differ from the full-color source portraits.

Validation: the bundled `gbagfx` compiler accepted all 63 sheets. A separate pixel-to-tile encoder matched every output byte across all 100 frames (29,312 bytes). Each image uses at most 16 palette indices. This validates the asset encoding, not a full campaign playthrough.

The generic Pokémon/Digimon dialogue rebrand already covers English text in maps and ordinary strings. Hardcoded species names are handled separately by the parent conversion pipeline. Code identifiers such as `SPECIES_POOCHYENA`, map event labels, and graphic constants intentionally retain their original identifiers to preserve script references.

Remaining graphical Pokémon references outside this field-art task include Game Corner artwork in `graphics/roulette` (`azurill.png`, `makuhita.png`, `shroomish.png`, `skitty.png`, `tailow.png`, `wynaut.png`, `poke_icons.png`, and wheel/header graphics) and `graphics/slot_machine` (`reel_pikachu.png`, `pika_aura.png`, selected reel symbols, and potentially combined tiles). Intro/title graphics are handled by the title worker. Poké Ball imagery and capture mechanics, map tiles, trainers, music, and other original campaign assets remain part of the base game unless another conversion step changes them.

Reproduction: run `overworld_convert.py` after generating the final roster. The script writes the PNGs, five graphic declarations, five picture tables, matching object descriptors, and frame-size build rules. A normal source build recompiles the PNGs through `gbagfx`.
