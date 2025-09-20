# main.ld
# Main game script

# Import game modules
import "quest.ld"
import "dialogs.ld"

# Define variables
define playerName as "Alex"
define npcName as "the old man"

# Define a cutscene for the intro
cutscene game_intro
    say "In a quiet village, a new story begins."
    say "{playerName} is looking for an adventure."
    say "You see {npcName} sitting by the well."
end cutscene

# --- Script Execution Starts Here ---

# Play the intro cutscene
play cutscene game_intro

# Start the conversation based on quest state
if quest find_amulet is inactive
    start dialog old_man_initial
else
    start dialog old_man_active
end

# Check the final quest status
if quest find_amulet is completed
    say "You have completed the quest!"
else
    if quest find_amulet is active
        say "You are still on the quest to find the amulet."
    else
        say "You did not accept the quest."
    end
end
