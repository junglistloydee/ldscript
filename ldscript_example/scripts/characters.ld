# ================================================================= #
# Character & Entity Definitions                                    #
# This file contains all friendly and enemy entities.               #
# ================================================================= #

# --- PLAYER ---
# This template is used to create a new player entity when a client
# connects in multiplayer. It's also used as the base for player_1.
entity player_template
    # Basic combat stats
    health 100
    max_hp 100
    strength 8
    defense 2

    # Advanced combat stats
    damage_variance 2
    crit_chance 0.10
    crit_multiplier 1.5

    # Leveling stats
    level 1
    xp 0
    xp_to_next_level 100 # The amount of XP needed to reach level 2
end entity

# The default player entity for the host/single-player game.
# It is a copy of the player_template.
entity player_1
    health 100
    max_hp 100
    strength 8
    defense 2
    damage_variance 2
    crit_chance 0.10
    crit_multiplier 1.5
    level 1
    xp 0
    xp_to_next_level 100
end entity


# --- NPCs ---
# The blacksmith is a vendor. Their inventory is a comma-separated
# list of item IDs that they have for sale.
entity blacksmith
    name "Borin"
    inventory "potion,rusty_sword,wooden_shield"
end entity


# --- MONSTERS ---
# The main "boss" of this example.
entity crystal_golem
    name "Crystal Golem"
    health 80
    strength 15
    defense 5
    xp_reward 120 # XP granted to the player who defeats it
end entity
