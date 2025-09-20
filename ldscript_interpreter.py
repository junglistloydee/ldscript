import re
import sys
import random
import pygame
import os
import json
import time
from copy import deepcopy
from game_state import GameState
from network import Server, Client

STATE_MODIFYING_COMMANDS = {
    'define', 'increase_stat', 'decrease_stat',
    'learn_skill', 'forget_skill', 'give_item', 'take_item',
    'attack', 'random', 'set_quest'
}

class Interpreter:
    """
    An interpreter for the ldscript language, now with networking capabilities.
    """
    def __init__(self, mode='singleplayer', host=None, port=65432):
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except pygame.error:
            self.sound_enabled = False
            print("Warning: Pygame mixer could not be initialized. Sound will be disabled.", file=sys.stderr)

        self.game_state = GameState()
        self.cutscenes = {}
        self.dialogs = {}
        self.functions = {}
        self.events = {}

        self.mode = mode
        self.network = None
        self.player_id = 'player_1' if mode != 'client' else None # Host is player_1 by default
        self.client_player_map = {} # Maps client socket to player_id

        if self.mode == 'host':
            self.network = Server(
                host=host, port=port,
                on_receive=self._on_client_data,
                on_connect=self._on_client_connect,
                on_disconnect=self._on_client_disconnect
            )
        elif self.mode == 'client':
            self.network = Client(host=host, port=port, on_receive=self._on_server_data)

    def _on_client_connect(self, client_socket, addr):
        """Callback for when a new client connects to the server."""
        print(f"[Server] New client connected: {addr}")

        # Generate a new player ID
        new_player_id = f"player_{client_socket.fileno()}"
        self.client_player_map[client_socket] = new_player_id

        # Create a new entity for the player from the template
        if 'player_template' in self.game_state.entities:
            self.game_state.entities[new_player_id] = deepcopy(self.game_state.entities['player_template'])
            print(f"[Server] Created entity '{new_player_id}' for new client.")
        else:
            print("[Server] Warning: 'player_template' entity not found. Cannot create entity for new client.", file=sys.stderr)

        # Assign the ID to the client
        assign_id_message = json.dumps({'type': 'assign_id', 'id': new_player_id})
        self.network.send_to(client_socket, assign_id_message)

        # Broadcast the new state to all clients
        self.network.broadcast(json.dumps({'type': 'state_update', 'state': self.game_state.to_json()}))

    def _on_client_disconnect(self, client_socket):
        """Callback for when a client disconnects."""
        player_id = self.client_player_map.pop(client_socket, None)
        if player_id and player_id in self.game_state.entities:
            del self.game_state.entities[player_id]
            print(f"[Server] Removed entity for disconnected player: {player_id}")
            # Broadcast the state change
            self.network.broadcast(json.dumps({'type': 'state_update', 'state': self.game_state.to_json()}))

    def _on_client_data(self, client_socket, data):
        """Callback for the server to handle data from a client."""
        player_id = self.client_player_map.get(client_socket)
        if not player_id:
            return # Ignore data from unknown clients

        print(f"[Server] Received command from {player_id}: {data}")
        try:
            command = json.loads(data)
            self._execute_command(command) # Server executes the command authoritatively
        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON from client: {data}", file=sys.stderr)

    def _on_server_data(self, data):
        """Callback for the client to handle data from the server."""
        try:
            message = json.loads(data)
            msg_type = message.get('type')

            if msg_type == 'assign_id':
                self.player_id = message.get('id')
                print(f"[Client] Assigned player ID: {self.player_id}")
            elif msg_type == 'state_update':
                # print("[Client] Received state update from server.")
                self.game_state.from_json(message.get('state'))
            else:
                print(f"[Client] Received unknown message type: {msg_type}", file=sys.stderr)

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON from server: {data}", file=sys.stderr)

    def _resolve_placeholders(self, data):
        """Recursively replaces 'local_player' with the client's player_id."""
        if isinstance(data, dict):
            return {k: self._resolve_placeholders(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_placeholders(i) for i in data]
        elif isinstance(data, str):
            return data.replace('local_player', self.player_id or '')
        else:
            return data

    def run_from_file(self, filepath):
        try:
            abs_filepath = os.path.abspath(filepath)
            initial_dir = os.path.dirname(abs_filepath)
            with open(abs_filepath, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            processed_lines = self._preprocess_imports(lines, initial_dir, set([abs_filepath]))
            self.ast, _ = self._parse(processed_lines)
            if self.mode == 'client':
                if not self.network.connect(): return
            execution_thread = threading.Thread(target=self._execute_block, args=(self.ast,))
            execution_thread.daemon = True
            execution_thread.start()
        except FileNotFoundError:
            print(f"Error: File not found at '{filepath}'"); sys.exit(1)
        except SyntaxError as e:
            print(f"Syntax Error: {e}", file=sys.stderr); sys.exit(1)

    def _preprocess_imports(self, lines, current_dir, processed_files):
        # This function remains unchanged
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
                    print(f"Error: Imported file not found at '{import_path}'", file=sys.stderr); sys.exit(1)
            else:
                final_lines.append(line)
        return final_lines

    def _parse(self, lines, index=0, end_keywords=None):
        # This function remains unchanged
        ast = []
        i = index
        while i < len(lines):
            line = lines[i]
            if end_keywords and line in end_keywords: return ast, i
            if line in ['break', 'continue']:
                ast.append({'type': line}); i += 1; continue

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
                ast.append({'type': 'if', 'condition': condition, 'then_block': then_block, 'else_block': else_block}); i += 1; continue

            match_cutscene_def = re.match(r'cutscene (\w+)', line)
            if match_cutscene_def:
                name = match_cutscene_def.group(1)
                cutscene_block, end_index = self._parse(lines, i + 1, end_keywords=['end cutscene'])
                self.cutscenes[name] = cutscene_block; i = end_index + 1; continue

            match_play = re.match(r'play cutscene (\w+)', line)
            if match_play:
                ast.append({'type': 'play_cutscene', 'name': match_play.group(1)}); i += 1; continue

            match_function_def = re.match(r'function (\w+)', line)
            if match_function_def:
                name = match_function_def.group(1)
                function_block, end_index = self._parse(lines, i + 1, end_keywords=['end function'])
                self.functions[name] = function_block; i = end_index + 1; continue

            match_call = re.match(r'call (\w+)', line)
            if match_call:
                ast.append({'type': 'call_function', 'name': match_call.group(1)}); i += 1; continue

            match_on_event = re.match(r'on (\w+)', line)
            if match_on_event:
                name = match_on_event.group(1)
                event_block, end_index = self._parse(lines, i + 1, end_keywords=['end event'])
                self.events[name] = event_block; i = end_index + 1; continue

            match_dialog_def = re.match(r'dialog (\w+)', line)
            if match_dialog_def:
                name = match_dialog_def.group(1)
                dialog_block, end_index = self._parse_dialog_block(lines, i + 1)
                self.dialogs[name] = dialog_block; i = end_index + 1; continue

            match_start_dialog = re.match(r'start dialog (\w+)', line)
            if match_start_dialog:
                ast.append({'type': 'start_dialog', 'name': match_start_dialog.group(1)}); i += 1; continue

            match_entity_def = re.match(r'entity (\w+)', line)
            if match_entity_def:
                name = match_entity_def.group(1)
                entity_block, end_index = self._parse_entity_block(lines, i + 1)
                self.game_state.entities[name] = entity_block; i = end_index + 1; continue

            match_quest_def = re.match(r'quest (\w+) "([^"]*)"', line)
            if match_quest_def:
                quest_id, quest_name = match_quest_def.groups()
                properties, end_index = self._parse_quest_block(lines, i + 1)
                self.game_state.quests[quest_id] = {'id': quest_id, 'name': quest_name, **properties}; i = end_index + 1; continue

            match_set_quest = re.match(r'set quest (\w+) to (\w+)', line)
            if match_set_quest:
                quest_id, new_state = match_set_quest.groups()
                ast.append({'type': 'set_quest', 'id': quest_id, 'state': new_state}); i += 1; continue

            match_set_stat = re.match(r'set stat (\w+) to (.*)', line)
            if match_set_stat:
                name, value = match_set_stat.groups()
                ast.append({'type': 'define', 'name': name.strip(), 'value': value.strip()}); i += 1; continue

            match_increase_stat = re.match(r'increase stat (\w+) by (.*)', line)
            if match_increase_stat:
                name, value = match_increase_stat.groups()
                ast.append({'type': 'increase_stat', 'name': name.strip(), 'value': value.strip()}); i += 1; continue

            match_decrease_stat = re.match(r'decrease stat (\w+) by (.*)', line)
            if match_decrease_stat:
                name, value = match_decrease_stat.groups()
                ast.append({'type': 'decrease_stat', 'name': name.strip(), 'value': value.strip()}); i += 1; continue

            match_learn_skill = re.match(r'learn skill (\w+)', line)
            if match_learn_skill:
                ast.append({'type': 'learn_skill', 'name': match_learn_skill.group(1)}); i += 1; continue

            match_forget_skill = re.match(r'forget skill (\w+)', line)
            if match_forget_skill:
                ast.append({'type': 'forget_skill', 'name': match_forget_skill.group(1)}); i += 1; continue

            match_give = re.match(r'give (?:(\d+)\s+)?(\w+)', line)
            if match_give:
                count, name = match_give.groups()
                ast.append({'type': 'give_item', 'name': name, 'count': count or "1"}); i += 1; continue

            match_take = re.match(r'take (?:(\d+)\s+)?(\w+)', line)
            if match_take:
                count, name = match_take.groups()
                ast.append({'type': 'take_item', 'name': name, 'count': count or "1"}); i += 1; continue

            match_attack = re.match(r'attack (\w+) on (\w+)(?: with (\w+))?', line)
            if match_attack:
                attacker, target, weapon = match_attack.groups()
                ast.append({'type': 'attack', 'attacker': attacker, 'target': target, 'weapon': weapon}); i += 1; continue

            match_loop = re.match(r'loop (.*) times', line)
            if match_loop:
                count_expr = match_loop.group(1).strip()
                loop_block, loop_end_index = self._parse(lines, i + 1, end_keywords=['end'])
                i = loop_end_index
                ast.append({'type': 'loop', 'count_expr': count_expr, 'block': loop_block}); i += 1; continue

            match_say = re.match(r'say (.*)', line)
            if match_say:
                ast.append({'type': 'say', 'value': match_say.group(1).strip()}); i += 1; continue

            match_define = re.match(r'define (\w+) as (.*)', line)
            if match_define:
                var_name, var_value = match_define.groups()
                ast.append({'type': 'define', 'name': var_name.strip(), 'value': var_value.strip()}); i += 1; continue

            match_random = re.match(r'random (\w+) from (.*) to (.*)', line)
            if match_random:
                var_name, min_val, max_val = match_random.groups()
                ast.append({'type': 'random', 'name': var_name.strip(), 'min': min_val.strip(), 'max': max_val.strip()}); i += 1; continue

            match_play_sound = re.match(r'play_sound (.*)', line)
            if match_play_sound:
                ast.append({'type': 'play_sound', 'filepath': match_play_sound.group(1).strip()}); i += 1; continue

            match_play_music = re.match(r'play_music (.*)', line)
            if match_play_music:
                ast.append({'type': 'play_music', 'filepath': match_play_music.group(1).strip()}); i += 1; continue

            if line in ['else', 'end', 'end cutscene', 'end dialog', 'end option', 'end quest', 'end entity', 'end function', 'end event']:
                raise SyntaxError(f"Unexpected '{line}' keyword.")
            raise SyntaxError(f"Unknown command: {line}")
        if end_keywords:
            raise SyntaxError(f"Expected one of '{end_keywords}' but reached end of file.")
        return ast, i

    def _parse_dialog_block(self, lines, index):
        # This function remains unchanged
        say_nodes = []
        options = []
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end dialog': return {'say_nodes': say_nodes, 'options': options}, i
            match_say = re.match(r'say (.*)', line)
            if match_say:
                say_nodes.append({'type': 'say', 'value': match_say.group(1).strip()}); i += 1
            else: break
        while i < len(lines):
            line = lines[i]
            if line == 'end dialog': return {'say_nodes': say_nodes, 'options': options}, i
            match_option = re.match(r'option ("[^"]*")', line)
            if not match_option: raise SyntaxError(f"Expected 'option' or 'end dialog', but got: {line}")
            option_text = match_option.group(1)[1:-1]
            option_block, end_index = self._parse(lines, i + 1, end_keywords=['end option'])
            options.append({'text': option_text, 'block': option_block}); i = end_index + 1
        raise SyntaxError("Expected 'end dialog' but reached end of file.")

    def _parse_entity_block(self, lines, index):
        # This function remains unchanged
        stats = {}; i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end entity': return stats, i
            match_stat = re.match(r'stat (\w+) (.*)', line)
            if match_stat:
                name, value = match_stat.groups()
                stats[name] = self._evaluate_expression(value)
            else: raise SyntaxError(f"Invalid line in entity definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end entity' but reached end of file.")

    def _parse_quest_block(self, lines, index):
        # This function remains unchanged
        properties = {}; i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end quest': return properties, i
            match_prop = re.match(r'(\w+)\s+(.*)', line)
            if match_prop:
                key, value = match_prop.groups()
                properties[key] = value[1:-1] if value.startswith('"') and value.endswith('"') else value
            else: raise SyntaxError(f"Invalid property line in quest definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end quest' but reached end of file.")

    def _execute_block(self, block):
        for command in block:
            signal = self._execute_command(command)
            if signal in ['break', 'continue']: return signal
        return None

    def _execute_command(self, command):
        command_type = command['type']

        if self.mode == 'client' and command_type in STATE_MODIFYING_COMMANDS:
            resolved_command = self._resolve_placeholders(command)
            # print(f"[Client] Sending command to server: {resolved_command}")
            self.network.send(json.dumps(resolved_command))
            return None

        method_name = f'_execute_{command_type}'
        method = getattr(self, method_name, None)
        if not method: return None

        result = method(command)

        if self.mode == 'host' and command_type in STATE_MODIFYING_COMMANDS:
            # print("[Server] Broadcasting state update after command.")
            self.network.broadcast(json.dumps({'type': 'state_update', 'state': self.game_state.to_json()}))

        return result

    def _execute_random(self, command):
        var_name = command['name']
        min_val = self._evaluate_expression(command['min'])
        max_val = self._evaluate_expression(command['max'])
        try:
            self.game_state.variables[var_name] = random.randint(int(min_val), int(max_val))
        except (ValueError, TypeError): print(f"Error: min/max for random must be ints.", file=sys.stderr)
        return None

    def _execute_attack(self, command):
        attacker_name = command['attacker']
        target_name = command['target']
        attacker = self.game_state.entities.get(attacker_name)
        target = self.game_state.entities.get(target_name)
        if not attacker or not target: print(f"Error: Attacker or target not found.", file=sys.stderr); return None
        if attacker.get('health', 0) <= 0: print(f"Error: {attacker_name} is already defeated.", file=sys.stderr); return None
        damage = random.randint(1, int(attacker.get('strength', 1)))
        target['health'] = target.get('health', 0) - damage
        print(f"{attacker_name} attacks {target_name} for {damage} damage!")
        if target['health'] <= 0:
            target['health'] = 0
            print(f"{target_name} has been defeated.")
            self.game_state.variables['last_death'] = target_name
            self._trigger_event('death')
        return None

    def _execute_play_sound(self, command):
        if not self.sound_enabled: return None
        try: pygame.mixer.Sound(self._evaluate_expression(command['filepath'])).play()
        except pygame.error as e: print(f"Error playing sound '{command['filepath']}': {e}", file=sys.stderr)
        return None

    def _execute_play_music(self, command):
        if not self.sound_enabled: return None
        try:
            pygame.mixer.music.load(self._evaluate_expression(command['filepath']))
            pygame.mixer.music.play(-1)
        except pygame.error as e: print(f"Error playing music '{command['filepath']}': {e}", file=sys.stderr)
        return None

    def _execute_play_cutscene(self, command):
        if command['name'] in self.cutscenes: return self._execute_block(self.cutscenes[command['name']])
        else: print(f"Error: Cutscene '{command['name']}' not defined.", file=sys.stderr); return None

    def _execute_call_function(self, command):
        if command['name'] in self.functions: return self._execute_block(self.functions[command['name']])
        else: print(f"Error: Function '{command['name']}' not defined.", file=sys.stderr); return None

    def _trigger_event(self, event_name):
        if event_name in self.events: return self._execute_block(self.events[event_name])
        return None

    def _execute_loop(self, command):
        try: count = int(self._evaluate_expression(command['count_expr']))
        except (ValueError, TypeError): print(f"Error: Loop count must be an int.", file=sys.stderr); return None
        self.game_state.variables['loop_index'] = 0
        for i in range(count):
            self.game_state.variables['loop_index'] = i
            signal = self._execute_block(command['block'])
            if signal == 'break': break
            if signal == 'continue': continue
        if 'loop_index' in self.game_state.variables: del self.game_state.variables['loop_index']
        return None

    def _execute_set_quest(self, command):
        quest_id, new_state = command['id'], command['state']
        if quest_id in self.game_state.quests: self.game_state.quests[quest_id]['state'] = new_state
        else: print(f"Error: Quest '{quest_id}' not defined.", file=sys.stderr)
        return None

    def _execute_start_dialog(self, command):
        if self.mode == 'client': print("Dialogs are currently disabled for clients."); return None
        name = command['name']
        if name not in self.dialogs: print(f"Error: Dialog '{name}' not defined.", file=sys.stderr); return None
        dialog = self.dialogs[name]
        for say_command in dialog['say_nodes']: self._execute_command(say_command)
        if not dialog['options']: return None
        print("\nChoose an option:")
        for i, option in enumerate(dialog['options']): print(f"  {i + 1}: {option['text']}")
        while True:
            try:
                choice_index = int(input("> ")) - 1
                if 0 <= choice_index < len(dialog['options']): return self._execute_block(dialog['options'][choice_index]['block'])
                else: print("Invalid choice.")
            except (ValueError, EOFError, KeyboardInterrupt): print("\nDialog cancelled."); return None

    def _execute_if(self, command):
        if self._evaluate_condition(command['condition']): return self._execute_block(command['then_block'])
        elif command['else_block']: return self._execute_block(command['else_block'])
        return None

    def _execute_say(self, command):
        message = command['value']
        def replace_var(match): return str(self._evaluate_expression(match.group(1)))
        if message.startswith('"') and message.endswith('"'): message = message[1:-1]
        print(re.sub(r'\{([\w\.]+)\}', replace_var, message))
        return None

    def _execute_define(self, command):
        self.game_state.variables[command['name']] = self._evaluate_expression(command['value'])
        return None

    def _execute_increase_stat(self, command):
        name, value_str = command['name'], command['value']
        current_value = self.game_state.variables.get(name, 0)
        try: self.game_state.variables[name] = float(current_value) + float(self._evaluate_expression(value_str))
        except (ValueError, TypeError): print(f"Error: Stat '{name}' and value must be numeric.", file=sys.stderr)
        return None

    def _execute_decrease_stat(self, command):
        name, value_str = command['name'], command['value']
        current_value = self.game_state.variables.get(name, 0)
        try: self.game_state.variables[name] = float(current_value) - float(self._evaluate_expression(value_str))
        except (ValueError, TypeError): print(f"Error: Stat '{name}' and value must be numeric.", file=sys.stderr)
        return None

    def _execute_learn_skill(self, command):
        skill_name = command['name']
        if skill_name not in self.game_state.skills: self.game_state.skills.append(skill_name)
        return None

    def _execute_forget_skill(self, command):
        skill_name = command['name']
        if skill_name in self.game_state.skills: self.game_state.skills.remove(skill_name)
        return None

    def _execute_give_item(self, command):
        item_name, count = command['name'], int(self._evaluate_expression(command['count']))
        if count <= 0: return None
        self.game_state.inventory[item_name] = self.game_state.inventory.get(item_name, 0) + count
        return None

    def _execute_take_item(self, command):
        item_name, count = command['name'], int(self._evaluate_expression(command['count']))
        if count <= 0: return None
        current_count = self.game_state.inventory.get(item_name, 0)
        if current_count >= count:
            self.game_state.inventory[item_name] = current_count - count
            if self.game_state.inventory[item_name] == 0: del self.game_state.inventory[item_name]
        else: print(f"Error: Not enough '{item_name}'. Have {current_count}, need {count}.", file=sys.stderr)
        return None

    def _evaluate_expression(self, expr_str):
        expr_str = str(expr_str).strip()
        if expr_str == 'local_player': return self.player_id
        if expr_str.startswith('{') and expr_str.endswith('}'): expr_str = expr_str[1:-1]
        parts = expr_str.split('.')
        if len(parts) == 2:
            entity_name, stat_name = parts
            if entity_name in self.game_state.entities and stat_name in self.game_state.entities[entity_name]:
                return self.game_state.entities[entity_name][stat_name]
        if expr_str in self.game_state.variables: return self.game_state.variables[expr_str]
        if expr_str.startswith('"') and expr_str.endswith('"'): return expr_str[1:-1]
        try: return int(expr_str)
        except ValueError:
            try: return float(expr_str)
            except ValueError: return expr_str

    def _evaluate_condition(self, condition_str):
        # This function remains mostly unchanged, but evaluation now uses the updated _evaluate_expression
        match_skill = re.match(r'has skill (\w+)', condition_str)
        if match_skill: return match_skill.group(1) in self.game_state.skills
        match_item = re.match(r'has (?:(\d+)\s+)?(\w+)', condition_str)
        if match_item:
            count_str, item_name = match_item.groups()
            return self.game_state.inventory.get(item_name, 0) >= (int(count_str) if count_str else 1)
        match_quest = re.match(r'quest (\w+) is (\w+)', condition_str)
        if match_quest:
            quest_id, state = match_quest.groups()
            return self.game_state.quests.get(quest_id, {}).get('state') == state
        match = re.match(r'(.+?)\s*(>=|<=|==|!=|>|<)\s*(.+)', condition_str)
        if not match:
            value = self._evaluate_expression(condition_str)
            return bool(value) if not isinstance(value, str) else value.lower() in ['true', 'yes', 'on']
        left_val, op, right_val = self._evaluate_expression(match.group(1)), match.group(2), self._evaluate_expression(match.group(3))
        try:
            num_left, num_right = float(left_val), float(right_val)
            ops = {'==': num_left == num_right, '!=': num_left != num_right, '>': num_left > num_right, '<': num_left < num_right, '>=': num_left >= num_right, '<=': num_left <= num_right}
            return ops[op]
        except (ValueError, TypeError): return str(left_val) == str(right_val) if op == '==' else str(left_val) != str(right_val)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ldscript_interpreter.py <filepath.ld> [--host [<ip>]|--connect <ip>]")
        sys.exit(1)

    filepath = sys.argv[1]
    mode = 'singleplayer'
    host = '127.0.0.1'

    if len(sys.argv) > 2:
        if sys.argv[2] == '--host':
            mode = 'host'
            if len(sys.argv) > 3: host = sys.argv[3]
        elif sys.argv[2] == '--connect':
            mode = 'client'
            if len(sys.argv) > 3: host = sys.argv[3]
            else: print("Error: --connect requires an IP address."); sys.exit(1)

    interpreter = Interpreter(mode=mode, host=host)
    interpreter.run_from_file(filepath)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        if interpreter.network: interpreter.network.shutdown()

if __name__ == "__main__":
    main()
