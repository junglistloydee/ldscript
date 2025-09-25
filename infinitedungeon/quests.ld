# ================================================================= #
# Quest Definitions                                                 #
# ================================================================= #

quest any_foe_i "Any Foe I"
    description "The monsters in these tunnels have been getting bolder. Clear out 5 enemies, any enemies will do."
    state inactive
    target_count 5
    reward_gold 50
    reward_xp 25
    reward_item "small_backpack"
    giver_npc_name "Grumpy Guard"
    required_level 1
    is_repeatable false
end quest

quest any_foe_ii "Any Foe II"
    description "You handled the early threats well, I heard. The deeper parts of the dungeon need clearing. Eliminate 10 more enemies."
    state inactive
    target_count 10
    reward_gold 100
    reward_xp 75
    reward_item "chainmail_tunic"
    giver_npc_name "Veteran Explorer"
    required_level 3
    prerequisite_quest "any_foe_i"
    is_repeatable false
end quest

quest any_foe_iii "Any Foe III"
    description "You've shown great skill, but the dungeon is vast and dangerous. Defeat 15 more foes to prove your worth."
    state inactive
    target_count 15
    reward_gold 200
    reward_xp 500
    reward_item "large_backpack"
    giver_npc_name "Old Wizard"
    required_level 5
    prerequisite_quest "any_foe_ii"
    is_repeatable false
end quest

quest any_foe_iv "Any Foe IV"
    description "You have become a true hero of the dungeon. Defeat 50 more foes to complete your legacy."
    state inactive
    target_count 50
    reward_gold 500
    reward_xp 1000
    reward_item "great_halberd"
    giver_npc_name "Dungeon Historian"
    required_level 7
    prerequisite_quest "any_foe_iii"
    is_repeatable false
end quest

quest any_foe_v "Any Foe V"
    description "You have reached the pinnacle of your journey. Defeat 100 more foes to cement your legacy."
    state inactive
    target_count 100
    reward_gold 1000
    reward_xp 2000
    reward_item "legendary_sword_of_the_ancients"
    giver_npc_name "Dungeon Master"
    required_level 10
    prerequisite_quest "any_foe_iv"
    is_repeatable false
end quest

quest fetch_item_i "The Collector's Curiosities"
    description "I'm looking for some glowing mushrooms. They're quite beautiful. Bring me 5 and I'll make it worth your while."
    state inactive
    target_item "glowing_mushroom"
    target_count 5
    reward_gold 100
    reward_xp 150
    reward_item "medium_backpack"
    giver_npc_name "Elara, the Collector"
    required_level 1
    is_repeatable false
end quest

quest fetch_item_ii "The Archivist's Lost Pages"
    description "I've lost some important scrolls. They're tattered, but priceless to me. Find 3 of them for me."
    state inactive
    target_item "tattered_scroll"
    target_count 3
    reward_gold 250
    reward_xp 400
    reward_item "enchanted_cloak"
    giver_npc_name "Borin, the Archivist"
    required_level 10
    prerequisite_quest "fetch_item_i"
    is_repeatable false
end quest

quest fetch_item_iii "The Alchemist's Ingredients"
    description "I need some... potent ingredients for a new potion. Bring me 10 vials of monster blood."
    state inactive
    target_item "vial_of_monster_blood"
    target_count 10
    reward_gold 500
    reward_xp 1000
    reward_item "greatsword_of_shadows"
    giver_npc_name "Lyra, the Alchemist"
    required_level 15
    prerequisite_quest "fetch_item_ii"
    is_repeatable false
end quest

quest fetch_item_iv "The Elder's Balance"
    description "The dungeon's energy is out of balance. A shard of dark crystal is causing it. Bring it to me, so I may restore harmony."
    state inactive
    target_item "shard_of_dark_crystal"
    target_count 1
    reward_gold 1500
    reward_xp 3000
    reward_item "heart_of_the_mountain"
    giver_npc_name "Zephyr, the Elder"
    required_level 20
    prerequisite_quest "fetch_item_iii"
    is_repeatable false
end quest

quest the_unfit_bridesmaid "The Unfit Bridesmaid"
    description "My bridesmaid... she's not fit for the job! Please, can you find the one who is clearly not supposed to be a bridesmaid? I'll reward you handsomely."
    state inactive
    target_npc_name "a man in a dress"
    reward_gold 150
    reward_xp 200
    reward_item "enchanted_cloak"
    giver_npc_name "sobbing woman"
    required_level 1
    is_repeatable false
end quest