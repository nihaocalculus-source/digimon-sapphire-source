#include <assert.h>
#include <stdio.h>
#include "digimon_trail.h"

int main(void)
{
    struct DigimonTrail trail;
    const struct DigimonTrailPoint *point;
    int x, y;
    struct DigimonTrailPoint reference[8192];
    int count, step, i, j, direction;

    DigimonTrail_Reset(&trail, 100, 100, 4, 3, 1);
    point = DigimonTrail_GetFollower(&trail);
    assert(point && point->x == 84 && point->y == 100);
    assert(DigimonTrail_Record(&trail, 100, 100, 1, 3) == 0);
    point = DigimonTrail_GetFollower(&trail);
    assert(point->x == 84 && point->direction == 4); /* turning does not orbit */
    for (x = 104; x <= 132; x += 4)
    {
        assert(DigimonTrail_Record(&trail, x, 100, 4, 3) == 4);
        point = DigimonTrail_GetFollower(&trail);
        assert(point->x == x - 16 && point->y == 100);
    }
    for (y = 104; y <= 116; y += 4)
    {
        DigimonTrail_Record(&trail, 132, y, 1, 3);
        point = DigimonTrail_GetFollower(&trail);
        assert(point->x == 116 + y - 100 && point->y == 100);
    }
    DigimonTrail_Record(&trail, 132, 120, 1, 4);
    point = DigimonTrail_GetFollower(&trail);
    assert(point->x == 132 && point->y == 104 && point->direction == 1);
    /* Camera position is not part of trail state; long scrolling cannot wrap it. */
    for (y = 124; y <= 400; y += 4)
    {
        DigimonTrail_Record(&trail, 132, y, 1, 4);
        point = DigimonTrail_GetFollower(&trail);
        assert(point->x == 132 && point->y == y - 16);
    }
    assert(point->elevation == 4);
    /* Warps and diagonal/discontinuous scripts reset instead of cutting corners. */
    DigimonTrail_Record(&trail, 500, 500, 4, 1);
    assert(DigimonTrail_GetFollower(&trail) == NULL);
    for (x = 504; x <= 512; x += 4)
    {
        DigimonTrail_Record(&trail, x, 500, 4, 1);
        assert(DigimonTrail_GetFollower(&trail) == NULL);
    }
    DigimonTrail_Record(&trail, 516, 500, 4, 1);
    point = DigimonTrail_GetFollower(&trail);
    assert(point && point->x == 500 && point->y == 500);
    DigimonTrail_Record(&trail, 520, 504, 4, 1);
    assert(DigimonTrail_GetFollower(&trail) == NULL);
    DigimonTrail_Reset(&trail, -10, -20, 2, 1, 1);
    point = DigimonTrail_GetFollower(&trail);
    assert(point && point->x == -10 && point->y == -4);
    /* Independent append-only path oracle exercises ring wrap and backtracks. */
    x = 0; y = 0; count = 0;
    reference[count].x = x; reference[count].y = y; count++;
    DigimonTrail_Reset(&trail, x, y, 1, 1, 0);
    for (i = 0; i < 500; i++)
    {
        direction = 1 + ((i * 17 + i / 7) % 4);
        step = 1 << (i % 4);
        for (j = 0; j < step; j++)
        {
            if (direction == 1) y++;
            if (direction == 2) y--;
            if (direction == 3) x--;
            if (direction == 4) x++;
            reference[count].x = x; reference[count].y = y; count++;
        }
        DigimonTrail_Record(&trail, x, y, direction, 1);
        point = DigimonTrail_GetFollower(&trail);
        if (count <= 16) assert(point == NULL);
        else
        {
            assert(point->x == reference[count - 17].x);
            assert(point->y == reference[count - 17].y);
        }
    }
    puts("PASS: one-tile following, idle/turns, running/bikes, corners, long travel, elevation, warps, and safe reappearance");
    return 0;
}
