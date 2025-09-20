# ldscript Demo: The Lost Key

# --- Setup ---
define playerName as "Valerius"
define playerHealth as 100
define searchAttempts as 5
define foundKey as "false"

# --- Introduction ---
say "Welcome, {playerName}. You are in a dark room."
say "You must find the key to escape."
say "You have {searchAttempts} attempts to search the room."

# --- The Search ---
loop searchAttempts times
    say "You search the dusty corners of the room... (Attempt {loop_index})"

    # Simulate a random chance of finding the key
    if loop_index == 3
        say "You found the key under a loose floorboard!"
        define foundKey as "true"
        break
    else
        say "You found nothing but dust and cobwebs."
    end
end

# --- Conclusion ---
say "Your search is over."
if foundKey == "true"
    say "Congratulations, {playerName}! You can now unlock the door and escape."
else
    say "You failed to find the key. The door remains locked."
end

say "You finish with {playerHealth} health."
