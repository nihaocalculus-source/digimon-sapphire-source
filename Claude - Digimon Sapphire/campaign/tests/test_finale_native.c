#include <assert.h>
#include <stdio.h>
#include "global.h"
#include "pokemon.h"
#include "digimon_finale.h"
#include "constants/flags.h"
#include "constants/battle.h"
#include "constants/species.h"
struct Pokemon gPlayerParty[6];u8 gPlayerPartyCount,gBattleOutcome;
static struct Pokemon before[6];static u8 ready,flags[65536];
u16 Digimon_CanEnterFinale(void){return ready;}
u8 FlagSet(u16 f){flags[f]=1;return 0;}
void CreateMon(struct Pokemon *p,u16 s,u8 l,u8 iv,u8 hp,u32 per,u8 ot,u32 id)
{(void)iv;(void)hp;(void)per;(void)ot;(void)id;memset(p,0,sizeof(*p));p->species=s;p->level=l;}
void SetMonMoveSlot(struct Pokemon *p,u16 move,u8 slot){memcpy(p->state+slot*2,&move,2);}
void SetMonData(struct Pokemon *p,int field,const void *v){if(field==21)p->state[8]=*(const u8*)v;else if(field>=17&&field<=20)p->state[9+field-17]=*(const u8*)v;}
u8 CalculatePPWithBonus(u16 move,u8 b,u8 i){(void)move;return (u8)(5+((b>>(2*i))&3)*1);}
int main(void){unsigned i,outcome;
 for(outcome=1;outcome<=4;outcome++){
  for(i=0;i<sizeof(gPlayerParty);i++)((u8 *)gPlayerParty)[i]=(u8)(i*37+outcome);
  memcpy(before,gPlayerParty,sizeof(before));gPlayerPartyCount=6;ready=0;memset(flags,0,sizeof(flags));
  assert(!Digimon_PrepareFinalBattle());assert(!memcmp(before,gPlayerParty,sizeof(before)));
  ready=1;assert(Digimon_PrepareFinalBattle());assert(!Digimon_PrepareFinalBattle());
  assert(gPlayerParty[0].species==SPECIES_RAYQUAZA);assert(gPlayerParty[0].level==100);assert(gPlayerParty[0].state[8]==0xFF);for(i=0;i<4;i++)assert(gPlayerParty[0].state[9+i]==8);
  assert(!memcmp(before+1,gPlayerParty+1,sizeof(before)-sizeof(before[0])));
  memset(gPlayerParty,0,sizeof(gPlayerParty));gPlayerPartyCount=1;gBattleOutcome=outcome;
  Digimon_RestoreFinalBattleParty();assert(gPlayerPartyCount==6);assert(!memcmp(before,gPlayerParty,sizeof(before)));
  assert(flags[FLAG_DIGIMON_FINAL_BATTLE_WON]==(outcome==B_OUTCOME_WON));
  assert(flags[FLAG_DIGIMON_FUSION_SEEN]==(outcome==B_OUTCOME_WON));
  Digimon_RestoreFinalBattleParty();assert(!memcmp(before,gPlayerParty,sizeof(before)));
 }
 puts("PASS: actual native fusion setup, all-party restoration, repeat guards, victory-only ending.");return 0;
}
