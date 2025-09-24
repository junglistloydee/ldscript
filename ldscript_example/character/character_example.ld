# character_example.ld
# A script to test the new character-related features.

say "--- Character Test Script ---"

# 1. Stats
say "\n--- Testing Stats ---"
set stat health to 100
set stat mana to 50
say "Initial stats: Health is {health}, Mana is {mana}."

increase stat strength by 5
say "After training, strength is now {strength}."

decrease stat mana by 15
say "After casting a spell, mana is now {mana}."

if {strength} > 3
    say "You feel strong!"
end

if {mana} < 40
    say "You are low on mana."
end

# 2. Skills
say "\n--- Testing Skills ---"
say "You visit a trainer..."
learn skill magic
say "You have learned the 'magic' skill."

if has skill magic
    say "You are a mage."
else
    say "You are not a mage."
end

say "You decide magic is not for you."
forget skill magic
say "You have forgotten the 'magic' skill."

if has skill magic
    say "You are still a mage."
else
    say "You are no longer a mage."
end

# 3. Inventory
say "\n--- Testing Inventory ---"
say "You find some items."
give 5 health_potion
give sword
say "You received 5 health potions and a sword."

if has 3 health_potion
    say "You have at least 3 health potions."
end

if has sword
    say "You have a sword."
end

say "You drink one potion."
take health_potion
say "You used a health potion."

if has 5 health_potion
    say "You still have 5 health potions."
else
    say "You have less than 5 health potions now."
end

take 10 gold # This should fail gracefully
say "\n--- End of Test ---"
