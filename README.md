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
Give items to or take items from the player.

- `give <count> <item_name>`: Adds one or more items to the player's inventory.
- `take <count> <item_name>`: Removes one or more items.
- `if has <item_name>` or `if has <count> <item_name>`: Checks if the player has a certain number of an item.

If `<count>` is omitted, it defaults to 1.

```ldscript
give 5 health_potion
give key
take 2 health_potion

if has key
    say "You can open the door."
end
```

## Usage

To run an ldscript file, you need Python 3 installed. Use the `ldscript_interpreter.py` script and provide the path to your `.ld` file as an argument.

```bash
python ldscript_interpreter.py path/to/your/script.ld
```

### Full Example (`main.ld`)

Here is an example that ties all the features together:
```ldscript
# ldscript example demonstrating all features

# Define variables and stats
define playerName as "Alex"
define npcName as "the old man"
set stat health to 100

# Define a quest
quest find_amulet "The Lost Amulet"
    description "Find the Old Man's lost amulet."
    state inactive
end quest

# Define a cutscene for the intro
cutscene game_intro
    say "In a quiet village, a new story begins."
    say "{playerName} is looking for an adventure with {health} HP."
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
            say "{npcName}: 'Please, take this for your troubles.'"
            give 50 gold
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
    if has 50 gold
        say "You received a reward of 50 gold."
    end
elif quest find_amulet is active
    say "You are still on the quest to find the amulet."
else
    say "You did not accept the quest."
end
```
