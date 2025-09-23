# ================================================================= #
# Item Definitions                                                  #
# This file contains all equippable and consumable items.           #
# ================================================================= #

# --- CONSUMABLES ---
item potion
    name "Health Potion"
    description "A common potion that restores 20 health."
    price 20
end item

# --- WEAPONS ---
item rusty_sword
    name "Rusty Sword"
    description "A worn-out sword. Better than nothing."
    price 10
    type "weapon"
    damage 5
end item

item goblin_axe
    name "Goblin Axe"
    description "A crude but sharp axe, favored by goblins."
    price 35
    type "weapon"
    damage 8
end item

# --- SHIELDS ---
item wooden_shield
    name "Wooden Shield"
    description "A simple shield made of splintery wood."
    price 15
    type "shield"
    defense 3
end item

# --- ARMOR ---
item leather_armor
    name "Leather Armor"
    description "Hardened leather plates. Offers basic protection."
    price 50
    type "armor"
    subtype "body_armor"
    defense 5
end item

item shadowy_cloak
    name "Shadowy Cloak"
    description "A dark cloak that seems to absorb the light."
    price 120
    type "armor"
    subtype "cloak"
    defense 2
end item

# --- MISC & QUEST ITEMS ---
item rare_ore
    name "Glimmering Ore"
    description "A rare, pulsating ore. The blacksmith might want this."
    # No price, as it's a quest item and can't be sold normally.
end item

item gold_coins
    name "Gold Coins"
    description "A handful of gold coins."
    price 1 # For accounting purposes
end item
