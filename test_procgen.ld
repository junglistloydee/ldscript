# Test file for procedural generation commands

# --- Data Definitions ---
dictionary spawn_weights
    sword 0.1
    shield 0.2
    potion 0.7
end dictionary

# --- Script Execution ---
say "--- Testing weighted_random_choice ---"
loop 10 times
    weighted_random_choice spawn_weights as spawned_item
    say "Spawned: {spawned_item}"
end
say "------------------------------------"
