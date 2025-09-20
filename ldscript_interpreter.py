import re
import sys

class Interpreter:
    """
    An interpreter for the ldscript language, featuring block-based parsing
    to support control structures like conditionals and loops.
    """
    def __init__(self):
        self.variables = {}
        self.cutscenes = {}
        self.dialogs = {}
        self.quests = {}
        self.skills = []
        self.inventory = {}

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

            match_cutscene_def = re.match(r'cutscene (\w+)', line)
            if match_cutscene_def:
                name = match_cutscene_def.group(1)
                cutscene_block, end_index = self._parse(lines, i + 1, end_keywords=['end cutscene'])
                self.cutscenes[name] = cutscene_block
                i = end_index + 1
                continue

            match_play = re.match(r'play cutscene (\w+)', line)
            if match_play:
                name = match_play.group(1)
                ast.append({'type': 'play_cutscene', 'name': name})
                i += 1
                continue

            match_dialog_def = re.match(r'dialog (\w+)', line)
            if match_dialog_def:
                name = match_dialog_def.group(1)
                dialog_block, end_index = self._parse_dialog_block(lines, i + 1)
                self.dialogs[name] = dialog_block
                i = end_index + 1
                continue

            match_start_dialog = re.match(r'start dialog (\w+)', line)
            if match_start_dialog:
                name = match_start_dialog.group(1)
                ast.append({'type': 'start_dialog', 'name': name})
                i += 1
                continue

            match_quest_def = re.match(r'quest (\w+) "([^"]*)"', line)
            if match_quest_def:
                quest_id, quest_name = match_quest_def.groups()
                properties, end_index = self._parse_quest_block(lines, i + 1)
                self.quests[quest_id] = {'id': quest_id, 'name': quest_name, **properties}
                i = end_index + 1
                continue

            match_set_quest = re.match(r'set quest (\w+) to (\w+)', line)
            if match_set_quest:
                quest_id, new_state = match_set_quest.groups()
                ast.append({'type': 'set_quest', 'id': quest_id, 'state': new_state})
                i += 1
                continue

            match_set_stat = re.match(r'set stat (\w+) to (.*)', line)
            if match_set_stat:
                name, value = match_set_stat.groups()
                ast.append({'type': 'define', 'name': name.strip(), 'value': value.strip()})
                i += 1
                continue

            match_increase_stat = re.match(r'increase stat (\w+) by (.*)', line)
            if match_increase_stat:
                name, value = match_increase_stat.groups()
                ast.append({'type': 'increase_stat', 'name': name.strip(), 'value': value.strip()})
                i += 1
                continue

            match_decrease_stat = re.match(r'decrease stat (\w+) by (.*)', line)
            if match_decrease_stat:
                name, value = match_decrease_stat.groups()
                ast.append({'type': 'decrease_stat', 'name': name.strip(), 'value': value.strip()})
                i += 1
                continue

            match_learn_skill = re.match(r'learn skill (\w+)', line)
            if match_learn_skill:
                name = match_learn_skill.group(1)
                ast.append({'type': 'learn_skill', 'name': name})
                i += 1
                continue

            match_forget_skill = re.match(r'forget skill (\w+)', line)
            if match_forget_skill:
                name = match_forget_skill.group(1)
                ast.append({'type': 'forget_skill', 'name': name})
                i += 1
                continue

            match_give = re.match(r'give (?:(\d+)\s+)?(\w+)', line)
            if match_give:
                count, name = match_give.groups()
                ast.append({'type': 'give_item', 'name': name, 'count': count or "1"})
                i += 1
                continue

            match_take = re.match(r'take (?:(\d+)\s+)?(\w+)', line)
            if match_take:
                count, name = match_take.groups()
                ast.append({'type': 'take_item', 'name': name, 'count': count or "1"})
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

            if line in ['else', 'end', 'end cutscene', 'end dialog', 'end option', 'end quest']:
                # These keywords are handled by the block parsing logic, so they are unexpected here.
                raise SyntaxError(f"Unexpected '{line}' keyword.")
            raise SyntaxError(f"Unknown command: {line}")

        if end_keywords:
            raise SyntaxError(f"Expected one of '{end_keywords}' but reached end of file.")
        return ast, i

    def _parse_dialog_block(self, lines, index):
        """
        Parses the contents of a dialog block, separating initial 'say' commands
        from subsequent 'option' blocks.
        """
        say_nodes = []
        options = []
        i = index

        # First, parse all initial 'say' commands
        while i < len(lines):
            line = lines[i]
            if line == 'end dialog':
                return {'say_nodes': say_nodes, 'options': options}, i

            match_say = re.match(r'say (.*)', line)
            if match_say:
                say_nodes.append({'type': 'say', 'value': match_say.group(1).strip()})
                i += 1
            else:
                # The first non-'say' command must be an 'option'
                break

        # Now, parse 'option' blocks
        while i < len(lines):
            line = lines[i]
            if line == 'end dialog':
                return {'say_nodes': say_nodes, 'options': options}, i

            match_option = re.match(r'option ("[^"]*")', line)
            if not match_option:
                raise SyntaxError(f"Expected 'option' or 'end dialog' inside a dialog block, but got: {line}")

            option_text = match_option.group(1)[1:-1]  # Remove quotes
            option_block, end_index = self._parse(lines, i + 1, end_keywords=['end option'])
            options.append({'text': option_text, 'block': option_block})
            i = end_index + 1 # Skip past 'end option'

        raise SyntaxError("Expected 'end dialog' but reached end of file.")

    def _parse_quest_block(self, lines, index):
        """Parses the properties of a quest block."""
        properties = {}
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end quest':
                return properties, i

            match_prop = re.match(r'(\w+)\s+(.*)', line)
            if match_prop:
                key, value = match_prop.groups()
                # Simple evaluation for the value
                if value.startswith('"') and value.endswith('"'):
                    properties[key] = value[1:-1]
                else:
                    properties[key] = value
            else:
                raise SyntaxError(f"Invalid property line in quest definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end quest' but reached end of file.")

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
        elif command_type == 'play_cutscene':
            return self._execute_play_cutscene(command)
        elif command_type == 'start_dialog':
            return self._execute_start_dialog(command)
        elif command_type == 'set_quest':
            return self._execute_set_quest(command)
        elif command_type == 'increase_stat':
            return self._execute_increase_stat(command)
        elif command_type == 'decrease_stat':
            return self._execute_decrease_stat(command)
        elif command_type == 'learn_skill':
            return self._execute_learn_skill(command)
        elif command_type == 'forget_skill':
            return self._execute_forget_skill(command)
        elif command_type == 'give_item':
            return self._execute_give_item(command)
        elif command_type == 'take_item':
            return self._execute_take_item(command)
        elif command_type == 'break':
            return 'break'
        elif command_type == 'continue':
            return 'continue'
        return None

    def _execute_play_cutscene(self, command):
        """Executes a 'play cutscene' command."""
        name = command['name']
        if name in self.cutscenes:
            return self._execute_block(self.cutscenes[name])
        else:
            print(f"Error: Cutscene '{name}' not defined.", file=sys.stderr)
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

    def _execute_set_quest(self, command):
        """Executes a 'set quest' command."""
        quest_id = command['id']
        new_state = command['state']
        if quest_id in self.quests:
            self.quests[quest_id]['state'] = new_state
        else:
            print(f"Error: Quest '{quest_id}' not defined.", file=sys.stderr)
        return None

    def _execute_start_dialog(self, command):
        """Executes a 'start dialog' command."""
        name = command['name']
        if name not in self.dialogs:
            print(f"Error: Dialog '{name}' not defined.", file=sys.stderr)
            return None

        dialog = self.dialogs[name]

        # Execute all initial 'say' commands
        for say_command in dialog['say_nodes']:
            self._execute_command(say_command)

        # Present options to the player
        if not dialog['options']:
            return None  # No options to choose from

        print("\nChoose an option:")
        for i, option in enumerate(dialog['options']):
            print(f"  {i + 1}: {option['text']}")

        # Get player choice
        while True:
            try:
                choice = input("> ")
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(dialog['options']):
                    chosen_option = dialog['options'][choice_index]
                    return self._execute_block(chosen_option['block'])
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except (EOFError, KeyboardInterrupt):
                print("\nDialog cancelled.")
                return None

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

    def _execute_increase_stat(self, command):
        name = command['name']
        value_str = command['value']

        current_value = self.variables.get(name, 0)
        increase_by = self._evaluate_expression(value_str)

        try:
            self.variables[name] = float(current_value) + float(increase_by)
        except (ValueError, TypeError):
            print(f"Error: Stat '{name}' and value for increasing must be numeric.", file=sys.stderr)

        return None

    def _execute_decrease_stat(self, command):
        name = command['name']
        value_str = command['value']

        current_value = self.variables.get(name, 0)
        decrease_by = self._evaluate_expression(value_str)

        try:
            self.variables[name] = float(current_value) - float(decrease_by)
        except (ValueError, TypeError):
            print(f"Error: Stat '{name}' and value for decreasing must be numeric.", file=sys.stderr)

        return None

    def _execute_learn_skill(self, command):
        skill_name = command['name']
        if skill_name not in self.skills:
            self.skills.append(skill_name)
        return None

    def _execute_forget_skill(self, command):
        skill_name = command['name']
        if skill_name in self.skills:
            self.skills.remove(skill_name)
        return None

    def _execute_give_item(self, command):
        item_name = command['name']
        count = int(self._evaluate_expression(command['count']))

        if count <= 0:
            return None

        current_count = self.inventory.get(item_name, 0)
        self.inventory[item_name] = current_count + count
        return None

    def _execute_take_item(self, command):
        item_name = command['name']
        count = int(self._evaluate_expression(command['count']))

        if count <= 0:
            return None

        current_count = self.inventory.get(item_name, 0)

        if current_count >= count:
            self.inventory[item_name] = current_count - count
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
        else:
            print(f"Error: Not enough '{item_name}' to take. Have {current_count}, need {count}.", file=sys.stderr)

        return None

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
        # Check for skill condition, e.g., "has skill magic"
        match_skill = re.match(r'has skill (\w+)', condition_str)
        if match_skill:
            skill_name = match_skill.group(1)
            return skill_name in self.skills

        # Check for item condition, e.g., "has 5 potion" or "has key"
        match_item = re.match(r'has (?:(\d+)\s+)?(\w+)', condition_str)
        if match_item:
            count_str, item_name = match_item.groups()
            required_count = int(count_str) if count_str else 1
            return self.inventory.get(item_name, 0) >= required_count

        # Check for quest status condition, e.g., "quest find_sword is active"
        match_quest = re.match(r'quest (\w+) is (\w+)', condition_str)
        if match_quest:
            quest_id, expected_state = match_quest.groups()
            if quest_id in self.quests:
                return self.quests[quest_id].get('state') == expected_state
            return False

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
