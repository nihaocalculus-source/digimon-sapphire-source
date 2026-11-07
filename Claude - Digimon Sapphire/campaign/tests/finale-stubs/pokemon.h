#include "global.h"
#define PARTY_SIZE 6
struct Pokemon { u16 species; u8 level; u8 state[97]; };
extern struct Pokemon gPlayerParty[6];
extern u8 gPlayerPartyCount;
void CreateMon(struct Pokemon*,u16,u8,u8,u8,u32,u8,u32);
void SetMonMoveSlot(struct Pokemon*,u16,u8);
void SetMonData(struct Pokemon*,int,const void*);
u8 CalculatePPWithBonus(u16,u8,u8);
