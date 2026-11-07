#include "digimon_trail.h"

static void DirectionVector(unsigned char direction, short *x, short *y)
{
    *x = 0;
    *y = 0;
    if (direction == 1)
        *y = 1;
    else if (direction == 2)
        *y = -1;
    else if (direction == 3)
        *x = -1;
    else if (direction == 4)
        *x = 1;
}

void DigimonTrail_Reset(struct DigimonTrail *trail, short x, short y,
    unsigned char direction, unsigned char elevation, int seedBehind)
{
    int i;
    short dx, dy;
    DirectionVector(direction, &dx, &dy);
    if (!seedBehind)
        dx = dy = 0;
    for (i = 0; i < DIGIMON_TRAIL_POINTS; i++)
    {
        trail->points[i].x = x - dx * (DIGIMON_TRAIL_DISTANCE - i);
        trail->points[i].y = y - dy * (DIGIMON_TRAIL_DISTANCE - i);
        trail->points[i].direction = direction;
        trail->points[i].elevation = elevation;
    }
    trail->head = DIGIMON_TRAIL_DISTANCE;
    trail->distance = seedBehind ? DIGIMON_TRAIL_DISTANCE : 0;
}

int DigimonTrail_Record(struct DigimonTrail *trail, short x, short y,
    unsigned char direction, unsigned char elevation)
{
    struct DigimonTrailPoint last = trail->points[trail->head];
    short dx = x - last.x;
    short dy = y - last.y;
    int distance = (dx < 0 ? -dx : dx) + (dy < 0 ? -dy : dy);
    int i;
    short stepX = (dx > 0) - (dx < 0);
    short stepY = (dy > 0) - (dy < 0);

    /* Walking/running/bikes move cardinally. A warp or scripted teleport must
     * never drag the partner through a wall or across the map. */
    if ((dx != 0 && dy != 0) || distance > DIGIMON_TRAIL_DISTANCE)
    {
        DigimonTrail_Reset(trail, x, y, direction, elevation, 0);
        return 0;
    }
    for (i = 0; i < distance; i++)
    {
        last.x += stepX;
        last.y += stepY;
        trail->head = (trail->head + 1) % DIGIMON_TRAIL_POINTS;
        trail->points[trail->head].x = last.x;
        trail->points[trail->head].y = last.y;
        trail->points[trail->head].direction = direction;
        trail->points[trail->head].elevation = elevation;
        if (trail->distance < DIGIMON_TRAIL_DISTANCE)
            trail->distance++;
    }
    return distance;
}

const struct DigimonTrailPoint *DigimonTrail_GetFollower(const struct DigimonTrail *trail)
{
    if (trail->distance < DIGIMON_TRAIL_DISTANCE)
        return 0;
    return &trail->points[(trail->head + 1) % DIGIMON_TRAIL_POINTS];
}
