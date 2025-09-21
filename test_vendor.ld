# test_vendor.ld
#
# This script tests the vendor functionality in a non-interactive way.

# Define some items that will be used in the game
item sword
    name "Iron Sword"
    description "A basic but reliable sword."
    price 100
end item

item shield
    name "Wooden Shield"
    description "A simple shield that can block some attacks."
    price 50
end item

item potion
    name "Health Potion"
    description "Restores 20 health."
    price 20
end item

# Define the vendor NPC
entity vendor
    stat name "Bob the Blacksmith"
    stat health 100
    stat strength 10
    stat inventory "sword,shield"
end entity

# Give the player some starting gold and an item to sell
function setup_player
    define gold as 150
    give 1 potion
end function

# --- Test Execution ---

# 1. Setup
call setup_player
say "--- Initial State ---"
inventory
say "Player gold: {gold}"

# 2. Show shop
say "\n--- Vendor's Shop ---"
shop vendor

# 3. Buy a sword
say "\n--- Buying a sword ---"
buy 1 sword from vendor
inventory
say "Player gold: {gold}"

# 4. Sell a potion
say "\n--- Selling a potion ---"
sell 1 potion to vendor
inventory
say "Player gold: {gold}"

# 5. Try to buy something too expensive
say "\n--- Trying to buy something unaffordable ---"
buy 1 sword from vendor
say "Player gold: {gold}"
