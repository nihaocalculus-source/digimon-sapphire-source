#ifndef DIGIMON_CAMPAIGN_CONTRACT_H
#define DIGIMON_CAMPAIGN_CONTRACT_H
/* Proposed native adapter contract. Not included by the current ROM build.
 * Use with pokeruby's global.h. Serialize fields explicitly; never memcpy
 * these structs over existing Pokemon records or save-sector layouts. */
#include "global.h"

enum DigiAttribute { DIGI_DATA, DIGI_VACCINE, DIGI_VIRUS, DIGI_FREE };
enum DigiStage { DIGI_ROOKIE, DIGI_CHAMPION, DIGI_ULTIMATE, DIGI_MEGA, DIGI_ULTRA };
enum DigiJourney { DIGI_TAI, DIGI_MATT };

struct DigiBaseStats {
    u8 hp;
    u8 attack;
    u8 defense;
    u8 spAttack;
    u8 spDefense;
    u8 speed;
};

struct DigiFormDefinition {
    u16 formId;             /* stable generated ID, never a localized name */
    u16 familyId;
    u16 gbaSpeciesSlot;     /* current native species-table bridge */
    struct DigiBaseStats base;
    u8 stage;
    u8 attribute;          /* separate from the native elemental type chart */
    u16 elementMask;
    u8 catchRate;
    u8 expYield;
    u8 growthRate;
};

struct DigiEvolutionRule {
    u16 fromForm;
    u16 toForm;
    u8 minimumLevel;
    u8 minimumBond;
    u16 requiredCrestFlag;
};

/* Extension indexed by stable partner identity, outside struct Pokemon.
 * Native Pokemon fields continue to own level/experience, IVs/EVs, moves,
 * nature, HP, status and held item. A bridge must keep the form ID in sync. */
struct DigiPartnerExtension {
    u32 instanceId;
    u16 familyId;
    u16 formId;
    u8 ownerJourney;
    u8 bond;
    u16 originEventId;
};

/* Temporary RAM state only. Source instances stay in their journey records. */
struct DigiFusionSession {
    u32 battleId;
    u32 sourceInstanceIds[2];
    u32 sourceJourneyRevisions[2];
    u16 resultForm;
    u8 active;
    u8 usedThisBattle;
};
#endif
