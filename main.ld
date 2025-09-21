item potion
    name "Health Potion"
    description "Restores 20 health."
    price 20
end item

item goblin_axe
    name "Goblin Axe"
    description "A crude but sharp axe."
    price 35
end item

item rare_ore
    name "Glimmering Ore"
    description "A rare ore needed by the blacksmith."
end item

quest get_rare_ore "The Glimmering Ore"
    description "Fetch a piece of Glimmering Ore from the Crystal Cave for the blacksmith."
    state inactive
end quest

entity player_template
    stat health 100
    stat strength 10
end entity

entity player_1
    stat health 100
    stat strength 10
end entity

entity blacksmith
    stat name "Borin"
    stat inventory "potion" # Items the vendor sells.
end entity

entity golem
    stat health 80
    stat strength 15
end entity

function golem_turn
    if golem.health > 0
        say "The Crystal Golem swings its heavy fists!"
        # The target is the player who last attacked it.
        attack golem on {last_attacker}
        play_sound "sounds/dragon_roar.wav" # Using existing sound for demo
        say "{last_attacker}'s health is now {local_player.health}."
    end
end function

on death
    if last_death == "golem"
        say "The Crystal Golem shatters into a thousand pieces!"
        say "You see a chunk of Glimmering Ore in the rubble."
        play_music "music/victory_fanfare.mp3"
        give 1 rare_ore
        set quest get_rare_ore to completed
    else
        # Check if a player died
        if last_death == "player_1" or last_death == "player_2"
            say "You have been defeated... The world fades to black."
            play_music "music/game_over.mp3"
        end
    end
end event

dialog blacksmith_talk
    say "---"
    say "{blacksmith.name} the blacksmith looks at you. 'What do you need?'"

    option "I'm looking for work."
        if quest get_rare_ore is inactive
            say "'I need a special ore from the Crystal Cave to the north,' he says."
            say "'It's guarded by a Golem. Bring me a piece and I'll reward you.'"
            set quest get_rare_ore to active
            say "Quest Started: The Glimmering Ore"
        else
            say "'You're already on the job! Get me that ore!'"
        end
        start dialog blacksmith_talk # Return to the main dialog
    end option

    option "I have the ore you wanted."
        if quest get_rare_ore is completed and has rare_ore
            say "'You got it! Amazing!' He takes the ore from you."
            take 1 rare_ore
            say "He hands you a hefty pouch of gold."
            increase stat gold by 100
            say "Your gold is now {gold}."
            say "'As promised, let me teach you a thing or two...'"
            learn skill blacksmithing
            say "You have learned the 'blacksmithing' skill!"
        else
            say "'You don't have it! Stop wasting my time.'"
        end
        start dialog blacksmith_talk
    end option

    option "I'd like to trade."
        dialog shop_menu
            shop blacksmith
            say "What would you like to do?"
            option "Buy a potion"
                buy 1 potion from blacksmith
                start dialog shop_menu
            end option
            option "Sell my goblin axe"
                if has goblin_axe
                    sell 1 goblin_axe to blacksmith
                else
                    say "You don't have a goblin axe to sell."
                end
                start dialog shop_menu
            end option
            option "Nevermind"
                start dialog blacksmith_talk
            end option
        end dialog
        start dialog shop_menu
    end option

    option "Leave."
        say "You leave the blacksmith's shop."
    end option
end dialog

define playerName as "Hero"
set stat gold to 50
give 1 goblin_axe

cutscene intro
    say "Your name is {playerName}, a traveler seeking fortune."
    say "You arrive at a small village with a renowned blacksmith."
end cutscene

play_music "music/battle_theme.mp3" # Using for ambient music
play cutscene intro

say "---"
say "Welcome, {local_player}! Your adventure begins." # Uses local_player for multiplayer context.
say "You have {gold} gold."
inventory # Display starting inventory.

start dialog blacksmith_talk

if quest get_rare_ore is active
    say "You head north towards the Crystal Cave."

    # Use 'loop' and 'random' to simulate a small event on the journey.
    loop 1 times
        random luck from 1 to 2
        if {luck} == 1
            say "On the path, you find a lost Health Potion!"
            give 1 potion
        end
    end

    say "You enter the cave and see the Crystal Golem!"

    loop 10 times
        if golem.health <= 0 or player_1.health <= 0 # Check host health as a baseline
            break # Exit the loop if battle is over.
        end

        say "---"
        say "Your turn! Golem HP: {golem.health}, Your HP: {local_player.health}"
        say "You attack the golem!"
        # Any connected player can attack the shared golem.
        define last_attacker as "{local_player}" # Set a variable for the golem's target
        attack local_player on golem
        play_sound "sounds/sword_swing.wav"

        call golem_turn
    end
end

if has skill blacksmithing
    say "---"
    say "You feel you have learned all you can from the blacksmith."
    forget skill blacksmithing # Demonstrate forgetting a skill.

    if has skill blacksmithing
        say "You are still a blacksmith."
    else
        say "You have forgotten the ways of the forge."
    end
end

say "---"
say "Your journey in this small village is over. Thank you for playing!"
