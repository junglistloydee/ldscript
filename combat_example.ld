# ldscript example demonstrating combat, functions, events, and sound.

# --- Entity Definitions ---
entity player
    stat health 100
    stat strength 12
    stat defense 5
end entity

entity dragon
    stat health 200
    stat strength 18
    stat defense 8
end entity

# --- Function Definitions ---
function player_turn
    say "Player attacks the dragon!"
    attack player on dragon
    play_sound "sounds/sword_swing.wav"
    say "Dragon's health is now {dragon.health}"
end function

function dragon_turn
    say "The dragon breathes fire!"
    attack dragon on player
    play_sound "sounds/dragon_roar.wav"
    say "Player's health is now {player.health}"
end function

# --- Event Handlers ---
on death
    if last_death == "dragon"
        say "The mighty dragon has been slain! Victory is yours!"
        play_music "music/victory_fanfare.mp3"
    else
        say "You have been defeated by the dragon. The kingdom is doomed."
        play_music "music/game_over.mp3"
    end
end event

# --- Script Execution Starts Here ---
play_music "music/battle_theme.mp3"
say "A fearsome dragon appears! Prepare for battle!"
say "Player: {player.health} HP | Dragon: {dragon.health} HP"

loop 10 times
    # Player's turn
    call player_turn
    if dragon.health <= 0
        break
    end

    # Dragon's turn
    call dragon_turn
    if player.health <= 0
        break
    end
end

say "The battle has ended."
