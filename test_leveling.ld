# Test file for the leveling system

# --- Entity Definitions ---
entity player_1
    level 1
    xp 0
    xp_to_next_level 100
    health 100
    max_hp 100
    strength 10
    crit_chance 0.1
end entity

entity xp_dummy
    name "XP Dummy"
    health 10
    strength 0
    xp_reward 120 # Enough to level up
end entity


# --- Script Execution ---

# --- Leveling Constants ---
define BASE_XP_TO_LEVEL_UP as 100
define XP_SCALE_FACTOR as 1.5
define HP_GAIN_PER_LEVEL as 15
define ATTACK_GAIN_PER_LEVEL as 3
define CRIT_CHANCE_GAIN_PER_LEVEL as 0.015

say "--- Player Stats Before ---"
say "Level: {player_1.level}"
say "XP: {player_1.xp} / {player_1.xp_to_next_level}"
say "HP: {player_1.health} / {player_1.max_hp}"
say "Strength: {player_1.strength}"
say "Crit Chance: {player_1.crit_chance}"
say "---------------------------"

say "\n--- Defeating the XP Dummy ---"
attack player_1 on xp_dummy
say "------------------------------"

say "\n--- Player Stats After ---"
say "Level: {player_1.level}"
say "XP: {player_1.xp} / {player_1.xp_to_next_level}"
say "HP: {player_1.health} / {player_1.max_hp}"
say "Strength: {player_1.strength}"
say "Crit Chance: {player_1.crit_chance}"
say "--------------------------"
