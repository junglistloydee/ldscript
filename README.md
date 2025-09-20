# ldscript

ldscript is a lightweight, natural-language scripting language designed for embedding simple game logic into Python-based games, with a focus on RPG-style mechanics.

The goal is to provide a syntax that is easy for game designers and writers to read and use without needing deep programming knowledge.

## Features

*   **Simple Syntax:** Commands are designed to be read like plain English.
*   **Variable Definition:** Define and store strings and numbers.
*   **Console Output:** Print messages or dialogue to the console.
*   **Variable Interpolation:** Use variables directly within strings.
*   **Comments:** Add comments to your scripts for clarity.

## Syntax

ldscript follows a few simple rules.

### Comments

Lines starting with `#` are ignored.

```ldscript
# This is a comment.
```

### Defining Variables

Use the `define ... as ...` keywords. The interpreter will automatically detect if the value is a number or a string.

```ldscript
define playerName as "Valerius"
define startingHealth as 100
```

### Printing Output

Use the `say` command. To use a variable inside a `say` command, wrap its name in curly braces `{}`.

```ldscript
say "A new hero has arrived."
say "Welcome, {playerName}! You have {startingHealth} health."
```

## Usage

To run an ldscript file, you need Python 3 installed. Use the `ldscript_interpreter.py` script and provide the path to your `.ld` file as an argument.

```bash
python ldscript_interpreter.py path/to/your/script.ld
```

### Example

Given a file `main.ld`:

```ldscript
# main.ld

define playerName as "Kael"
define playerHealth as 100

say "Welcome, {playerName}."
say "You start with {playerHealth} health."
```

Running the interpreter will produce the following output:

```
Welcome, Kael.
You start with 100 health.
```
