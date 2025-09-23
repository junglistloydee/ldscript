# ================================================================= #
# Functions & Event Handlers                                        #
# This file contains reusable code blocks (functions) and           #
# handlers for game events (like 'on death').                       #
# ================================================================= #

# --- FUNCTIONS ---
# A reusable function for the golem's turn in combat.
function golem_attack_turn
    if crystal_golem.health > 0
        say "The Crystal Golem lumbers towards you and swings its heavy fists!"
        # The target is the player who last attacked it.
        # We use a variable 'last_attacker' which is set in the main script.
        attack crystal_golem on {last_attacker}
        play_sound "sounds/swing.wav" # Placeholder sound
    end
end function


# --- EVENT HANDLERS ---
# This event triggers automatically whenever any entity's health reaches 0.
# The interpreter sets the 'last_death' variable to the ID of the defeated entity.
on death
    if last_death == "crystal_golem"
        say "With a final groan, the Crystal Golem shatters into a thousand pieces!"
        say "You see a chunk of Glimmering Ore in the rubble."
        play_music "music/theme.mp3" # Placeholder for a victory fanfare
        give 1 rare_ore

        # Grant XP to the player who delivered the final blow.
        # 'last_attacker' holds the ID of that player.
        gain_xp {last_attacker} {crystal_golem.xp_reward}
    else
        # Check if a player died. We use the local_player variable to be
        # compatible with multiplayer.
        if last_death == "{local_player}"
            say "You have been defeated... The world fades to black."
            # In a real game, you might end the script or trigger a game over sequence here.
        end
    end
end event
