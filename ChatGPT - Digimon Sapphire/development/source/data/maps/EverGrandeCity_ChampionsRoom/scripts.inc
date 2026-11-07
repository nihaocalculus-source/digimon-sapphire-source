EverGrandeCity_ChampionsRoom_MapScripts::
    map_script MAP_SCRIPT_ON_FRAME_TABLE, EverGrandeCity_ChampionsRoom_OnFrame
    .byte 0
EverGrandeCity_ChampionsRoom_OnFrame::
    map_script_2 VAR_TEMP_1, 0, Digimon_EventScript_Reunion
    .2byte 0
Digimon_EventScript_Reunion::
    lockall
    special DigimonFollower_Hide
    setvar VAR_TEMP_1, 1
    call Digimon_EventScript_TryReunion
    specialvar VAR_RESULT, Digimon_CanEnterFinale
    compare VAR_RESULT, TRUE
    goto_if_ne Digimon_EventScript_GateLocked
    goto_if_set FLAG_DIGIMON_FINAL_BATTLE_WON, Digimon_EventScript_ReturnHome
    applymovement LOCALID_PLAYER, Common_Movement_WalkUp4
    waitmovement 0
    msgbox Digimon_Text_Reunion, MSGBOX_DEFAULT
    closemessage
    showmonpic SPECIES_BLAZIKEN, 10, 3
    msgbox Digimon_Text_Courage, MSGBOX_DEFAULT
    hidemonpic
    showmonpic SPECIES_SWAMPERT, 10, 3
    msgbox Digimon_Text_Friendship, MSGBOX_DEFAULT
    hidemonpic
    msgbox Digimon_Text_DNA, MSGBOX_DEFAULT
    closemessage
    fadescreenspeed FADE_TO_WHITE, 4
    delay 40
    fadescreenspeed FADE_FROM_WHITE, 4
    showmonpic SPECIES_RAYQUAZA, 10, 3
    playfanfare MUS_OBTAIN_BADGE
    msgbox Digimon_Text_Omegamon, MSGBOX_DEFAULT
    waitfanfare
    hidemonpic
    closemessage
    specialvar VAR_RESULT, Digimon_PrepareFinalBattle
    compare VAR_RESULT, TRUE
    goto_if_ne Digimon_EventScript_GateLocked
    trainerbattle_no_intro TRAINER_STEVEN, Digimon_Text_DarkCoreDefeat
    goto_if_unset FLAG_DIGIMON_FINAL_BATTLE_WON, Digimon_EventScript_GateLocked
    clearflag FLAG_DIGIMON_FINALE_ARMED
Digimon_EventScript_ReturnHome::
    msgbox Digimon_Text_GateHome, MSGBOX_DEFAULT
    closemessage
    fadescreen FADE_TO_WHITE
    warp MAP_EVER_GRANDE_CITY_HALL_OF_FAME, 255, 7, 16
    waitstate
    releaseall
    end
Digimon_EventScript_GateLocked::
    special DigimonFollower_Show
    msgbox Digimon_Text_GateLocked, MSGBOX_DEFAULT
    releaseall
    end
