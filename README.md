# ldscript

ldscript is a lightweight, natural-language scripting language designed for embedding simple game logic into Python-based games, with a focus on RPG-style mechanics.

The goal is to provide a syntax that is easy for game designers and writers to read and use without needing deep programming knowledge.

## Features

*   **Simple Syntax:** Commands are designed to be read like plain English.
*   **Variable Definition:** Define and store strings and numbers.
*   **Console Output:** Print messages or dialogue to the console.
*   **Variable Interpolation:** Use variables directly within strings.
*   **Comments:** Add comments to your scripts for clarity.
*   **Conditional Logic:** Use `if/else/end` blocks to control script flow.
*   **Loops:** Repeat blocks of code a specific number of times.
*   **Cutscenes:** Define and play non-interactive sequences.
*   **Dialogs:** Create interactive conversations with player choices.
*   **Quests:** Define and track the state of quests.
*   **Character Stats:** Manipulate character attributes like health and strength.
*   **Character Skills:** Grant and revoke character skills.
*   **Inventory Management:** Give and take items from the player.
*   **Combat System:** A basic combat system with attack commands.
*   **Functions and Events:** Reusable blocks of code and event-driven scripting.
*   **Randomization:** Generate random numbers for loot drops, damage calculation, etc.
*   **Sound and Music:** Play sound effects and background music.
*   **Multiplayer:** A client-server model for networked gameplay.

## Syntax

### Comments
Lines starting with `#` are ignored.
```ldscript
# This is a comment.
```

### Defining Variables
Use the `define ... as ...` keywords.
```ldscript
define playerName as "Valerius"
define startingHealth as 100
```

### Printing Output
Use the `say` command. To use a variable, wrap its name in curly braces `{}`.
```ldscript
say "Welcome, {playerName}! You have {startingHealth} health."
```

### Conditional Logic
Use `if`, `else`, and `end` to control which commands are executed.
```ldscript
if {playerHealth} <= 0
    say "You have been defeated."
else
    say "The battle continues."
end
```

### Loops
Use `loop ... times` and `end` to repeat actions.
```ldscript
loop 3 times
    say "A goblin appears!"
end
```

### Cutscenes
Define a reusable, non-interactive sequence of commands with `cutscene` and `end cutscene`.
```ldscript
cutscene intro
    say "The sun rises over the village."
    say "A new day has begun."
end cutscene

# To play the cutscene later
play cutscene intro
```

### Interactive Dialogs
Create conversations with player choices. Use `dialog` to define the conversation, `say` for NPC lines, and `option` for player choices. Each `option` has its own command block that ends with `end option`.
```ldscript
dialog merchant_greet
    say "Welcome to my shop!"
    option "I'd like to see your wares."
        say "Right this way..."
        # ... more script ...
    end option
    option "I'm just browsing."
        say "Let me know if you need anything."
    end option
end dialog

# To start the conversation
start dialog merchant_greet
```

### Quest Management
Define and track quests. Quests have an ID, a name, and properties like `description` and `state`.
```ldscript
quest find_sword "Find the Legendary Sword"
    description "A sword is rumored to be in the dark cave."
    state inactive
end quest

# Check a quest's state
if quest find_sword is inactive
    say "You have not yet started the quest."
end

# Update a quest's state
set quest find_sword to active
```

### Character Stats
Manage numerical attributes for the player character. Stats are stored as variables and can be used in `say` commands and `if` conditions.

- `set stat <name> to <value>`: Sets a stat to a specific value.
- `increase stat <name> by <value>`: Increases a stat by a certain amount.
- `decrease stat <name> by <value>`: Decreases a stat by a certain amount.

```ldscript
set stat health to 100
increase stat strength by 5
say "Your strength is now {strength}."
```

### Character Skills
Grant or revoke skills. Skills are simple flags that can be checked in conditions.

- `learn skill <name>`: Adds a skill to the character.
- `forget skill <name>`: Removes a skill from the character.
- `if has skill <name>`: Checks if the character possesses a skill.

```ldscript
learn skill stealth
if has skill stealth
    say "You can move silently."
end
```

### Inventory Management
The inventory system allows for creating detailed items and managing a player's inventory.

- `inventory`: Displays the player's current inventory.
- `give <count> <item_id>`: Adds one or more items to the player's inventory.
- `take <count> <item_id>`: Removes one or more items.
- `if has <item_id>` or `if has <count> <item_id>`: Checks if the player has a certain number of an item.

If `<count>` is omitted, it defaults to 1.

```ldscript
# The player is given a potion.
give 1 potion

# Check if the player has it.
if has potion
    say "You have a healing potion!"
end

# Show the inventory
inventory
```

### Vendors and Shopping
You can define vendors and their inventories, allowing players to buy and sell items.

#### Defining Items
Items are defined using the `item` block. They can have properties like a `name`, `description`, and `price`.
```ldscript
item sword
    name "Iron Sword"
    description "A basic but reliable sword."
    price 100
end item
```

