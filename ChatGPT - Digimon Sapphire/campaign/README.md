# Tai & Matt: native campaign and design prototype

The GBA source now implements Tai/Agumon for Ruby and Matt/Gabumon for Sapphire, fixed overworld followers, the Digital Keys narrative, Dark Master encounters, and the forced Omegamon reunion and return-home credits. `digimon.json` records the actor and follower asset mappings used by this conversion.

The native Home Gate requires all eight badge flags. Winning the fourth Dark Master encounter with all four defeated flags arms the finale. The reunion shows WarGreymon and MetalGarurumon combining into Omegamon, then returns the heroes home through the credits sequence. Campaign flags allow the scene to resume without duplicating its fusion sequence. This cinematic leaves party records intact and runs within each edition's independent save.

The remaining sections describe the **standalone JavaScript prototype**, not additional cartridge features: 33 form definitions, two coordinated journey records, recruitment rewards, Sun/Tide route blueprints, and temporary battle fusion. Those systems have no native save/map/battle adapters yet; the two cartridges do not read each other's progress.

## Data model

| Record | Owns | Why separate |
| --- | --- | --- |
| `FormDefinition` | Stable form ID; display name; stage; attribute; elements; six base stats; growth; learnset; ability IDs; digivolution edges; current ROM slot | Shared immutable design data, never a saved individual |
| `PartnerInstance` | Unique instance ID; family/form IDs; owner; origin; level/XP; IVs/EVs; nature; bond; moves; current HP/status/item | Two Agumon can share a form without sharing progress |
| `JourneyState` | Tai or Matt; revision; map/position; badges/flags; party; storage; inventory; money; original starter ID | Progress remains independent before and after reunion |
| `CampaignSave` | Schema version; stable campaign ID; revision; active journey; both journey records; shared reunion flag | One consistent envelope for coordinating the two journeys |
| `BattleSession` | Save revision; active battle ID; fusion use flag; temporary merged partner; locked source IDs | Fusion never changes the saved source partners |

`digimon.json` contains the first eight Adventure partner families and their four main forms, plus Omegamon. Familiar English labels are used where appropriate: Salamon/Plotmon, Gatomon/Tailmon, MagnaAngemon/HolyAngemon, and Omnimon/Omegamon. Branches and numeric stats are proposed fan-game balance, not an official canonical stats database. Move and ability lists are intentionally empty pending combat design; these definitions cannot yet power a complete battle.

Stats are `hp`, `attack`, `defense`, `spAttack`, `spDefense`, and `speed`, each base 1–255. Individual level is 1–100, IVs 0–31, EVs 0–252 per stat and 510 total. Nature modifies a non-HP stat by 10%. Bond is 0–100. `attribute` (Vaccine/Data/Virus) and `elements` are separate design concepts. They are **not automatically mapped to the current GBA type chart**.

The existing cartridge species indices are exposed as `gbaSlot` and its 10-character name as `gbaName`. Stable string IDs are the campaign's identity. Never serialize a display name as a key. Never expand `POKEMON_NAME_LENGTH`, or insert these fields directly into the original `struct Pokemon`: doing so changes its encrypted save representation.

## Independent progress and convergence

In the prototype, Tai begins with Agumon on the Sun route. Matt begins with Gabumon on the Tide route. Their inventory, money, flags and roster have separate ownership. Switching the active journey must save the current map/battle transition before loading the other one. A partner's instance ID includes the campaign, owner and recruitment event; each journey has its own recruited instances.

The prototype stores both journeys in a single versioned JSON envelope, so a host can atomically commit both sides. Writes require an expected revision; stale writes fail rather than discard newer progress. Keep two previous checksummed backups when integrating persistent storage. `serializeSave` and `loadSave` validate the structure; actual disk/browser persistence and crash recovery are still adapter work.

Two independent GBA ROMs cannot directly inspect each other's RAM or save. For this local desktop package, use a host bridge that reads an explicit native campaign export from each cartridge, validates campaign ID/owner/revision, and commits the shared reunion record. The current emulator has **no such bridge yet**. A single-cartridge hardware edition needs a save-sector budget and redundant-bank design before porting both records; do not append new fields to the existing save sectors without that analysis. Link-cable convergence is another possible future adapter.

