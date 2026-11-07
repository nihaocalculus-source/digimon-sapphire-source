# Editing and rebuilding

The games are local fan conversions built from `development/source`. The source now implements the Tai/Matt campaign overhaul. `campaign` contains both native C tests and a separate JavaScript design prototype.

## GBA source

`Build Games.command` rebuilds both editions, copies the results into `roms`, and changes the player's asset-version URL so the emulator does not reuse an older cached cartridge. Run it after edits to source, graphics or scripts. The agbcc and asset tools are included as existing Mac binaries. This Mac also needs the installed `arm-none-eabi` binutils on its PATH. See `development/source/INSTALL.md` for the source project's full toolchain instructions; different operating systems must rebuild the host tools.

Keep the ROM header game codes `AXPE` and `AXVE`: the emulator uses these to recognize the original FLASH1M save hardware. Project and edition saves are separated by browser origin, game names and emulator IDs, not those header codes. The Digimon title names remain in the ROM header.

`development/source` is the complete editable source and includes the converted graphics. `make` recreates build products when needed. The native overhaul replaces protagonist graphics and starter selection, adds fixed followers, reframes the opening and Gym rewards, replaces Elite Four teams and dialogue with the Dark Masters, and scripts the Omegamon reunion and return-home credits. Existing Hoenn layouts, music, most encounters, species stats, move rules and evolution triggers remain the framework. The 386 slots map to distinct Digimon; original species identifiers remain in source so scripts keep valid references. `ROSTER.csv` maps slots to full and abbreviated names.

The main native entry points are `src/digimon_campaign.c`, `src/digimon_follower.c`, `src/digimon_trail.c`, and the Ever Grande map scripts under `data/maps`. The finale uses existing badge/Elite Four flags and three reserved campaign flags; it does not enlarge the saved Pokémon structure. Follower assets and actor metadata are recorded in `campaign/digimon.json`; generated hero atlases are in `development/campaign_assets`.

## Recreating conversion assets

Normal source rebuilds use the graphics already included and do not require asset regeneration. The older `development` import scripts use Python plus Pillow and are listed below for maintenance. They regenerate the base conversion and can overwrite later campaign artwork or dialogue. Preserve the campaign changes before using them; do not run this list as a routine build step. The source GIF archive, title art, title font, original text baselines and roster are included. From `development`:

```sh
python3 convert_roster.py
python3 text_rebrand.py
python3 replace_species_dialogue.py
python3 title_brand.py
python3 overworld_convert.py
```

Then run `Build Games.command` from the project root. Regeneration intentionally overwrites generated names, descriptions and creature images; make artistic edits in the conversion scripts or preserve manual edits first. The browser player needs no Python imaging packages, internet connection, Node or GBA development toolchain; only rebuilding assets does.

After a source build, `python3 development/verify_roms.py` checks cartridge headers and compares names, species pointers and compiled graphics against the linked ROMs. Verification reports are kept in `verification/`.

Run `Test Campaign.command` from the project root for all campaign tests. The native campaign test exercises the actual C helper against 32,768 combinations of keys, defeated masters, battle outcomes and completion state. The follower test checks exact trailing positions, including 500 generated movements. The 23 JavaScript tests cover the separate state and route prototype. The runner needs a C compiler and Node.js; playing the game does not.

## Known boundaries

Battle rear views and follower frames adapt/mirror portraits. Specialized Tai/Matt movement states reuse directional poses. Source palettes constrain some field colors; certain minigame art, ball imagery and optional dialogue remain from the base games. A complete campaign playthrough, long-term save durability and link play have not been verified.

Native endgame fusion is a forced cinematic after the four Dark Masters and all eight Digital Keys; saved party members remain intact. The JSON prototype's shared dual-journey save, Sun/Tide map blueprints, recruitment rewards, proposed stats and controllable temporary battle fusion still need native adapters. There is no cross-ROM save bridge. `campaign/README.md` distinguishes these systems from the implemented native campaign.

## Native protagonist artwork

`python3 development/compile_avatars.py` compiles the included transparent Tai/Matt atlases into indexed GBA movement and trainer sheets using Pillow. Run `Build Games.command` afterward. This compiler updates only the two actors’ generated graphics and palettes. Native event and follower source files remain editable independently.
