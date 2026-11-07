@ Caller owns object locks. Repeated calls safely recover unclaimed rewards.
Digimon_EventScript_ClaimRewards::
    specialvar VAR_RESULT, Digimon_ClaimNextReward
    compare VAR_RESULT, 1
    goto_if_eq Digimon_EventScript_RewardParty
    compare VAR_RESULT, 2
    goto_if_eq Digimon_EventScript_RewardPC
    compare VAR_RESULT, 3
    goto_if_eq Digimon_EventScript_RewardFull
    compare VAR_RESULT, 4
    goto_if_eq Digimon_EventScript_RewardOwnCrest
    return
Digimon_EventScript_RewardParty::
    playfanfare MUS_OBTAIN_BADGE
    msgbox Digimon_Text_RewardParty, MSGBOX_DEFAULT
    waitfanfare
    goto Digimon_EventScript_ClaimRewards
Digimon_EventScript_RewardPC::
    playfanfare MUS_OBTAIN_BADGE
    msgbox Digimon_Text_RewardPC, MSGBOX_DEFAULT
    waitfanfare
    goto Digimon_EventScript_ClaimRewards
Digimon_EventScript_RewardOwnCrest::
    playfanfare MUS_OBTAIN_BADGE
    msgbox Digimon_Text_RewardOwnCrest, MSGBOX_DEFAULT
    waitfanfare
    goto Digimon_EventScript_ClaimRewards
Digimon_EventScript_RewardFull::
    msgbox Digimon_Text_RewardFull, MSGBOX_DEFAULT
    return
Digimon_Text_RewardParty::
    .string "{STR_VAR_3}'s signal reaches you!\p"
    .string "You received the CREST OF\n"
    .string "{STR_VAR_2}!\p"
    .string "{STR_VAR_1} joins your party!\n"
    .string "Take this bond to the final battle!$"
Digimon_Text_RewardPC::
    .string "{STR_VAR_3}'s signal reaches you!\p"
    .string "You received the CREST OF\n"
    .string "{STR_VAR_2}!\p"
    .string "{STR_VAR_1} joined your PC storage.\n"
    .string "Use a PC to choose your battle team.$"
Digimon_Text_RewardOwnCrest::
    .string "Your own CREST OF {STR_VAR_2}\n"
    .string "awakens! All eight bonds shine.\p"
    .string "Find your friend at the LEAGUE gate.\n"
    .string "Face the DARK MASTERS together!$"
Digimon_Text_RewardFull::
    .string "Your party and PC storage are full.\p"
    .string "Your crest is safe. Make room, then\n"
    .string "speak to a leader or LEAGUE guard\l"
    .string "to receive your waiting partner.$"

Digimon_EventScript_TryReunion::
    call Digimon_EventScript_ClaimRewards
    specialvar VAR_RESULT, Digimon_ReunionReady
    compare VAR_RESULT, TRUE
    goto_if_ne Digimon_EventScript_ReunionNotReady
    goto_if_set FLAG_DIGIMON_REUNITED, Digimon_EventScript_ReunionDone
    msgbox Digimon_Text_EarlyReunion, MSGBOX_DEFAULT
    setflag FLAG_DIGIMON_REUNITED
Digimon_EventScript_ReunionDone::
    setvar VAR_RESULT, TRUE
    return
Digimon_EventScript_ReunionNotReady::
    setvar VAR_RESULT, FALSE
    return
Digimon_EventScript_FriendAtLeague::
    lock
    faceplayer
    call Digimon_EventScript_TryReunion
    msgbox Digimon_Text_FriendAtLeague, MSGBOX_DEFAULT
    release
    end
Digimon_Text_EarlyReunion::
    .string "TAI: Matt! Our signals finally meet!\p"
    .string "MATT: Every crest brought another\n"
    .string "friend and partner back to us.\p"
    .string "TAI: The DARK MASTERS are holding\n"
    .string "this broken multiverse together.\p"
    .string "MATT: Choose two partners to lead.\n"
    .string "We'll break their seals together!\p"
    .string "TAI: Then repair the glitch...\n"
    .string "and bring everyone home!$"
Digimon_Text_FriendAtLeague::
    .string "Our eight crests open the way.\p"
    .string "Use the PC to choose your team.\n"
    .string "Bring two healthy partners!$"
Digimon_Text_NeedTwoPartners::
    .string "Bring two healthy DIGIMON.\n"
    .string "The DARK MASTERS fight in pairs!$"
Digimon_Text_RewardsRequired::
    .string "Gather all eight DIGITAL KEYS and\n"
    .string "collect every crest and partner.\p"
    .string "If storage is full, make room and\n"
    .string "speak to the LEAGUE guard again.$"
