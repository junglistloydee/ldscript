# Test file for the enhanced combat system

# --- Item Definitions ---
item steel_sword
    name "Steel Sword"
    type "weapon"
    damage 10
end item

item iron_armor
    name "Iron Armor"
    type "armor"
    subtype "body_armor"
    defense 5
end item

# --- Entity Definitions ---
entity player_1
    health 100
    strength 8
    damage_variance 2
    crit_chance 0.2
    crit_multiplier 1.5
end entity

entity goblin_brute
    name "Goblin Brute"
    health 50
    strength 12
    damage_variance 3
    crit_chance 0.1
    crit_multiplier 2.0
    defense 3
end entity


# --- Script Execution ---

say "--- Initial State ---"
give 1 steel_sword
give 1 iron_armor
equip steel_sword
equip iron_armor
say "Player equipped for battle."
say "---------------------"

say "\n--- Player attacks Goblin ---"
attack player_1 on goblin_brute
say "---------------------------"

say "\n--- Goblin attacks Player ---"
attack goblin_brute on player_1
say "---------------------------"
