#include "global.h"
#include "digimon_finale.h"
#include "digimon_campaign.h"
#include "pokemon.h"
#include "event_data.h"
#include "constants/flags.h"
#include "constants/species.h"
#include "constants/moves.h"
#include "constants/battle.h"
extern u8 gBattleOutcome;
static EWRAM_DATA struct Pokemon sOriginalParty[PARTY_SIZE] = {0};
static EWRAM_DATA u8 sOriginalCount = 0;
static EWRAM_DATA bool8 sFusionActive = FALSE;
/* The final encounter is a temporary fusion. Preserve every recruited
 * partner, its moves, held item and health; restore on victory AND defeat. */
u16 Digimon_PrepareFinalBattle(void)
{
    if (sFusionActive || !Digimon_CanEnterFinale()) return FALSE;
    memcpy(sOriginalParty, gPlayerParty, sizeof(sOriginalParty));
    sOriginalCount = gPlayerPartyCount;
    sFusionActive = TRUE;
    CreateMon(&gPlayerParty[0], SPECIES_RAYQUAZA, 75, 31, 0, 0, 0, 0);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_SACRED_FIRE, 0);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_ICE_BEAM, 1);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_AEROBLAST, 2);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_EXTREME_SPEED, 3);
    if (!gPlayerPartyCount) gPlayerPartyCount = 1;
    return TRUE;
}
void Digimon_RestoreFinalBattleParty(void)
{
    if (!sFusionActive) return;
    memcpy(gPlayerParty, sOriginalParty, sizeof(sOriginalParty));
    gPlayerPartyCount = sOriginalCount;
    sFusionActive = FALSE;
    if (gBattleOutcome == B_OUTCOME_WON)
    {
        FlagSet(FLAG_DIGIMON_FUSION_SEEN);
        FlagSet(FLAG_DIGIMON_FINAL_BATTLE_WON);
    }
}
