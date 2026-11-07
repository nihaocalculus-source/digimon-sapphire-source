#include <assert.h>
#include <stdio.h>
#include "digimon_rewards.h"
#include "reward_test_support.h"
int main(void) {
 unsigned i,mask;u8 before;
#if defined(RUBY)
 const u16 expected[7]={16,13,1,7,277,108,283};
#else
 const u16 expected[7]={7,277,13,16,1,108,280};
#endif
 const u8 levels[7]={14,20,24,28,32,36,40};
 assert(!Digimon_ClaimNextReward());assert(!calls);
 for(i=0;i<8;i++) {
  FlagSet(FLAG_BADGE01_GET+i);storageResult=0;
  assert(Digimon_ClaimNextReward()==(i==7?4:1));
  assert(Digimon_CountCrests()==i+1);
  if(i<7){assert(lastSpecies==expected[i]);assert(lastLevel==levels[i]);}
  before=calls;assert(!Digimon_ClaimNextReward());assert(calls==before);
 }
 assert(Digimon_RewardsComplete());assert(calls==7);
 /* Legacy saves with all badges receive every missing gift, once. */
 memset(flags,0,sizeof(flags));calls=0;
 for(i=0;i<8;i++)FlagSet(FLAG_BADGE01_GET+i);
 storageResult=2;assert(Digimon_ClaimNextReward()==3);
 assert(Digimon_CountCrests()==8);assert(!FlagGet(FLAG_DIGIMON_REWARD_FIRST));
 assert(!Digimon_RewardsComplete());
 storageResult=1;assert(Digimon_ClaimNextReward()==2);assert(lastSpecies==expected[0]);
 for(i=1;i<7;i++){assert(Digimon_ClaimNextReward()==2);assert(lastSpecies==expected[i]);}
 assert(Digimon_ClaimNextReward()==4);assert(Digimon_RewardsComplete());
 before=calls;assert(!Digimon_ClaimNextReward());assert(before==calls);
 for(mask=0;mask<256;mask++) {
  unsigned count=0;memset(flags,0,sizeof(flags));storageResult=1;
  for(i=0;i<8;i++)if(mask&(1u<<i)){FlagSet(FLAG_BADGE01_GET+i);count++;}
  while(Digimon_ClaimNextReward());
  assert(Digimon_CountCrests()==count);assert(Digimon_RewardsComplete()==(mask==255));
 }
 puts("PASS: native rewards, both storage destinations, full-PC retry, duplicate prevention and 256 badge migrations.");
 return 0;
}
