import re
import os
import sys

class LdParser:
    """
    Parses a .ld file and transforms its contents into a data structure
    that the visual editor can understand and load.
    """
    def __init__(self):
        self.entities = {}
        self.items = {}
        self.quests = {}
        self.functions = {}
        self.dialogs = {}
        self.variables = {}  # Needed for _evaluate_expression

    def parse(self, filepath):
        """
        Main entry point for parsing a .ld file.
        """
        try:
            abs_filepath = os.path.abspath(filepath)
            initial_dir = os.path.dirname(abs_filepath)
            with open(abs_filepath, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            processed_lines = self._preprocess_imports(lines, initial_dir, set([abs_filepath]))
            self._parse_toplevel(processed_lines)

            # Convert the raw ASTs into the editor's node format
            converted_functions = {
                func_id: {
                    "type": "function", "id": func_id,
                    "nodes": self._convert_ast_to_nodes(func_ast)
                } for func_id, func_ast in self.functions.items()
            }
            converted_dialogs = {
                dialog_id: {
                    "type": "dialog", "id": dialog_id,
                    "nodes": self._convert_ast_to_nodes(dialog_block)
                } for dialog_id, dialog_block in self.dialogs.items()
            }

            return {
                "entities": self.entities,
                "items": self.items,
                "quests": self.quests,
                "functions": converted_functions,
                "dialogs": converted_dialogs,
            }
        except (FileNotFoundError, SyntaxError) as e:
            # Re-raise to be handled by the caller in the editor
            raise e

    def _preprocess_imports(self, lines, current_dir, processed_files):
        final_lines = []
        for line in lines:
            match_import = re.match(r'import "([^"]+)"', line)
            if match_import:
                relative_path = match_import.group(1)
                import_path = os.path.abspath(os.path.join(current_dir, relative_path))
                if import_path in processed_files: continue
                processed_files.add(import_path)
                try:
                    with open(import_path, 'r') as f:
                        imported_content = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
                    new_dir = os.path.dirname(import_path)
                    final_lines.extend(self._preprocess_imports(imported_content, new_dir, processed_files))
                except FileNotFoundError:
                    raise FileNotFoundError(f"Imported file not found: {import_path}")
            else:
                final_lines.append(line)
        return final_lines

    def _parse_toplevel(self, lines):
        """
        Parses only the top-level definitions (entity, item, quest, function, dialog).
        """
        i = 0
        while i < len(lines):
            line = lines[i]

            match_entity = re.match(r'entity\s+(\w+)', line)
            if match_entity:
                name = match_entity.group(1)
                block, i = self._parse_entity_block(lines, i + 1)
                self.entities[name] = {"stats": block}
                continue

            match_item = re.match(r'item\s+(\w+)', line)
            if match_item:
                name = match_item.group(1)
                block, i = self._parse_item_block(lines, i + 1)
                self.items[name] = block
                continue

            match_quest = re.match(r'quest\s+(\w+)\s+"([^"]*)"', line)
            if match_quest:
                quest_id, quest_name = match_quest.groups()
                props, i = self._parse_quest_block(lines, i + 1)
                self.quests[quest_id] = {'id': quest_id, 'name': quest_name, **props}
                continue

            match_func = re.match(r'function\s+(\w+)', line)
            if match_func:
                name = match_func.group(1)
                block, i = self._parse_block(lines, i + 1, end_keywords=['end function'])
                self.functions[name] = block
                continue

            match_dialog = re.match(r'dialog\s+(\w+)', line)
            if match_dialog:
                name = match_dialog.group(1)
                block, i = self._parse_dialog_block(lines, i + 1)
                self.dialogs[name] = block
                continue

            i += 1 # Move to the next line if no top-level definition is found

    def _parse_block(self, lines, index, end_keywords):
        """
        Generic block parser that creates a raw AST for function bodies, if-blocks, etc.
        """
        ast = []
        i = index
        while i < len(lines):
            line = lines[i]
            if line in end_keywords:
                return ast, i + 1

            match_if = re.match(r'if\s+(.*)', line)
            if match_if:
                condition = match_if.group(1).strip()
                then_block, then_end_i = self._parse_block(lines, i + 1, end_keywords=['else', 'end'])

                else_block = []
                # Check if the block ended with 'else'
                if lines[then_end_i - 1] == 'else':
                    else_block, else_end_i = self._parse_block(lines, then_end_i, end_keywords=['end'])
                    i = else_end_i
                else:
                    i = then_end_i

                ast.append({'type': 'if', 'condition': condition, 'then_block': then_block, 'else_block': else_block})
                continue

            match_say = re.match(r'say\s+(.*)', line)
            if match_say:
                ast.append({'type': 'say', 'text': match_say.group(1).strip()})
                i += 1; continue

            match_set_quest = re.match(r'set\s+quest\s+(\w+)\s+to\s+(\w+)', line)
            if match_set_quest:
                quest_id, state = match_set_quest.groups()
                ast.append({'type': 'set_quest', 'quest_id': quest_id, 'state': state})
                i += 1; continue

            match_give = re.match(r'give\s+(?:(\d+)\s+)?(\w+)', line)
            if match_give:
                count, item_id = match_give.groups()
                ast.append({'type': 'give', 'item_id': item_id, 'count': count or "1"})
                i += 1; continue

            match_take = re.match(r'take\s+(?:(\d+)\s+)?(\w+)', line)
            if match_take:
                count, item_id = match_take.groups()
                ast.append({'type': 'take', 'item_id': item_id, 'count': count or "1"})
                i += 1; continue

            match_call = re.match(r'call\s+(\w+)', line)
            if match_call:
                ast.append({'type': 'call_function', 'name': match_call.group(1)})
                i += 1; continue

            # If no command is matched, move to the next line
            i += 1

        raise SyntaxError(f"Expected one of '{end_keywords}' but reached end of file.")

    def _parse_dialog_block(self, lines, index):
        """
        Parses a dialog block, which can contain any regular command plus 'option' blocks.
        """
        ast = []
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end dialog':
                return ast, i + 1

            # --- Standard commands from _parse_block ---
            match_if = re.match(r'if\s+(.*)', line)
            if match_if:
                condition = match_if.group(1).strip()
                then_block, then_end_i = self._parse_block(lines, i + 1, end_keywords=['else', 'end'])
                else_block = []
                if lines[then_end_i - 1] == 'else':
                    else_block, else_end_i = self._parse_block(lines, then_end_i, end_keywords=['end'])
                    i = else_end_i
                else:
                    i = then_end_i
                ast.append({'type': 'if', 'condition': condition, 'then_block': then_block, 'else_block': else_block})
                continue

            match_say = re.match(r'say\s+(.*)', line)
            if match_say:
                ast.append({'type': 'say', 'text': match_say.group(1).strip()})
                i += 1; continue

            match_set_quest = re.match(r'set\s+quest\s+(\w+)\s+to\s+(\w+)', line)
            if match_set_quest:
                quest_id, state = match_set_quest.groups()
                ast.append({'type': 'set_quest', 'quest_id': quest_id, 'state': state})
                i += 1; continue

            match_give = re.match(r'give\s+(?:(\d+)\s+)?(\w+)', line)
            if match_give:
                count, item_id = match_give.groups()
                ast.append({'type': 'give', 'item_id': item_id, 'count': count or "1"})
                i += 1; continue

            match_take = re.match(r'take\s+(?:(\d+)\s+)?(\w+)', line)
            if match_take:
                count, item_id = match_take.groups()
                ast.append({'type': 'take', 'item_id': item_id, 'count': count or "1"})
                i += 1; continue

            match_call = re.match(r'call\s+(\w+)', line)
            if match_call:
                ast.append({'type': 'call_function', 'name': match_call.group(1)})
                i += 1; continue

            # --- Dialog-specific command ---
            match_option = re.match(r'option\s+("[^"]*")', line)
            if match_option:
                option_text = match_option.group(1)[1:-1]
                # The inside of an option is a standard block
                option_block, end_i = self._parse_block(lines, i + 1, end_keywords=['end option'])
                ast.append({'type': 'option', 'text': option_text, 'block': option_block})
                i = end_i
                continue

            # If no command is matched, it's a syntax error
            raise SyntaxError(f"Invalid command in dialog block: {line}")

        raise SyntaxError("Expected 'end dialog' but reached end of file.")

    def _convert_ast_to_nodes(self, raw_ast):
        """
        Recursively converts a raw AST from _parse_block into the
        list-of-nodes format the editor expects.
        """
        nodes = []
        for command in raw_ast:
            node_type = command.get('type')
            # Most command types map directly
            new_node = command.copy()

            if node_type == 'if':
                new_node['nodes'] = self._convert_ast_to_nodes(command.get('then_block', []))
                if command.get('else_block'):
                    new_node['nodes'].append({'type': 'else_marker'})
                    new_node['nodes'].extend(self._convert_ast_to_nodes(command.get('else_block')))
                del new_node['then_block']
                del new_node['else_block']

            elif node_type == 'option':
                new_node['nodes'] = self._convert_ast_to_nodes(command.get('block', []))
                del new_node['block']

            # Strip quotes from 'say' text
            elif node_type == 'say':
                text = new_node.get('text', "")
                if text.startswith('"') and text.endswith('"'):
                    new_node['text'] = text[1:-1]

            nodes.append(new_node)
        return nodes


    def _parse_entity_block(self, lines, index):
        stats = {}
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end entity': return stats, i + 1
            match_stat = re.match(r'stat\s+(\w+)\s+(.*)', line)
            if match_stat:
                name, value = match_stat.groups()
                stats[name] = self._evaluate_expression(value)
            else: raise SyntaxError(f"Invalid line in entity definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end entity' but reached end of file.")

    def _parse_item_block(self, lines, index):
        properties = {}
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end item': return properties, i + 1
            match_prop = re.match(r'(\w+)\s+(.*)', line)
            if match_prop:
                key, value = match_prop.groups()
                properties[key] = self._evaluate_expression(value)
            else: raise SyntaxError(f"Invalid property line in item definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end item' but reached end of file.")

    def _parse_quest_block(self, lines, index):
        properties = {}
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end quest': return properties, i + 1
            match_prop = re.match(r'(\w+)\s+(.*)', line)
            if match_prop:
                key, value = match_prop.groups()
                if value.startswith('"') and value.endswith('"'):
                    properties[key] = value[1:-1]
                else:
                    properties[key] = value
            else: raise SyntaxError(f"Invalid property line in quest definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end quest' but reached end of file.")

    def _evaluate_expression(self, expr_str):
        expr_str = str(expr_str).strip()
        if expr_str.startswith('"') and expr_str.endswith('"'):
            return expr_str[1:-1]
        return expr_str