#### Creating a Vendor
A vendor is an `entity` with an `inventory` stat. The inventory is a comma-separated string of item IDs that the vendor sells.
```ldscript
entity blacksmith
    stat name "Bob the Blacksmith"
    stat inventory "sword,shield"
end entity
```

#### Shopping Commands
- `shop <vendor_id>`: Displays the items a vendor has for sale.
- `buy <count> <item_id> from <vendor_id>`: Buys an item from a vendor.
- `sell <count> <item_id> to <vendor_id>`: Sells an item to a vendor.

```ldscript
# Show what the blacksmith is selling
shop blacksmith

# Buy a sword
buy 1 sword from blacksmith

# Sell a potion
sell 1 potion to blacksmith
```

### Defining Entities
Define game entities like the player or enemies using the `entity` block. Each entity can have its own set of stats.
```ldscript
entity player
    stat health 100
    stat strength 10
end entity

entity goblin
    stat health 30
    stat strength 5
end entity
```

### Combat
Use the `attack` command to make one entity attack another. The damage is calculated based on the attacker's strength.
```ldscript
attack player on goblin
```

### Randomization
Generate a random number and store it in a variable.
```ldscript
random damage from 1 to 10
say "You deal {damage} damage!"
```

### Functions and Events
Define reusable blocks of code with `function` and call them with `call`.
```ldscript
function heal_player
    increase stat health by 10
    say "You feel refreshed. Your health is now {player.health}."
end function

call heal_player
```

Define event handlers that trigger on specific game events. The `on death` event is triggered when an entity's health reaches 0.
```ldscript
on death
    say "{last_death} has been defeated."
end event

# This will trigger the 'on death' event if the goblin's health drops to 0.
attack player on goblin
```

### Sound and Music
Play sound effects and background music. You'll need to have the `pygame` library installed (`pip install pygame`).
```ldscript
play_sound "sounds/sword_swing.wav"
play_music "music/battle_theme.mp3"
```

### Multiplayer
ldscript now supports a basic client-server multiplayer model. One player acts as the "host" (the server), and other players connect as "clients". The host is the single source of truth for the game state.

When a client performs an action that changes the game (like attacking a monster), it sends the command to the host. The host executes the command and then broadcasts the new, updated game state to all connected clients.

#### `player_template` Entity
To support multiplayer, your script should define an entity named `player_template`. This entity is used as a blueprint by the server to create a new player entity every time a new client connects.

```ldscript
entity player_template
    stat health 100
    stat strength 10
end entity
```

#### `local_player` Variable
When writing scripts for multiplayer, you can use the special `local_player` variable. This variable automatically resolves to the unique ID of the player running the command. This is essential for commands like `attack` where you need to specify who is performing the action.

```ldscript
# When a client runs this, 'local_player' becomes their unique ID (e.g., 'player_2')
attack local_player on goblin
```

## Usage

To run an ldscript file, you need Python 3 installed. Use the `ldscript_interpreter.py` script.

**Single Player:**
```bash
python ldscript_interpreter.py path/to/your/script.ld
```

**Multiplayer Host:**
To host a game, use the `--host` flag. This will start a server on the default IP (127.0.0.1) and port (65432).
```bash
python ldscript_interpreter.py path/to/your/script.ld --host
```

**Multiplayer Client:**
To connect to a host, use the `--connect` flag followed by the host's IP address.
```bash
python ldscript_interpreter.py path/to/your/script.ld --connect 127.0.0.1
```

### Full Examples

Here are some examples that tie all the features together:
- `main.ld`: A general example showing many features.
- `vendor_example.ld`: A demonstration of the vendor and shopping system.

