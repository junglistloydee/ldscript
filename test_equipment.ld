# Test file for the equipment system

# --- Item Definitions ---
item iron_sword
    name "Iron Sword"
    type "weapon"
    damage 10
end item

item wooden_shield
    name "Wooden Shield"
    type "shield"
    defense 5
end item

item leather_armor
    name "Leather Armor"
    type "armor"
    subtype "body_armor"
    defense 8
end item

item shimmering_cloak
    name "Shimmering Cloak"
    type "armor"
    subtype "cloak"
    defense 2
end item

item strength_ring
    name "Ring of Strength"
    type "equipment"
    description "A simple ring that boosts strength."
end item

item health_potion
    name "Health Potion"
    type "consumable"
    description "A simple health potion."
end item


# --- Script Execution ---

say "--- Initial State ---"
give 1 iron_sword
give 1 wooden_shield
give 1 leather_armor
give 1 shimmering_cloak
give 1 strength_ring
give 1 health_potion

inventory
equipment
say "---------------------"

say "\n--- Equipping Sword ---"
equip iron_sword
inventory
equipment
say "-----------------------"

say "\n--- Equipping Shield and Armor ---"
equip wooden_shield
equip leather_armor
inventory
equipment
say "----------------------------------"

say "\n--- Equipping Cloak and Misc Item ---"
equip shimmering_cloak
equip strength_ring
inventory
equipment
say "-------------------------------------"

say "\n--- Trying to equip a non-equippable item ---"
equip health_potion
say "-----------------------------------------------"

say "\n--- Unequipping the sword ---"
unequip iron_sword
inventory
equipment
say "-----------------------------"
