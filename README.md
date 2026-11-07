# Digimon Sapphire — editable source snapshots

Download and experiment with the ChatGPT and Claude versions of Max's Digimon × Ruby/Sapphire fan-game project.

## Download

**[Download the source ZIP](https://github.com/nihaocalculus-source/digimon-sapphire-source/archive/refs/heads/main.zip)**

Or use the green **Code → Download ZIP** button on this page. No GitHub account is needed to download this public repository.

## What is included

- `ChatGPT - Digimon Sapphire/`: editable native game source, campaign logic/tests, converted graphics, art, conversion tools, browser player and project documentation.
- `Claude - Digimon Sapphire/`: the available comparison version, asset/conversion tools and campaign material.
- The Ollama comparison folder on the original computer was empty; no Ollama build is claimed here.

**This download contains source and assets, not ready-to-play `.gba` cartridges.** Existing project notes may describe local compiled games or installed tools; those outputs and installations are not part of this download. Browser player pages will need the expected game files after a source build.

## Start editing

1. Extract the ZIP, or `git clone` this repository.
2. Read [the ChatGPT project's editing guide](ChatGPT%20-%20Digimon%20Sapphire/DEVELOPMENT.md).
3. The editable GBA project is [development/source](ChatGPT%20-%20Digimon%20Sapphire/development/source). Build-tool instructions are in its [INSTALL.md](ChatGPT%20-%20Digimon%20Sapphire/development/source/INSTALL.md).
4. On a configured Mac, create the output directory with `mkdir -p roms` from the edition's folder before using its `Build Games.command`. Other operating systems need the platform's toolchain and equivalent build commands. Review scripts before running them.
5. Build and test your changes in your own copy. A full new campaign playthrough was not performed for this source publication.

## Credits and scope

The source foundation is [pret/pokeruby](https://github.com/pret/pokeruby). Existing game, sprite, font and EmulatorJS credits/notices are retained in the included project documentation. This is an unofficial fan project.

`SOURCE-SHA256SUMS.txt` records the hashes of the downloadable source files (Git-normalized text line endings). Passwords, API credentials, login data, personal vault files, ROMs and save files are not included.

Source snapshot published November 6, 2026. You can download, inspect and experiment with the available files; this page does not promise a completed or bug-free game.
