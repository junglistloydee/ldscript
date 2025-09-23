# ================================================================= #
# LDScript Complete Example                                         #
# This is the main entry point for the game. It imports all other   #
# script files and contains the primary game logic that drives      #
# the player's adventure.                                           #
# ================================================================= #

# --- IMPORTS ---
# The 'import' command loads all definitions from other files.
# This is great for organizing a larger game.
import "scripts/data_structures.ld"
import "scripts/items.ld"
import "scripts/quests.ld"
import "scripts/characters.ld"
import "scripts/dialogs.ld"
import "scripts/functions.ld"

# --- GLOBAL GAME VARIABLES & SETUP ---
# Use 'define' to create global variables for the game session.
define game_title as "The Golem's Core"
define last_attacker as "none" # Will store who last attacked the golem

# Constants for the leveling system, read by the interpreter
define BASE_XP_TO_LEVEL_UP as 100
define XP_SCALE_FACTOR as 1.5
define HP_GAIN_PER_LEVEL as 20
define ATTACK_GAIN_PER_LEVEL as 5
define CRIT_CHANCE_GAIN_PER_LEVEL as 0.02

# Player starting stats and items
set stat gold to 50
give 1 rusty_sword
give 1 potion

# --- INTRO CUTSCENE ---
cutscene intro
    say "Welcome to {game_title}!"
    say "You are a traveler who has arrived at a remote village."
    say "Rumor has it the local blacksmith has a dangerous, but profitable, job available."
end cutscene

# ================================================================= #
# --- SCRIPT EXECUTION STARTS HERE ---                              #
# ================================================================= #

# --- INITIALIZATION ---
play_music "music/theme.mp3"
play cutscene intro
say "---"
say "Your adventure begins, {local_player}."
inventory
say "You are carrying {gold} gold."
say "---"

# --- MAIN INTERACTION ---
# Start the main conversation with the blacksmith.
# This will allow the player to get the quest.
start dialog blacksmith_main

# --- THE ADVENTURE ---
# This block only runs if the player accepted the quest from the blacksmith.
if quest find_rare_ore is active
    say "You leave the village and head towards the ominous Crystal Cave."

    # Demonstrate procedural room description
    generate_room_description as room_desc
    say "{room_desc}"

    say "You venture deeper into the cave. Finally, you see it..."
    say "The Crystal Golem turns its head towards you, its eyes glowing with a faint light."

    # --- MAIN COMBAT LOOP ---
    # This loop will continue for up to 20 turns or until someone is defeated.
    loop 20 times
        # Check for victory or defeat conditions to exit the loop early.
        if crystal_golem.health <= 0
            say "The golem has been defeated!"
            break # Exit the loop
        end
        if player_1.health <= 0
            say "You have been defeated!"
            break # Exit the loop
        end

        say "---"
        say "Your turn! Your HP: {player_1.health} | Golem HP: {crystal_golem.health}"
        say "You ready your weapon..."

        # Set the 'last_attacker' variable so the golem knows who to target.
        # This is important for multiplayer contexts.
        define last_attacker as "{local_player}"
        attack {local_player} on crystal_golem

        # The golem fights back by calling its function.
        call golem_attack_turn
    end
end

# --- POST-QUEST DEMONSTRATIONS ---
# This section demonstrates features that might be used after the main quest.
if quest find_rare_ore is completed
    say "---"
    say "With the golem defeated and the blacksmith rewarded, you are a local hero."

    # Demonstrate weighted loot drop
    say "You find a small chest left behind by the golem."
    weighted_random_choice monster_loot_table as loot
    say "Inside, you find: {loot}!"
    if loot == "potion"
        give 1 potion
    end
    if loot == "goblin_axe"
        give 1 goblin_axe
    end

    # Demonstrate skill usage
    if has skill blacksmithing
        say "You feel the knowledge of blacksmithing in your hands."
        say "You decide to try to improve your rusty sword."
        # A nested loop to show break/continue
        loop 2 times
            if {loop_index} == 0
                say "You heat the blade in the forge..."
                continue # Skip to the next iteration
            end
            say "You hammer the blade into a better shape!"
            break # Exit the inner loop
        end
        forget skill blacksmithing
        say "You have forgotten the ways of the forge for now."
    end
end

say "---"
say "Thank you for playing this comprehensive example of LDScript!"
say "End of script."
