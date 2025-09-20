# ldscript example demonstrating all features

# Define variables
define playerName as "Alex"
define npcName as "the old man"

# Define a quest
quest find_amulet "The Lost Amulet"
    description "Find the Old Man's lost amulet."
    state inactive
end quest

# Define a cutscene for the intro
cutscene game_intro
    say "In a quiet village, a new story begins."
    say "{playerName} is looking for an adventure."
    say "You see {npcName} sitting by the well."
end cutscene

# Define the main dialog
dialog old_man_talk
    say "{npcName}: 'Hello, young {playerName}.'"
    if quest find_amulet is inactive
        say "{npcName}: 'I seem to have lost my amulet. It's very precious to me.'"
        option "How can I help?"
            say "{npcName}: 'If you could find it for me, I would be most grateful.'"
            say "The quest 'The Lost Amulet' has started!"
            set quest find_amulet to active
        end option
        option "Sorry, I'm busy."
            say "{npcName}: 'Ah, a shame. Well, safe travels.'"
        end option
    end if
    if quest find_amulet is active
        say "{npcName}: 'Any luck finding my amulet?'"
        option "I'm still looking."
            say "{npcName}: 'Don't give up!'"
        end option
        option "I found it!"
            say "{npcName}: 'You did! Oh, thank you, thank you!'"
            say "You hand the amulet to the old man."
            set quest find_amulet to completed
        end option
    end if
end dialog

# --- Script Execution Starts Here ---

# Play the intro cutscene
play cutscene game_intro

# Start the conversation
start dialog old_man_talk

# Check the final quest status
if quest find_amulet is completed
    say "You have completed the quest!"
elif quest find_amulet is active
    say "You are still on the quest to find the amulet."
else
    say "You did not accept the quest."
end
