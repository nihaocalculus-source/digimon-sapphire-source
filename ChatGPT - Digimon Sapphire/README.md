# Digimon Sapphire

A separate, local Digimon fan conversion of the Ruby and Sapphire GBA adventures.

## Play

1. Double-click **Launch Digimon Sapphire.command**.
2. Keep its Terminal window open while playing.
3. Choose **Digimon Sapphire** or **Digimon Ruby**, then select **ENTER THE GAME** in the player.

The launcher opens **http://127.0.0.1:8744/**. It uses the Python 3 installation on this Mac. If the server is already running, launching it again opens the existing arcade. To stop it, press **Control+C** in its Terminal window.

All emulator files, fonts, and artwork used by the arcade are included. Internet access is not needed for play. Keep this folder together when moving it.

## What this conversion changes

The cartridges are rebuilt from the GBA game source, with Digimon replacing the 386-species roster: names, battle portraits, party icons, and encyclopedia descriptions. The starter families use condensed, three-stage Digimon paths. Other evolution paths and combat roles follow the original game's structure; this is a custom crossover, rather than a recreation of the official Digimon games.

The native campaign casts Tai with Agumon in Digimon Ruby and Matt with Gabumon in Digimon Sapphire. Each partner follows its hero through the overworld, independently of party order. Hoenn becomes a digital-physical glitch world: eight Gym Badges are Digital Keys to the gate home. The Dark Masters replace the Elite Four, and defeating all four with all eight keys triggers a reunion, an Omegamon DNA-Digivolution cinematic, and return-home credits.

Hoenn's existing map layouts, music, progression and battle system provide the framework. The main opening, key rewards and finale have new dialogue; some optional conversations and side quests retain their original story. Names may be shortened to fit GBA text limits. This is an unofficial fan conversion.

Battle back views use mirrored front portraits. Tai and Matt have new directional avatars; specialized movement states reuse those poses, and followers adapt the catalog's creature portraits. The original slot's types, stats, moves, height, and weight are retained and should not be read as official Digimon lore. For example, the starters inherit Grass for Patamon, Fire for Agumon, and Water for Gabumon. Some minigame and other secondary graphics still use the original game artwork.

The game has not been tested through a complete campaign playthrough. See any build and verification files included with this package for the checks actually performed.

## Controls

Click inside the game before using the keyboard.

| Action | Key |
| --- | --- |
| Move | Arrow keys |
| A / Confirm | Z |
| B / Back | X |
| Start / Menu | Enter |
| Select | Shift |
| L / R | A / S |
| Quick save / Quick load | 1 / 2 |
| Next save-state slot | 3 |
| Fast forward | F |

The emulator toolbar provides control remapping, gamepad configuration, save import/export, save states, volume, and fullscreen.

## Protect your progress

- Start a **new game** for the Tai/Matt campaign so the fixed hero, starter and opening events initialize correctly. Export existing progress first. Older conversion saves and original Pokémon saves may retain incompatible names or story flags.
- Use the game's **SAVE** menu and wait for saving to finish before closing it.
- Export a save file or save-state snapshot through the emulator toolbar for a backup outside the browser.
- Continue using the same browser and address, **127.0.0.1:8744**. Switching to `localhost`, changing the port, using another browser, or clearing browser site data can make existing saves unavailable.
- Each edition has its own game identity. This project also uses a separate browser origin from Sapphire Wednesday on port 8743.
- Loading an older state replaces the current session. Export progress before loading a state you are unsure about.

## Troubleshooting

**The page says “Launcher needed.”** Open the `.command` launcher instead of opening `index.html` directly.

**A cartridge says “Game file not installed.”** The `roms` folder must contain `digimon-sihappiere.gba` and `digimon-ruby.gba`. Keep them in the same project folder as the launcher and reload the page after restoring them.

**The launcher says port 8744 is busy.** Close the other application using that port, then launch again. The launcher does not stop other programs.

**Keys do nothing.** Click inside the player first. Press Enter for the game's Start button, and Z to confirm.

**The game will not load.** Close the player and reopen it, then try restarting the launcher. Use a current browser with WebAssembly support.

## Files and credits

- `roms/`: the converted GBA cartridges.
- `index.html`, `style.css`, `app.mjs`: the Digital Gate arcade.
- `player.html`: the bundled GBA player configuration.
- `server.py`: the local, loopback-only server.
- `emulator/`: [EmulatorJS](https://github.com/EmulatorJS/EmulatorJS), version 4.2.3, using the mGBA core. The included license is in `emulator/LICENSE`.
- `assets/`: arcade artwork and fonts. VT323 and IBM Plex Mono include their respective OFL license files.
- Game source foundation: [pret/pokeruby](https://github.com/pret/pokeruby).
- Digimon sprite archive: [E-M-B-E-R/digimon-world-ds-dawn-dusk-animated-sprites](https://github.com/E-M-B-E-R/digimon-world-ds-dawn-dusk-animated-sprites), preserving sprites credited to AngelofHope and the With the Will community. The sprites originate from Digimon World DS, Dawn, and Dusk.

Pokémon game assets and Digimon characters/art remain the property of their respective rights holders. This local project does not claim ownership of those materials.

## Campaign source and tests

The native character, follower, Digital Key and finale logic lives in `development/source`. Run **Test Campaign.command** for the native condition and follower tests plus the standalone campaign tests. Build and verification reports describe the checks actually run.

[campaign/README.md](campaign/README.md) also documents the separate JSON design prototype: 33 forms, independent journey records, eight-family recruitment rewards, Sun/Tide route blueprints, and temporary battle fusion. Those prototype systems still need native adapters. The cartridges have separate saves; their reunion is scripted within each edition, with no cross-cartridge save bridge. The native Omegamon finale is a cinematic and does not replace or consume saved party members.

Editable GBA source and the asset compilation scripts are in `development/`. See `DEVELOPMENT.md` for rebuild instructions. Verification reports are in `verification/`.
