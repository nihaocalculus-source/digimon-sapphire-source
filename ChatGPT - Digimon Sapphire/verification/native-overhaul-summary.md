# Native campaign overhaul verification

Both delivered 16 MiB cartridges are rebuilt from the included source. SHA256SUMS and native-integration.json identify the final files.

## Implemented in the GBA games

- Ruby fixes the new-game hero to Tai and the starter to Agumon; Sapphire fixes them to Matt and Gabumon. Generated avatar movement/trainer sheets and dedicated palettes are compiled into both editions.
- Each edition uses its assigned catalog follower regardless of party order. The companion trails the player’s recorded path one tile behind, resets across map transitions, and hides for the finale.
- Opening, major progression dialogue and eight Gym rewards present Hoenn as a glitch world and badges as Digital Keys. Optional side dialogue still includes base-game material.
- All four Elite encounters have Dark Master teams, names, battle portraits and dialogue. The fourth victory checks all eight key flags and all four boss flags before forcing reunion.
- WarGreymon and MetalGarurumon combine into Omegamon in a forced cinematic, then the return-home dialogue, saved completion and credits run. Party records remain intact.

## Checks completed

- Both native agbcc builds and ROM installation succeeded.
- 23 JavaScript campaign/route prototype tests passed.
- 32,768 combinations passed against the actual native campaign helper: every key mask, every Dark Master mask, win/loss/flee outcomes, completed and resumable states.
- Native follower tests passed, including 500 generated movements compared against independent path history.
- Both binaries passed checks for 386 species names, 386 front pointers, 2,403 compiled creature graphics arrays, headers and save hardware codes.
- Additional binary checks confirmed edition-specific Tai/Matt graphics, both companion assets, linked native event helpers, EWRAM follower state and installed/source ROM equality.
- Isolated emulator smoke tests: Matt’s opening and reunion, Omegamon presentation, return-home transition, completion save and credits; Tai’s corrected avatar and Agumon following straight movement and a corner. Test entry points accelerated progression in separate QA ROMs outside this Desktop package; production code was restored and verified afterward.

## Scope and limits

No complete campaign playthrough, exhaustive bike/surf/warp visual pass, or long-duration save testing was performed. Start a new game for the revised campaign; pre-overhaul late-game saves have no migration for the new finale flags. Native fusion is a cinematic, not a selectable battle command. The independent dual-save bridge, new Sun/Tide maps and eight-family recruitment prototype remain separate JavaScript design code. Special movement art reuses directional poses; follower and creature back views adapt existing portraits.

Run `Test Campaign.command` to repeat all campaign and follower unit tests. See README.md and DEVELOPMENT.md for play and build instructions.
