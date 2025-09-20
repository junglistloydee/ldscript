import re
import sys

class Interpreter:
    """
    An interpreter for the ldscript language, featuring block-based parsing
    to support control structures like conditionals and loops.
    """
    def __init__(self):
        self.variables = {}

    def run_from_file(self, filepath):
        """Loads, parses, and executes an ldscript file."""
        try:
            with open(filepath, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            ast, _ = self._parse(lines)
            self._execute_block(ast)

        except FileNotFoundError:
            print(f"Error: File not found at '{filepath}'")
            sys.exit(1)
        except SyntaxError as e:
            print(f"Syntax Error: {e}", file=sys.stderr)
            sys.exit(1)

    def _parse(self, lines, index=0, end_keywords=None):
        """
        Parses a list of lines into a nested block structure (AST).
        """
        ast = []
        i = index
        while i < len(lines):
            line = lines[i]

            if end_keywords and line in end_keywords:
                return ast, i

            if line == 'break':
                ast.append({'type': 'break'})
                i += 1
                continue

            if line == 'continue':
                ast.append({'type': 'continue'})
                i += 1
                continue

            match_if = re.match(r'if (.*)', line)
            if match_if:
                condition = match_if.group(1).strip()
                then_block, then_end_index = self._parse(lines, i + 1, end_keywords=['else', 'end'])
                else_block = []
                if then_end_index < len(lines) and lines[then_end_index] == 'else':
                    else_block, else_end_index = self._parse(lines, then_end_index + 1, end_keywords=['end'])
                    i = else_end_index
                else:
                    i = then_end_index
                ast.append({'type': 'if', 'condition': condition, 'then_block': then_block, 'else_block': else_block})
                i += 1
                continue

            match_loop = re.match(r'loop (.*) times', line)
            if match_loop:
                count_expr = match_loop.group(1).strip()
                loop_block, loop_end_index = self._parse(lines, i + 1, end_keywords=['end'])
                i = loop_end_index
                ast.append({'type': 'loop', 'count_expr': count_expr, 'block': loop_block})
                i += 1
                continue

            match_say = re.match(r'say (.*)', line)
            if match_say:
                ast.append({'type': 'say', 'value': match_say.group(1).strip()})
                i += 1
                continue

            match_define = re.match(r'define (\w+) as (.*)', line)
            if match_define:
                var_name, var_value = match_define.groups()
                ast.append({'type': 'define', 'name': var_name.strip(), 'value': var_value.strip()})
                i += 1
                continue

            if line in ['else', 'end']:
                raise SyntaxError(f"Unexpected '{line}' keyword.")
            raise SyntaxError(f"Unknown command: {line}")

        if end_keywords:
            raise SyntaxError(f"Expected one of '{end_keywords}' but reached end of file.")
        return ast, i

    def _execute_block(self, block):
        """Executes a block of commands, handling control flow signals."""
        for command in block:
            signal = self._execute_command(command)
            if signal in ['break', 'continue']:
                return signal  # Propagate signal up
        return None  # No signal

    def _execute_command(self, command):
        """Dispatches a command and returns any control flow signal."""
        command_type = command['type']
        if command_type == 'say':
            self._execute_say(command['value'])
        elif command_type == 'define':
            self._execute_define(command['name'], command['value'])
        elif command_type == 'if':
            return self._execute_if(command)
        elif command_type == 'loop':
            return self._execute_loop(command)
        elif command_type == 'break':
            return 'break'
        elif command_type == 'continue':
            return 'continue'
        return None

    def _execute_loop(self, loop_command):
        """Executes a 'loop' command, handling break and continue."""
        count_val = self._evaluate_expression(loop_command['count_expr'])
        try:
            count = int(count_val)
        except (ValueError, TypeError):
            print(f"Error: Loop count must be an integer, but got '{count_val}'.", file=sys.stderr)
            return None

        # Introduce a variable for loop iteration counting
        self.variables['loop_index'] = 0
        for i in range(count):
            self.variables['loop_index'] = i
            signal = self._execute_block(loop_command['block'])
            if signal == 'break':
                break  # Exit the loop
            if signal == 'continue':
                continue  # Skip to the next iteration

        # Clean up loop variable
        if 'loop_index' in self.variables:
            del self.variables['loop_index']

        return None  # Loop consumes the signal

    def _execute_if(self, if_command):
        """Executes an 'if' command, propagating signals."""
        if self._evaluate_condition(if_command['condition']):
            return self._execute_block(if_command['then_block'])
        elif if_command['else_block']:
            return self._execute_block(if_command['else_block'])
        return None

    def _execute_say(self, message):
        def replace_var(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, f"{{{var_name}}}"))
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
        interpolated_message = re.sub(r'\{(\w+)\}', replace_var, message)
        print(interpolated_message)

    def _execute_define(self, name, value_str):
        self.variables[name] = self._evaluate_expression(value_str)

    def _evaluate_expression(self, expr_str):
        expr_str = expr_str.strip()
        if expr_str.startswith('"') and expr_str.endswith('"'):
            return expr_str[1:-1]
        try:
            return int(expr_str)
        except ValueError:
            try:
                return float(expr_str)
            except ValueError:
                pass
        if expr_str in self.variables:
            return self.variables[expr_str]
        return expr_str

    def _evaluate_condition(self, condition_str):
        match = re.match(r'(.+?)\s*(>=|<=|==|!=|>|<)\s*(.+)', condition_str)
        if not match:
            value = self._evaluate_expression(condition_str)
            if isinstance(value, str):
                return value.lower() in ['true', 'yes', 'on']
            return bool(value)

        left_str, op, right_str = match.groups()
        left_val = self._evaluate_expression(left_str)
        right_val = self._evaluate_expression(right_str)

        try:
            num_left = float(left_val)
            num_right = float(right_val)
            if op == '==': return num_left == num_right
            if op == '!=': return num_left != num_right
            if op == '>': return num_left > num_right
            if op == '<': return num_left < num_right
            if op == '>=': return num_left >= num_right
            if op == '<=': return num_left <= num_right
        except (ValueError, TypeError):
            if op == '==': return str(left_val) == str(right_val)
            if op == '!=': return str(left_val) != str(right_val)
            return False
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python ldscript_interpreter.py <filepath.ld>")
        sys.exit(1)
    script_file = sys.argv[1]
    interpreter = Interpreter()
    interpreter.run_from_file(script_file)

if __name__ == "__main__":
    main()