## Prototype badge rewards

Native Gyms award Digital Keys; the automatic partner recruitment table below is implemented only in `state.mjs`.

| Badge | Tai recruits | Matt recruits |
| --- | --- | --- |
| 1 | Biyomon | Gomamon |
| 2 | Tentomon | Patamon |
| 3 | Palmon | Tentomon |
| 4 | Gomamon | Biyomon |
| 5 | Patamon | Palmon |
| 6 | Gatomon | Gatomon |
| 7 | Gabumon | Agumon |
| 8 | Reunion access | Reunion access |

A boss victory calls `awardBadge(catalog, save, journey, badge, expectedRevision)`. The handler requires sequential progress and is idempotent. Recruitment goes to the party if there is room, otherwise storage. If both are full, the reward remains pending until `claimPendingRewards` succeeds. There are eight classic families, but the GBA party remains six slots: both heroes possess all eight by the Elite Four, with two in storage.

Recruiting the other lead's family grants a distinct partner instance. It never transfers or duplicates the other protagonist's original starter. Only Tai's original Agumon and Matt's original Gabumon qualify for the story's Omegamon fusion.

## Early maps and event contracts

`routes.json` defines eight 24×18 layout blueprints: each home, two early routes, and the first trial. `#` is blocked, `.` a safe path, `g` encounter terrain, and `~` blocked water. Every route has a safe main path; encounters are optional in the adjacent grass.

- **Tai:** home → Sun Route 1 (Palmon 50%, Tentomon 30%, Biyomon 20%, levels 2–5) → Sun Route 2 (levels 4–7, healing camp and a gate trainer) → a level-12 Togemon trial. Winning grants badge 1 and Biyomon.
- **Matt:** home → Tide Route 1 (Gomamon 50%, Patamon 30%, Gabumon 20%, levels 2–5) → Tide Route 2 (levels 4–7, healing camp, gate trainer and shoreline) → a level-12 Ikkakumon trial. Winning grants badge 1 and Gomamon.
- Starter events use `starter_received`; tutorial battles use `tutorial_won`; the second route's trainer sets `trial_gate_open`. These flags belong to the current journey. A map script must check a one-time flag before granting a starter or reopening its event.
- The shared `convergence_gate` requires both eight-badge journeys to have arrived. Calling `reunite` sets the shared flag once. The map grid, collision, warp, encounter and boss metadata must still be compiled into native map/script resources.

## Prototype digivolution and battle fusion

These rules govern temporary battle fusion in `state.mjs`. The native endgame uses the cinematic described above.

Normal paths propose Rookie → Champion at level 16/bond 20, Ultimate at level 32/bond 50, and Mega at level 48/bond 80 plus the family's crest. `digivolve` validates these gates and preserves the current HP ratio, including fainted status.

For the endgame: both heroes reach the gate with eight badges; their original leads are WarGreymon and MetalGarurumon, healthy, level ≥48 and bond ≥80. `startFinalBattle` freezes the save revision. `activateFusion` creates one temporary Omegamon and locks the two source IDs out of other battle commands. It can run once per battle. `endFinalBattle` removes the temporary form on victory, defeat or escape. The source partners stay intact at their pre-fusion HP/status. The future battle adapter must enforce those source locks, reject mid-battle save mutations, and commit post-battle rewards exactly once. Animation, command-menu integration, damage resolution and native save persistence are not implemented here.

## Run the checks

Double-click `Test Campaign.command` to run the native campaign condition tests, follower trail tests and JavaScript prototype suite together. Native conditions are exercised across 32,768 combinations; the trail test includes 500 generated movements. These tests do not substitute for a complete campaign playthrough.

To run only the 23 JavaScript prototype checks from this project folder:

```sh
node --test campaign/test.mjs campaign/test-routes.mjs
```

No third-party JavaScript packages are required. Tests cover stats, ownership isolation, full teams, storage overflow, duplicate rewards, stale writes, reunion gates, temporary fusion, failure paths and save round-trips. The tests simulate engine events; they are not a full campaign playthrough.
