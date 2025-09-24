# vendor_example.ld
#
# This example demonstrates the new vendor functionality.
#
# To run this example:
# python ldscript_interpreter.py vendor_example.ld

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

# Main game loop
function main_loop
    say "You are in a town. Bob the blacksmith is here."
    start dialog bob_dialog
end function

# Dialog with the vendor
dialog bob_dialog
    say "Hello, I'm {vendor.name}. What can I do for you?"
    option "Buy something"
        shop vendor
        start dialog buy_dialog
    end option
    option "Sell something"
        inventory
        start dialog sell_dialog
    end option
    option "Nothing, thanks"
        say "Farewell."
    end option
end dialog

dialog buy_dialog
    say "What would you like to buy? (e.g., 'buy 1 sword')"
    option "Buy a sword"
        buy 1 sword from vendor
        start dialog bob_dialog
    end option
    option "Buy a shield"
        buy 1 shield from vendor
        start dialog bob_dialog
    end option
    option "Back to main menu"
        start dialog bob_dialog
    end option
end dialog

dialog sell_dialog
    say "What would you like to sell? (e.g., 'sell 1 potion')"
    option "Sell a potion"
        sell 1 potion to vendor
        start dialog bob_dialog
    end option
    option "Back to main menu"
        start dialog bob_dialog
    end option
end dialog


# Start the game
call setup_player
call main_loop
