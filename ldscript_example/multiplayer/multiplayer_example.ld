# multiplayer_example.ld
# A script to test the multiplayer functionality.

# Define a template for players that join.
# The server will use this to create entities for new clients (e.g., player_2, player_3...).
entity player_template
    stat health 100
    stat strength 10
end entity

# The host is player_1 by default. This entity must exist for the host.
# Note: The name 'player_1' is hardcoded for the host in the interpreter.
entity player_1
    stat health 100
    stat strength 10
end entity

# A monster for all players to interact with.
entity goblin
    stat health 120
    stat strength 5
end entity

# --- Script Logic ---

say "--- Multiplayer Test Script ---"
say "A goblin with {goblin.health} HP has appeared!"
say "You are {local_player} with {local_player.health} HP."
say " "
say "To connect as a client, run this in a new terminal:"
say "python ldscript_interpreter.py multiplayer_example.ld --connect 127.0.0.1"
say " "
say "From either the host or a client, you can now attack the goblin."
say "To do so, you'll need to type commands into the console after the script finishes."
say "For example, to attack the goblin, type:"
say "attack local_player on goblin"
say " "
say "The goblin's health is shared. Watch it decrease across all connected games!"
say "--------------------------------"

# The script itself is very short. The main test is for players to
# interact with the shared world state after the script has run.
# The server will keep running, listening for commands from clients.
