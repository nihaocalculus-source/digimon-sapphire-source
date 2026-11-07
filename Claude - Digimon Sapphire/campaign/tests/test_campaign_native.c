#include <assert.h>
#include <stdio.h>
#include "digimon_campaign.h"
#include "digimon_rewards.h"
#include "constants/battle.h"
#include "reward_test_support.h"
static void setup(unsigned keys, unsigned masters, unsigned rewards, unsigned reunited) {
 unsigned i;memset(flags,0,sizeof(flags));
 for(i=0;i<8;i++)if(keys&(1u<<i))FlagSet(FLAG_BADGE01_GET+i);
 for(i=0;i<8;i++)if(rewards){FlagSet(FLAG_DIGIMON_CREST_FIRST+i);FlagSet(FLAG_DIGIMON_REWARD_FIRST+i);}
 if(masters&1)FlagSet(FLAG_DEFEATED_ELITE_4_SYDNEY);
 if(masters&2)FlagSet(FLAG_DEFEATED_ELITE_4_PHOEBE);
 if(masters&4)FlagSet(FLAG_DEFEATED_ELITE_4_GLACIA);
 if(masters&8)FlagSet(FLAG_DEFEATED_ELITE_4_DRAKE);
 if(reunited)FlagSet(FLAG_DIGIMON_REUNITED);
}
int main(void) {
 unsigned keys,masters,outcome,complete,rewards,reunited,cases=0;
 for(keys=0;keys<256;keys++) {
  unsigned i,count=0;for(i=0;i<8;i++)count+=(keys>>i)&1;
  setup(keys,0,0,0);
  assert(Digimon_CountDigitalKeys()==count);
  assert(Digimon_HomeGateUnlocked()==(keys==255));
  for(masters=0;masters<16;masters++)for(outcome=1;outcome<=4;outcome++)for(complete=0;complete<2;complete++)
  for(rewards=0;rewards<2;rewards++)for(reunited=0;reunited<2;reunited++) {
   unsigned expected=keys==255 && masters==15 && outcome==B_OUTCOME_WON && !complete && rewards && reunited;
   setup(keys,masters,rewards,reunited);gBattleOutcome=outcome;
   if(complete)FlagSet(FLAG_DIGIMON_RETURNED_HOME);
   assert(!Digimon_CanEnterFinale());
   assert(Digimon_TryArmFinale()==expected);
   assert(FlagGet(FLAG_DIGIMON_FINALE_ARMED)==expected);
   assert(Digimon_CanEnterFinale()==expected);cases++;
  }
 }
 setup(255,15,1,1);gBattleOutcome=B_OUTCOME_WON;
 assert(Digimon_TryArmFinale());
 FlagSet(FLAG_DIGIMON_FUSION_SEEN);flags[FLAG_DIGIMON_FINALE_ARMED]=0;
 assert(Digimon_CanEnterFinale());
 FlagSet(FLAG_DIGIMON_RETURNED_HOME);assert(!Digimon_TryArmFinale());
 setup(255,14,1,1);FlagSet(FLAG_DIGIMON_FUSION_SEEN);assert(!Digimon_CanEnterFinale());
 printf("PASS: %u actual native finale cases, key masks, rewards, reunion, victory/defeat and resume guards.\n",cases);
 return 0;
}
