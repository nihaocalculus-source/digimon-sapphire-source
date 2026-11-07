#include "global.h"
#include "constants/flags.h"
static u8 flags[65536];
u8 gStringVar1[64], gStringVar2[64], gStringVar3[64];
u8 gBattleOutcome;
static u8 storageResult, calls, lastLevel;
static u16 lastSpecies;
u8 FlagGet(u16 f) { return flags[f]; }
u8 FlagSet(u16 f) { flags[f] = 1; return 0; }
u8 *StringCopy(u8 *d,const u8 *s) { return (u8 *)strcpy((char *)d,(const char *)s); }
u8 ScriptGiveMon(u16 species,u8 level,u16 item,u32 a,u32 b,u8 c)
{ (void)item;(void)a;(void)b;(void)c; calls++;lastSpecies=species;lastLevel=level;return storageResult; }
