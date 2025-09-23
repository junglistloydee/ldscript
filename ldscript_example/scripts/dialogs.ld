# ================================================================= #
# Dialogs & Conversations                                           #
# This file contains all the interactive dialog trees.              #
# ================================================================= #

dialog blacksmith_main
    say "---"
    say "{blacksmith.name} the blacksmith looks up from his anvil. 'What can I do for you?'"

    # Option to get the quest
    option "Are you in need of any help?"
        if quest find_rare_ore is inactive
            say "'As a matter of fact, I am,' he says, wiping his brow."
            say "'I need a special Glimmering Ore to finish a commission. It's found deep in the Crystal Cave, but a nasty Golem guards the place.'"
            say "'If you can bring me a piece, I'll make it worth your while.'"
            set quest find_rare_ore to active
            say "Quest Started: The Glimmering Ore"
        else
            say "'You're already helping me! That Glimmering Ore won't find itself!'"
        end
        start dialog blacksmith_main # Return to the main dialog menu
    end option

    # Option to turn in the quest
    option "I have that Glimmering Ore you wanted."
        if quest find_rare_ore is active and has rare_ore
            say "'You actually got it! Incredible!' He takes the ore from you."
            take 1 rare_ore
            say "He hands you a hefty pouch of gold as a reward."
            increase stat gold by 150
            say "Your gold is now {gold}."
            say "'You've got some real talent. Let me teach you a thing or two about the forge.'"
            learn skill blacksmithing
            say "You have learned the 'blacksmithing' skill!"
            set quest find_rare_ore to completed
        else
            say "'If you have it, I don't see it. Stop wasting my time.'"
        end
        start dialog blacksmith_main
    end option

    # Option to open the shop menu
    option "I'd like to see what you have for sale."
        say "'Of course, take a look.'"
        # This nested dialog creates a sub-menu for the shop
        dialog shop_menu
            shop blacksmith
            say "You have {gold} gold. What would you like to do?"

            option "Buy a Health Potion"
                buy 1 potion from blacksmith
                start dialog shop_menu # Return to the shop menu
            end option

            option "Sell my Goblin Axe"
                if has goblin_axe
                    sell 1 goblin_axe to blacksmith
                else
                    say "You don't have a Goblin Axe to sell."
                end
                start dialog shop_menu
            end option

            option "Nevermind, I'm done trading."
                start dialog blacksmith_main # Go back to the main blacksmith dialog
            end option
        end dialog
        start dialog shop_menu
    end option

    # Option to leave
    option "Nothing right now. Goodbye."
        say "'Stay safe out there.'"
    end option
end dialog
