#include "global.h"
#include "digimon_follower.h"
#include "digimon_trail.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_player_avatar.h"
#include "fieldmap.h"
#include "palette.h"
#include "sprite.h"
#include "constants/event_objects.h"
#include "constants/flags.h"

/* A visual companion deliberately consumes no map ObjectEvent slot. It cannot
 * block doors, interrupt a trainer's approach, trigger scripts or be pushed. */
static EWRAM_DATA struct DigimonTrail sTrail = {0};
static EWRAM_DATA u8 sFollowerSpriteId = MAX_SPRITES;
static EWRAM_DATA u8 sMapGroup = 0xFF;
static EWRAM_DATA u8 sMapNum = 0xFF;
static EWRAM_DATA bool8 sTrailReady = FALSE;
static EWRAM_DATA bool8 sCutsceneHidden = FALSE;

static void SpriteCB_DigimonFollower(struct Sprite *sprite)
{
    /* Position is updated after all actors and the camera have advanced. */
}

static u8 GetFollowerGraphicsId(void)
{
#ifdef RUBY
    return OBJ_EVENT_GFX_AGUMON_FOLLOWER;
#else
    return OBJ_EVENT_GFX_GABUMON_FOLLOWER;
#endif
}

static bool8 HasFollowerSprite(void)
{
    return sFollowerSpriteId < MAX_SPRITES
        && gSprites[sFollowerSpriteId].inUse
        && gSprites[sFollowerSpriteId].callback == SpriteCB_DigimonFollower;
}

void DigimonFollower_Reset(void)
{
    if (HasFollowerSprite())
    {
        DestroySprite(&gSprites[sFollowerSpriteId]);
        FreeSpritePaletteByTag(GetObjectEventGraphicsInfo(GetFollowerGraphicsId())->paletteTag);
    }
    sFollowerSpriteId = MAX_SPRITES;
    sMapGroup = 0xFF;
    sMapNum = 0xFF;
    sTrailReady = FALSE;
    sCutsceneHidden = FALSE;
}

void DigimonFollower_Hide(void)
{
    sCutsceneHidden = TRUE;
    sTrailReady = FALSE;
    if (HasFollowerSprite())
        gSprites[sFollowerSpriteId].invisible = TRUE;
}

void DigimonFollower_Show(void)
{
    sCutsceneHidden = FALSE;
    sTrailReady = FALSE;
}

static bool8 CanStartBehindPlayer(const struct ObjectEvent *player)
{
    s16 x = player->currentCoords.x;
    s16 y = player->currentCoords.y;
    u8 elevation;

    if (player->facingDirection == DIR_SOUTH)
        y--;
    else if (player->facingDirection == DIR_NORTH)
        y++;
    else if (player->facingDirection == DIR_WEST)
        x++;
    else if (player->facingDirection == DIR_EAST)
        x--;
    else
        return FALSE;
    elevation = MapGridGetElevationAt(x, y);
    return MapGridGetCollisionAt(x, y) == 0
        && elevation != 0xF
        && AreZCoordsCompatible(elevation, player->previousElevation)
        && GetObjectEventIdByXYZ(x, y, player->previousElevation) == OBJECT_EVENTS_COUNT;
}

void DigimonFollower_Update(void)
{
    struct ObjectEvent *player;
    struct Sprite *playerSprite;
    struct Sprite *follower;
    const struct ObjectEventGraphicsInfo *graphics;
    const struct DigimonTrailPoint *point;
    s16 footX, footY;
    int moved;
    u8 anim;

    if (!FlagGet(FLAG_SYS_POKEMON_GET)
        || gPlayerAvatar.objectEventId >= OBJECT_EVENTS_COUNT
        || gPlayerAvatar.spriteId >= MAX_SPRITES)
    {
        DigimonFollower_Reset();
        return;
    }
    player = &gObjectEvents[gPlayerAvatar.objectEventId];
    playerSprite = &gSprites[gPlayerAvatar.spriteId];
    if (!player->active || !player->isPlayer || !playerSprite->inUse
        || player->spriteId != gPlayerAvatar.spriteId)
    {
        DigimonFollower_Reset();
        return;
    }
    /* Follow even on bikes, water and underwater. Only explicit cinematic
     * suppression or the player becoming invisible hides the companion. */
    if (sCutsceneHidden || player->invisible || playerSprite->invisible)
    {
        if (HasFollowerSprite())
            gSprites[sFollowerSpriteId].invisible = TRUE;
        sTrailReady = FALSE;
        return;
    }
    if (sMapGroup != gSaveBlock1.location.mapGroup || sMapNum != gSaveBlock1.location.mapNum)
    {
        DigimonFollower_Reset();
        sMapGroup = gSaveBlock1.location.mapGroup;
        sMapNum = gSaveBlock1.location.mapNum;
    }
    if (!HasFollowerSprite())
    {
        sTrailReady = FALSE;
        if (gPaletteFade.active)
            return;
        sFollowerSpriteId = AddPseudoObjectEvent(GetFollowerGraphicsId(), SpriteCB_DigimonFollower, 0, 0, 0);
        if (sFollowerSpriteId == MAX_SPRITES)
            return;
        /* A full palette allocator must not paint the partner with palette 15. */
        graphics = GetObjectEventGraphicsInfo(GetFollowerGraphicsId());
        if (IndexOfSpritePaletteTag(graphics->paletteTag) == 0xFF)
        {
            DestroySprite(&gSprites[sFollowerSpriteId]);
            sFollowerSpriteId = MAX_SPRITES;
            return;
        }
        follower = &gSprites[sFollowerSpriteId];
        follower->centerToCornerVecX = -(graphics->width >> 1);
        follower->centerToCornerVecY = -(graphics->height >> 1);
        follower->coordOffsetEnabled = TRUE;
        follower->invisible = TRUE;
    }
    follower = &gSprites[sFollowerSpriteId];
    footX = playerSprite->x;
    footY = playerSprite->y - playerSprite->centerToCornerVecY;
    moved = 0;
    if (!sTrailReady)
    {
        DigimonTrail_Reset(&sTrail, footX, footY, player->facingDirection,
            player->previousElevation, CanStartBehindPlayer(player));
        sTrailReady = TRUE;
    }
    else
    {
        moved = DigimonTrail_Record(&sTrail, footX, footY,
            player->movementDirection, player->previousElevation);
    }
    point = DigimonTrail_GetFollower(&sTrail);
    if (point == NULL)
    {
        follower->invisible = TRUE;
        return;
    }
    follower->x = point->x;
    follower->y = point->y + follower->centerToCornerVecY;
    follower->x2 = 0;
    follower->y2 = 0;
    follower->oam.priority = ZCoordToPriority(point->elevation);
    follower->subspriteTableNum = point->elevation == 13 || point->elevation == 14 ? 0
        : (follower->oam.priority == 1 ? 2 : 1);
    SetObjectSubpriorityByZCoord(point->elevation, follower, 1);
    anim = moved ? GetMoveDirectionAnimNum(point->direction) : GetFaceDirectionAnimNum(point->direction);
    if (follower->animNum != anim)
        StartSpriteAnim(follower, anim);
    follower->animPaused = !moved;
    UpdateObjectEventSpriteVisibility(follower, FALSE);
}
