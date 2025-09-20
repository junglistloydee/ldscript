# Defines dialogs for the old man character

dialog old_man_initial
    say "{npcName}: 'Hello, young {playerName}.'"
    say "{npcName}: 'I seem to have lost my amulet. It's very precious to me.'"
    option "How can I help?"
        say "{npcName}: 'If you could find it for me, I would be most grateful.'"
        say "The quest 'The Lost Amulet' has started!"
        set quest find_amulet to active
    end option
    option "Sorry, I'm busy."
        say "{npcName}: 'Ah, a shame. Well, safe travels.'"
    end option
end dialog

dialog old_man_active
    say "{npcName}: 'Any luck finding my amulet?'"
    option "I'm still looking."
        say "{npcName}: 'Don't give up!'"
    end option
    option "I found it!"
        say "{npcName}: 'You did! Oh, thank you, thank you!'"
        say "You hand the amulet to the old man."
        set quest find_amulet to completed
    end option
end dialog
