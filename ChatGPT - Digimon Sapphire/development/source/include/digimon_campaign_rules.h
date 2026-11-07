#ifndef GUARD_DIGIMON_CAMPAIGN_RULES_H
#define GUARD_DIGIMON_CAMPAIGN_RULES_H
/* Pure rules shared by the ROM and host unit tests. Masks are limited to
 * the eight Digital Keys and four Dark Masters, not unrelated flags. */
static unsigned char DigimonKeyCount(unsigned int keys)
{
    unsigned char count = 0;
    keys &= 0xFF;
    while (keys) { count += keys & 1; keys >>= 1; }
    return count;
}
static unsigned char DigimonGateUnlocked(unsigned int keys)
{
    return DigimonKeyCount(keys) == 8;
}
static unsigned char DigimonShouldBeginFusion(unsigned int keys, unsigned int masters,
    unsigned char wonLastBattle, unsigned char alreadyCompleted)
{
    return DigimonGateUnlocked(keys) && (masters & 15) == 15
        && wonLastBattle && !alreadyCompleted;
}
#endif
