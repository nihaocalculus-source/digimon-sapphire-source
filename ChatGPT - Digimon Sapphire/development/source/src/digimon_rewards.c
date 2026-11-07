#include "global.h"
#include "digimon_rewards.h"
#include "contest_util.h"
#include "event_data.h"
#include "string_util.h"
#include "constants/flags.h"
extern u8 gStringVar1[], gStringVar2[], gStringVar3[];
struct DigimonReward { u16 species; u8 level; u8 partner[12], crest[12], tamer[8]; };
static const struct DigimonReward sRewards[8] = {
#if defined(RUBY)
    {16, 14, _("BIYOMON"), _("LOVE"), _("SORA")},
    {13, 20, _("TENTOMON"), _("KNOWLEDGE"), _("IZZY")},
    {1, 24, _("PALMON"), _("SINCERITY"), _("MIMI")},
    {7, 28, _("GOMAMON"), _("RELIABILITY"), _("JOE")},
    {277, 32, _("PATAMON"), _("HOPE"), _("T.K.")},
    {108, 36, _("GATOMON"), _("LIGHT"), _("KARI")},
    {283, 40, _("GABUMON"), _("FRIENDSHIP"), _("MATT")},
    {0, 0, _("AGUMON"), _("COURAGE"), _("TAI")},
#else
    {7, 14, _("GOMAMON"), _("RELIABILITY"), _("JOE")},
    {277, 20, _("PATAMON"), _("HOPE"), _("T.K.")},
    {13, 24, _("TENTOMON"), _("KNOWLEDGE"), _("IZZY")},
    {16, 28, _("BIYOMON"), _("LOVE"), _("SORA")},
    {1, 32, _("PALMON"), _("SINCERITY"), _("MIMI")},
    {108, 36, _("GATOMON"), _("LIGHT"), _("KARI")},
    {280, 40, _("AGUMON"), _("COURAGE"), _("TAI")},
    {0, 0, _("GABUMON"), _("FRIENDSHIP"), _("MATT")},
#endif
};
u16 Digimon_CountCrests(void)
{
    u8 i, count = 0;
    for (i = 0; i < 8; i++)
        if (FlagGet(FLAG_BADGE01_GET + i) && FlagGet(FLAG_DIGIMON_CREST_FIRST + i)) count++;
    return count;
}
u16 Digimon_RewardsComplete(void)
{
    u8 i;
    for (i = 0; i < 8; i++)
        if (!FlagGet(FLAG_BADGE01_GET + i) || !FlagGet(FLAG_DIGIMON_CREST_FIRST + i)
            || !FlagGet(FLAG_DIGIMON_REWARD_FIRST + i)) return FALSE;
    return TRUE;
}
/* Called after a victory and on revisits. A full party goes to the PC;
 * full storage leaves the reward pending. Existing saves catch up here. */
u16 Digimon_ClaimNextReward(void)
{
    u8 i, result;
    for (i = 0; i < 8; i++)
        if (FlagGet(FLAG_BADGE01_GET + i)) FlagSet(FLAG_DIGIMON_CREST_FIRST + i);
    for (i = 0; i < 8; i++)
    {
        const struct DigimonReward *reward = &sRewards[i];
        if (!FlagGet(FLAG_BADGE01_GET + i) || FlagGet(FLAG_DIGIMON_REWARD_FIRST + i)) continue;
        StringCopy(gStringVar1, reward->partner);
        StringCopy(gStringVar2, reward->crest);
        StringCopy(gStringVar3, reward->tamer);
        result = reward->species ? ScriptGiveMon(reward->species, reward->level, 0, 0, 0, 0) : 3;
        if (result == 2) return 3;
        FlagSet(FLAG_DIGIMON_REWARD_FIRST + i);
        return result == 3 ? 4 : result + 1;
    }
    return 0;
}