#### `main.ld`
```ldscript
# --- ITEM DEFINITIONS ---
# Defines items with their properties.
item potion
    name "Health Potion"
    description "Restores 20 health."
    price 20
end item

item goblin_axe
    name "Goblin Axe"
    description "A crude but sharp axe."
    price 35
end item

item rare_ore
    name "Glimmering Ore"
    description "A rare ore needed by the blacksmith."
end item

# --- QUEST DEFINITION ---
# Defines the main quest for the game.
quest get_rare_ore "The Glimmering Ore"
    description "Fetch a piece of Glimmering Ore from the Crystal Cave for the blacksmith."
    state inactive
end quest

# --- ENTITY DEFINITIONS ---
# Template for new players who connect to the server.
entity player_template
    stat health 100
    stat strength 10
end entity

# The host player's entity, required to exist.
entity player_1
    stat health 100
    stat strength 10
end entity

# The blacksmith NPC, who is also a vendor.
entity blacksmith
    stat name "Borin"
    stat inventory "potion" # Items the vendor sells.
end entity

# The monster in the cave, a shared entity for all players.
entity golem
    stat health 80
    stat strength 15
end entity

# --- FUNCTION DEFINITIONS ---
# A function for the Golem's turn in combat.
function golem_turn
    if golem.health > 0
        say "The Crystal Golem swings its heavy fists!"
        # The target is the player who last attacked it.
        attack golem on {last_attacker}
        play_sound "sounds/dragon_roar.wav" # Using existing sound for demo
        say "{last_attacker}'s health is now {local_player.health}."
    end
end

# --- EVENT HANDLER ---
# This event triggers when any entity's health reaches 0.
on death
    if last_death == "golem"
        say "The Crystal Golem shatters into a thousand pieces!"
        say "You see a chunk of Glimmering Ore in the rubble."
        play_music "music/victory_fanfare.mp3"
        give 1 rare_ore
        set quest get_rare_ore to completed
    else
        # Check if a player died
        if last_death == "player_1" or last_death == "player_2"
            say "You have been defeated... The world fades to black."
            play_music "music/game_over.mp3"
        end
    end
end event

# --- DIALOG DEFINITIONS ---
# Main dialog with the blacksmith.
dialog blacksmith_talk
    say "---"
    say "{blacksmith.name} the blacksmith looks at you. 'What do you need?'"
    
    option "I'm looking for work."
        if quest get_rare_ore is inactive
            say "'I need a special ore from the Crystal Cave to the north,' he says."
            say "'It's guarded by a Golem. Bring me a piece and I'll reward you.'"
            set quest get_rare_ore to active
            say "Quest Started: The Glimmering Ore"
        else
            say "'You're already on the job! Get me that ore!'"
        end
        start dialog blacksmith_talk # Return to the main dialog
    end option

    option "I have the ore you wanted."
        if quest get_rare_ore is completed and has rare_ore
            say "'You got it! Amazing!' He takes the ore from you."
            take 1 rare_ore
            say "He hands you a hefty pouch of gold."
            increase stat gold by 100
            say "Your gold is now {gold}."
            say "'As promised, let me teach you a thing or two...'"
            learn skill blacksmithing
            say "You have learned the 'blacksmithing' skill!"
        else
            say "'You don't have it! Stop wasting my time.'"
        end
        start dialog blacksmith_talk
    end option

    option "I'd like to trade."
        # Nested dialog for the shop
        dialog shop_menu
            shop blacksmith
            say "What would you like to do?"
            option "Buy a potion"
                buy 1 potion from blacksmith
                start dialog shop_menu
            end option
            option "Sell my goblin axe"
                if has goblin_axe
                    sell 1 goblin_axe to blacksmith
                else
                    say "You don't have a goblin axe to sell."
                end
                start dialog shop_menu
            end option
            option "Nevermind"
                start dialog blacksmith_talk
            end option
        end dialog
        start dialog shop_menu
    end option

    option "Leave."
        say "You leave the blacksmith's shop."
    end option
end dialog

# Main game script that ties everything together.
# Use 'import' to include definitions from other files.
import "definitions.ld"
import "dialogs.ld"

# --- GAME SETUP ---
# Use 'define' to create a variable.
define playerName as "Hero"
# Use 'set stat' to initialize a player variable.
set stat gold to 50
give 1 goblin_axe # Give starting item.

# --- INTRO CUTSCENE ---
cutscene intro
    say "Your name is {playerName}, a traveler seeking fortune."
    say "You arrive at a small village with a renowned blacksmith."
end cutscene

play_music "music/battle_theme.mp3" # Using for ambient music
play cutscene intro

say "---"
say "Welcome, {local_player}! Your adventure begins." # Uses local_player for multiplayer context.
say "You have {gold} gold."
inventory # Display starting inventory.

# --- START THE MAIN INTERACTION ---
start dialog blacksmith_talk

# --- THE JOURNEY & BATTLE (if quest was accepted) ---
if quest get_rare_ore is active
    say "You head north towards the Crystal Cave."
    
    # Use 'loop' and 'random' to simulate a small event on the journey.
    loop 1 times
        random luck from 1 to 2
        if {luck} == 1
            say "On the path, you find a lost Health Potion!"
            give 1 potion
        end
    end
    
    say "You enter the cave and see the Crystal Golem!"
    
    # Main combat loop
    loop 10 times
        if golem.health <= 0 or player_1.health <= 0 # Check host health as a baseline
            break # Exit the loop if battle is over.
        end

        say "---"
        say "Your turn! Golem HP: {golem.health}, Your HP: {local_player.health}"
        say "You attack the golem!"
        # Any connected player can attack the shared golem.
        define last_attacker as "{local_player}" # Set a variable for the golem's target
        attack local_player on golem
        play_sound "sounds/sword_swing.wav"
        
        # Golem's turn
        call golem_turn
    end
end

# --- POST-BATTLE & SKILL DEMO ---
if has skill blacksmithing
    say "---"
    say "You feel you have learned all you can from the blacksmith."
    forget skill blacksmithing # Demonstrate forgetting a skill.
    
    if has skill blacksmithing
        say "You are still a blacksmith."
    else
        say "You have forgotten the ways of the forge."
    end
end

say "---"
say "Your journey in this small village is over. Thank you for playing!"
```
