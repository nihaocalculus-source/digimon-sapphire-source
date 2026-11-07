#ifndef GUARD_DIGIMON_TRAIL_H
#define GUARD_DIGIMON_TRAIL_H

/* This movement core deliberately has no engine dependencies, so the exact
 * code used by the cartridge can be checked by the host C unit test. */
#define DIGIMON_TRAIL_DISTANCE 16
#define DIGIMON_TRAIL_POINTS (DIGIMON_TRAIL_DISTANCE + 1)

struct DigimonTrailPoint
{
    short x;
    short y;
    unsigned char direction;
    unsigned char elevation;
};

struct DigimonTrail
{
    struct DigimonTrailPoint points[DIGIMON_TRAIL_POINTS];
    unsigned char head;
    unsigned char distance;
};

void DigimonTrail_Reset(struct DigimonTrail *trail, short x, short y,
    unsigned char direction, unsigned char elevation, int seedBehind);
/* Returns the number of pixels advanced; discontinuous moves reset the trail. */
int DigimonTrail_Record(struct DigimonTrail *trail, short x, short y,
    unsigned char direction, unsigned char elevation);
const struct DigimonTrailPoint *DigimonTrail_GetFollower(const struct DigimonTrail *trail);

#endif
