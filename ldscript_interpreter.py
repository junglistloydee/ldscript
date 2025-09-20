import re
import sys

class Interpreter:
    """
    A basic interpreter for the ldscript language.
    It can define variables, print messages, and handle basic string interpolation.
    """
    def __init__(self):
        self.variables = {}

    def execute_from_file(self, filepath):
        """Reads and executes an ldscript file line by line."""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    self.parse_line(line.strip())
        except FileNotFoundError:
            print(f"Error: File not found at '{filepath}'")
            sys.exit(1)

    def parse_line(self, line):
        """Parses a single line of ldscript code."""
        # Ignore empty lines and comments
        if not line or line.startswith('#'):
            return

        # 'say' command: say "a message" or say variable
        match_say = re.match(r'say (.*)', line)
        if match_say:
            message = match_say.group(1).strip()
            self.execute_say(message)
            return

        # 'define' command: define <name> as <value>
        match_define = re.match(r'define (\w+) as (.*)', line)
        if match_define:
            var_name, var_value = match_define.groups()
            self.execute_define(var_name.strip(), var_value.strip())
            return

        # If no command is matched, we can add error handling later
        # For now, we'll just ignore it.
        # print(f"Syntax Error: Unknown command -> {line}")

    def execute_say(self, message):
        """Executes the 'say' command, handling variable interpolation."""
        def replace_var(match):
            var_name = match.group(1)
            # Return the variable's value, or the placeholder if not found
            return str(self.variables.get(var_name, f"{{{var_name}}}"))

        # Unquote the message if it's a string literal
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]

        # Perform variable interpolation
        interpolated_message = re.sub(r'\{(\w+)\}', replace_var, message)
        print(interpolated_message)

    def execute_define(self, name, value):
        """Executes the 'define' command, storing the variable."""
        # Check if the value is a string literal
        if value.startswith('"') and value.endswith('"'):
            self.variables[name] = value[1:-1]
        # Check if it's an integer
        elif value.isdigit():
            self.variables[name] = int(value)
        # Check if it's a float
        elif re.match(r'^-?\d+(\.\d+)?$', value):
            try:
                self.variables[name] = float(value)
            except ValueError:
                self.variables[name] = value # Fallback to string
        else:
            # If it's not a recognized format, store it as a string
            self.variables[name] = value

def main():
    """Main entry point for the interpreter script."""
    if len(sys.argv) != 2:
        print("Usage: python ldscript_interpreter.py <filepath.ld>")
        sys.exit(1)

    script_file = sys.argv[1]
    interpreter = Interpreter()
    interpreter.execute_from_file(script_file)

if __name__ == "__main__":
    main()
