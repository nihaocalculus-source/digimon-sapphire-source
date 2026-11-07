#include "global.h"
#include "digimon_campaign.h"
#include "digimon_rewards.h"
#include "digimon_campaign_rules.h"
#include "event_data.h"
#include "constants/flags.h"
#include "constants/battle.h"
extern u8 gBattleOutcome;
static u16 DigitalKeyMask(void)
{
    u16 keys = 0;
    u8 i;
    for (i = 0; i < 8; i++)
        if (FlagGet(FLAG_BADGE01_GET + i)) keys |= 1 << i;
    return keys;
}
static u8 DarkMasterMask(void)
{
    u8 mask = 0;
    if (FlagGet(FLAG_DEFEATED_ELITE_4_SYDNEY)) mask |= 1;
    if (FlagGet(FLAG_DEFEATED_ELITE_4_PHOEBE)) mask |= 2;
    if (FlagGet(FLAG_DEFEATED_ELITE_4_GLACIA)) mask |= 4;
    if (FlagGet(FLAG_DEFEATED_ELITE_4_DRAKE)) mask |= 8;
    return mask;
}
u16 Digimon_CountDigitalKeys(void) { return DigimonKeyCount(DigitalKeyMask()); }
u16 Digimon_HomeGateUnlocked(void) { return DigimonGateUnlocked(DigitalKeyMask()); }
u16 Digimon_ReunionReady(void)
{
    return Digimon_HomeGateUnlocked() && Digimon_RewardsComplete();
}
u16 Digimon_TryArmFinale(void)
{
    if (!Digimon_ReunionReady() || !FlagGet(FLAG_DIGIMON_REUNITED)) return FALSE;
    if (!DigimonShouldBeginFusion(DigitalKeyMask(), DarkMasterMask(),
        gBattleOutcome == B_OUTCOME_WON, FlagGet(FLAG_DIGIMON_RETURNED_HOME)))
        return FALSE;
    FlagSet(FLAG_DIGIMON_FINALE_ARMED);
    return TRUE;
}
u16 Digimon_CanEnterFinale(void)
{
    return Digimon_ReunionReady() && FlagGet(FLAG_DIGIMON_REUNITED) && DarkMasterMask() == 15
        && (FlagGet(FLAG_DIGIMON_FINALE_ARMED) || FlagGet(FLAG_DIGIMON_FUSION_SEEN));
}
