# ================================================================= #
# Data Structures                                                   #
# This file defines reusable data structures like lists and         #
# dictionaries for procedural generation and randomization.         #
# ================================================================= #

# --- LISTS FOR ROOM DESCRIPTIONS ---
# These lists are used by the 'generate_room_description' command.

string_list adjectives
    "damp"
    "dusty"
    "ancient"
    "shadowy"
    "cold"
    "forgotten"
end string_list

string_list room_types
    "cavern"
    "hallway"
    "chamber"
    "repository"
    "sanctum"
end string_list

string_list details
    "an eerie silence"
    "the faint sound of dripping water"
    "strange markings on the walls"
    "a pile of discarded bones"
    "a sense of being watched"
end string_list

# --- DICTIONARY FOR WEIGHTED LOOT DROPS ---
# Used by 'weighted_random_choice' to determine loot.
# The number represents the "weight" or probability.
dictionary monster_loot_table
    potion 50
    gold_coins 30
    goblin_axe 15
    rare_ore 5
end dictionary
