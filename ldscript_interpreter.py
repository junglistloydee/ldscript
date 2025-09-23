import re
import sys
import random
import pygame
import os
import json
import time
import threading
from copy import deepcopy
from game_state import GameState
from network import Server, Client

STATE_MODIFYING_COMMANDS = {
    'define', 'increase_stat', 'decrease_stat',
    'learn_skill', 'forget_skill', 'give_item', 'take_item',
    'attack', 'random', 'set_quest', 'buy', 'sell'
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

    def _clean_lines(self, file_content_lines):
        cleaned_lines = []
        for line in file_content_lines:
            code = line.split('#')[0].strip()
            if code:
                cleaned_lines.append(code)
        return cleaned_lines

    def run_from_file(self, filepath):
        try:
            abs_filepath = os.path.abspath(filepath)
            initial_dir = os.path.dirname(abs_filepath)
            with open(abs_filepath, 'r') as f:
                lines = self._clean_lines(f)
            processed_lines = self._preprocess_imports(lines, initial_dir, set([abs_filepath]))
            self.ast, _ = self._parse(processed_lines)
            if self.mode == 'client':
                if not self.network.connect(): return
            execution_thread = threading.Thread(target=self._execute_block, args=(self.ast,))
            execution_thread.daemon = True
            execution_thread.start()
            return execution_thread
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
                        imported_content = self._clean_lines(f)
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

            match_option = re.match(r'option ("[^"]*")', line)
            if match_option:
                option_text = match_option.group(1)[1:-1]
                option_block, end_index = self._parse(lines, i + 1, end_keywords=['end option'])
                ast.append({'type': 'option', 'text': option_text, 'block': option_block}); i = end_index + 1
                continue

            match_on_event = re.match(r'on (\w+)', line)
            if match_on_event:
                name = match_on_event.group(1)
                event_block, end_index = self._parse(lines, i + 1, end_keywords=['end event'])
                self.events[name] = event_block; i = end_index + 1; continue

            match_dialog_def = re.match(r'dialog (\w+)', line)
            if match_dialog_def:
                name = match_dialog_def.group(1)
                dialog_block, end_index = self._parse(lines, i + 1, end_keywords=['end dialog'])
                self.dialogs[name] = dialog_block; i = end_index + 1; continue

            match_start_dialog = re.match(r'start dialog (\w+)', line)
            if match_start_dialog:
                ast.append({'type': 'start_dialog', 'name': match_start_dialog.group(1)}); i += 1; continue

            match_entity_def = re.match(r'entity (\w+)', line)
            if match_entity_def:
                name = match_entity_def.group(1)
                entity_block, end_index = self._parse_entity_block(lines, i + 1)
                self.game_state.entities[name] = entity_block; i = end_index + 1; continue

            match_item_def = re.match(r'item (\w+)', line)
            if match_item_def:
                name = match_item_def.group(1)
                item_block, end_index = self._parse_item_block(lines, i + 1)
                item_block['id'] = name
                self.game_state.items[name] = item_block
                i = end_index + 1
                continue

            match_quest_def = re.match(r'quest (\w+) "([^"]*)"', line)
            if match_quest_def:
                quest_id, quest_name = match_quest_def.groups()
                properties, end_index = self._parse_quest_block(lines, i + 1)
                self.game_state.quests[quest_id] = {'id': quest_id, 'name': quest_name, **properties}; i = end_index + 1; continue

            match_list_def = re.match(r'string_list (\w+)', line)
            if match_list_def:
                name = match_list_def.group(1)
                list_data, end_index = self._parse_string_list_block(lines, i + 1)
                self.game_state.lists[name] = list_data; i = end_index + 1; continue

            match_dict_def = re.match(r'dictionary (\w+)', line)
            if match_dict_def:
                name = match_dict_def.group(1)
                dict_data, end_index = self._parse_dictionary_block(lines, i + 1)
                self.game_state.dictionaries[name] = dict_data; i = end_index + 1; continue

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

            match_gain_xp = re.match(r'gain_xp (\w+) (.*)', line)
            if match_gain_xp:
                entity_id, amount_expr = match_gain_xp.groups()
                ast.append({'type': 'gain_xp', 'entity_id': entity_id, 'amount': amount_expr}); i += 1; continue

            match_give = re.match(r'give (?:(\d+)\s+)?(\w+)', line)
            if match_give:
                count, name = match_give.groups()
                ast.append({'type': 'give_item', 'name': name, 'count': count or "1"}); i += 1; continue

            match_take = re.match(r'take (?:(\d+)\s+)?(\w+)', line)
            if match_take:
                count, name = match_take.groups()
                ast.append({'type': 'take_item', 'name': name, 'count': count or "1"}); i += 1; continue

            match_buy = re.match(r'buy (?:(\d+)\s+)?(\w+) from (\w+)', line)
            if match_buy:
                count, item_id, vendor_id = match_buy.groups()
                ast.append({'type': 'buy', 'item_id': item_id, 'vendor_id': vendor_id, 'count': count or "1"}); i += 1; continue

            match_sell = re.match(r'sell (?:(\d+)\s+)?(\w+) to (\w+)', line)
            if match_sell:
                count, item_id, vendor_id = match_sell.groups()
                ast.append({'type': 'sell', 'item_id': item_id, 'vendor_id': vendor_id, 'count': count or "1"}); i += 1; continue

            match_shop = re.match(r'shop (\w+)', line)
            if match_shop:
                vendor_id = match_shop.group(1)
                ast.append({'type': 'shop', 'vendor_id': vendor_id}); i += 1; continue

            match_inventory = re.match(r'inventory', line)
            if match_inventory:
                ast.append({'type': 'inventory'}); i += 1; continue

            match_equip = re.match(r'equip (\w+)', line)
            if match_equip:
                ast.append({'type': 'equip', 'item_id': match_equip.group(1)}); i += 1; continue

            match_unequip = re.match(r'unequip (\w+)', line)
            if match_unequip:
                ast.append({'type': 'unequip', 'item_id': match_unequip.group(1)}); i += 1; continue

            match_attack = re.match(r'attack ([\w{}.-]+) on ([\w{}.-]+)(?: with ([\w{}.-]+))?', line)
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

            match_random_choice = re.match(r'random_choice (\w+) as (\w+)', line)
            if match_random_choice:
                list_name, var_name = match_random_choice.groups()
                ast.append({'type': 'random_choice', 'list_name': list_name, 'var_name': var_name}); i += 1; continue

            match_gen_room_desc = re.match(r'generate_room_description as (\w+)', line)
            if match_gen_room_desc:
                var_name = match_gen_room_desc.group(1)
                ast.append({'type': 'generate_room_description', 'var_name': var_name}); i += 1; continue

            match_weighted_choice = re.match(r'weighted_random_choice (\w+) as (\w+)', line)
            if match_weighted_choice:
                dict_name, var_name = match_weighted_choice.groups()
                ast.append({'type': 'weighted_random_choice', 'dict_name': dict_name, 'var_name': var_name}); i += 1; continue

            match_play_sound = re.match(r'play_sound (.*)', line)
            if match_play_sound:
                ast.append({'type': 'play_sound', 'filepath': match_play_sound.group(1).strip()}); i += 1; continue

            match_play_music = re.match(r'play_music (.*)', line)
            if match_play_music:
                ast.append({'type': 'play_music', 'filepath': match_play_music.group(1).strip()}); i += 1; continue

            if line in ['else', 'end', 'end cutscene', 'end dialog', 'end option', 'end quest', 'end entity', 'end function', 'end event', 'end item']:
                raise SyntaxError(f"Unexpected '{line}' keyword.")
            raise SyntaxError(f"Unknown command: {line}")
        if end_keywords:
            raise SyntaxError(f"Expected one of '{end_keywords}' but reached end of file.")
        return ast, i

    def _parse_key_value_block(self, lines, index, end_keyword):
        """
        Parses a generic block of key-value pairs, supporting nested blocks.
        A line with a single word is treated as the key for a new nested block.
        """
        properties = {}
        i = index
        while i < len(lines):
            line = lines[i]
            if line == end_keyword:
                return properties, i

            # Check for a nested block (e.g., 'effect_value')
            match_block = re.match(r'^(\w+)$', line)
            if match_block:
                key = match_block.group(1)
                nested_end_keyword = f"end {key}"
                # Recursively parse the nested block
                nested_properties, end_i = self._parse_key_value_block(lines, i + 1, nested_end_keyword)
                properties[key] = nested_properties
                i = end_i + 1
                continue

            # Check for a simple key-value pair (e.g., 'name "Iron Sword"')
            match_prop = re.match(r'(\w+)\s+(.*)', line)
            if match_prop:
                key, value = match_prop.groups()
                properties[key] = self._evaluate_expression(value)
                i += 1
                continue

            raise SyntaxError(f"Invalid line in block near '{line}'")

        raise SyntaxError(f"Expected '{end_keyword}' but reached end of file.")

    def _parse_entity_block(self, lines, index):
        # Refactored to use the generic key-value block parser
        return self._parse_key_value_block(lines, index, 'end entity')

    def _parse_item_block(self, lines, index):
        # Refactored to use the generic key-value block parser
        return self._parse_key_value_block(lines, index, 'end item')

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

    def _parse_string_list_block(self, lines, index):
        """Parses a block of strings for a string_list definition."""
        items = []
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end string_list':
                return items, i
            # Each line is a string item, remove quotes
            items.append(line.strip('"'))
            i += 1
        raise SyntaxError("Expected 'end string_list' but reached end of file.")

    def _parse_dictionary_block(self, lines, index):
        """Parses a block of key-value pairs for a dictionary definition."""
        properties = {}
        i = index
        while i < len(lines):
            line = lines[i]
            if line == 'end dictionary':
                return properties, i
            match_prop = re.match(r'(\w+)\s+(.*)', line)
            if match_prop:
                key, value = match_prop.groups()
                properties[key] = self._evaluate_expression(value)
            else:
                raise SyntaxError(f"Invalid line in dictionary definition: {line}")
            i += 1
        raise SyntaxError("Expected 'end dictionary' but reached end of file.")

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

    def _execute_random_choice(self, command):
        list_name = command['list_name']
        var_name = command['var_name']

        if list_name not in self.game_state.lists:
            print(f"Error: List '{list_name}' not found.", file=sys.stderr)
            return None

        chosen_item = random.choice(self.game_state.lists[list_name])
        self.game_state.variables[var_name] = chosen_item
        return None

    def _execute_generate_room_description(self, command):
        var_name = command['var_name']

        try:
            adj = random.choice(self.game_state.lists['adjectives'])
            room_type = random.choice(self.game_state.lists['room_types'])
            detail = random.choice(self.game_state.lists['details'])
        except KeyError as e:
            print(f"Error: Missing required list for room generation: {e}", file=sys.stderr)
            return None

        description = f"You are in a {adj} {room_type}. You notice {detail}."
        self.game_state.variables[var_name] = description
        return None

    def _execute_weighted_random_choice(self, command):
        dict_name = command['dict_name']
        var_name = command['var_name']

        if dict_name not in self.game_state.dictionaries:
            print(f"Error: Dictionary '{dict_name}' not found.", file=sys.stderr)
            return None

        choices_dict = self.game_state.dictionaries[dict_name]
        population = list(choices_dict.keys())
        weights = [float(w) for w in choices_dict.values()]

        if not population:
            print(f"Warning: Dictionary '{dict_name}' is empty.", file=sys.stderr)
            return None

        try:
            chosen_item = random.choices(population, weights=weights, k=1)[0]
            self.game_state.variables[var_name] = chosen_item
        except (ValueError, TypeError) as e:
            print(f"Error during weighted choice from '{dict_name}': {e}", file=sys.stderr)

        return None

    def _execute_attack(self, command):
        attacker_id = self._evaluate_expression(command['attacker'])
        target_id = self._evaluate_expression(command['target'])

        attacker_entity = self.game_state.entities.get(attacker_id)
        target_entity = self.game_state.entities.get(target_id)

        if not attacker_entity or not target_entity:
            print(f"Error: Attacker or target not found.", file=sys.stderr)
            return None

        if attacker_entity.get('health', 0) <= 0:
            print(f"Error: {attacker_id} is already defeated.", file=sys.stderr)
            return None
        if target_entity.get('health', 0) <= 0:
            print(f"Error: {target_id} is already defeated.", file=sys.stderr)
            return None

        # --- Calculate Attacker's Power ---
        base_attack = int(attacker_entity.get('strength', 5))
        variance = int(attacker_entity.get('damage_variance', 1))
        crit_chance = float(attacker_entity.get('crit_chance', 0.1))
        crit_multiplier = float(attacker_entity.get('crit_multiplier', 1.5))

        # Add weapon damage if the attacker is the player
        # For now, we assume only the main player has equipment state
        # A more robust system would check if the attacker_id matches a player with an equipment state
        if attacker_id == self.player_id and self.game_state.equipped_weapon:
            base_attack += int(self.game_state.equipped_weapon.get('damage', 0))

        # --- Calculate Target's Defense ---
        total_defense = 0
        if target_id == self.player_id: # Simplified: only player has defense
            if self.game_state.equipped_shield:
                total_defense += int(self.game_state.equipped_shield.get('defense', 0))
            if self.game_state.equipped_armor:
                total_defense += int(self.game_state.equipped_armor.get('defense', 0))
            if self.game_state.equipped_cloak:
                total_defense += int(self.game_state.equipped_cloak.get('defense', 0))
        else: # For monsters
            total_defense = int(target_entity.get('defense', 0))


        # --- Calculate Damage ---
        damage = random.randint(base_attack - variance, base_attack + variance)

        is_crit = random.random() < crit_chance
        if is_crit:
            damage = int(damage * crit_multiplier)

        final_damage = max(0, damage - total_defense)
        target_entity['health'] = target_entity.get('health', 0) - final_damage

        # --- Print Combat Log ---
        if is_crit:
            print(f"CRITICAL HIT! {attacker_id} strikes {target_id} for {damage} damage!")
        else:
            print(f"{attacker_id} strikes {target_id} for {damage} damage!")

        if total_defense > 0:
            absorbed = damage - final_damage
            print(f"{target_id}'s armor absorbed {absorbed} damage.")

        print(f"{target_id} takes {final_damage} damage. Health is now {target_entity.get('health', 0)}.")

        # --- Check for Defeat ---
        if target_entity.get('health', 0) <= 0:
            target_entity['health'] = 0
            print(f"{target_id} has been defeated.")
            self.game_state.variables['last_death'] = target_id

            # Grant XP to the attacker
            xp_reward = int(target_entity.get('xp_reward', 0))
            if xp_reward > 0:
                self._execute_gain_xp({'entity_id': attacker_id, 'amount': xp_reward})

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
        if self.mode == 'client':
            print("Dialogs are currently disabled for clients.")
            return None

        name = command['name']
        if name not in self.dialogs:
            print(f"Error: Dialog '{name}' not defined.", file=sys.stderr)
            return None

        dialog_ast = self.dialogs[name]

        pre_option_commands = []
        options = []
        found_options = False
        for cmd in dialog_ast:
            if cmd['type'] == 'option':
                found_options = True
                options.append(cmd)
            elif not found_options:
                pre_option_commands.append(cmd)
            else:
                print(f"Warning: Command '{cmd['type']}' found after options in dialog '{name}'. It will be ignored.", file=sys.stderr)

        self._execute_block(pre_option_commands)

        if not options:
            return None

        print("\nChoose an option:")
        for i, option in enumerate(options):
            print(f"  {i + 1}: {option['text']}")

        while True:
            try:
                choice_index = int(input("> ")) - 1
                if 0 <= choice_index < len(options):
                    return self._execute_block(options[choice_index]['block'])
                else:
                    print("Invalid choice.")
            except (ValueError, EOFError, KeyboardInterrupt):
                print("\nDialog cancelled.")
                return None

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
        item_id, count = command['name'], int(self._evaluate_expression(command['count']))
        if item_id not in self.game_state.items:
            print(f"Error: Item '{item_id}' is not defined.", file=sys.stderr)
            return None
        if count <= 0: return None
        for _ in range(count):
            self.game_state.inventory.append(deepcopy(self.game_state.items[item_id]))
        return None

    def _execute_take_item(self, command):
        item_id, count = command['name'], int(self._evaluate_expression(command['count']))
        if count <= 0: return None

        current_count = sum(1 for item in self.game_state.inventory if item.get('id') == item_id)
        if current_count < count:
            print(f"Error: Not enough '{item_id}'. Have {current_count}, need {count}.", file=sys.stderr)
            return None

        removed_count = 0
        new_inventory = []
        for item in self.game_state.inventory:
            if item.get('id') == item_id and removed_count < count:
                removed_count += 1
            else:
                new_inventory.append(item)
        self.game_state.inventory = new_inventory
        return None

    def _execute_inventory(self, command):
        print("Your inventory:")
        if not self.game_state.inventory:
            print("  - Empty")
            return None

        item_counts = {}
        for item in self.game_state.inventory:
            item_id = item.get('id', 'unknown_item')
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        for item_id, count in sorted(item_counts.items()):
            item_def = self.game_state.items.get(item_id)
            if item_def:
                print(f"  - {count}x {item_def.get('name', item_id)} ({item_def.get('description', '')})")
            else:
                print(f"  - {count}x {item_id}")
        return None

    def _execute_shop(self, command):
        vendor_id = command['vendor_id']
        vendor = self.game_state.entities.get(vendor_id)
        if not vendor:
            print(f"Error: Vendor '{vendor_id}' not found.", file=sys.stderr)
            return None

        vendor_inventory_ids = vendor.get('inventory', "").split(',')
        if not vendor_inventory_ids or vendor_inventory_ids == ['']:
            print(f"{vendor.get('name', vendor_id)} has nothing for sale.")
            return None

        print(f"{vendor.get('name', vendor_id)}'s Shop:")
        for item_id in sorted(list(set(vendor_inventory_ids))):
            item_def = self.game_state.items.get(item_id)
            if item_def:
                price = item_def.get('price', 0)
                print(f"  - {item_def.get('name', item_id)} ({price} gold) - {item_def.get('description', 'No description.')}")
            else:
                print(f"  - {item_id} (Unknown Item)")
        return None

    def _execute_buy(self, command):
        item_id, count, vendor_id = command['item_id'], int(self._evaluate_expression(command['count'])), command['vendor_id']

        vendor = self.game_state.entities.get(vendor_id)
        if not vendor:
            print(f"Error: Vendor '{vendor_id}' not found.", file=sys.stderr)
            return None

        item_def = self.game_state.items.get(item_id)
        if not item_def:
            print(f"Error: Item '{item_id}' is not defined.", file=sys.stderr)
            return None

        vendor_inventory = vendor.get('inventory', "").split(',')
        if item_id not in vendor_inventory:
            print(f"Error: {vendor.get('name', vendor_id)} does not sell '{item_id}'.", file=sys.stderr)
            return None

        price = item_def.get('price', 0)
        total_cost = price * count

        player_gold = self.game_state.variables.get('gold', 0)
        if player_gold < total_cost:
            print(f"Error: Not enough gold. Have {player_gold}, need {total_cost}.", file=sys.stderr)
            return None

        self.game_state.variables['gold'] = player_gold - total_cost
        for _ in range(count):
            self.game_state.inventory.append(deepcopy(item_def))

        print(f"You bought {count}x {item_def.get('name', item_id)} for {total_cost} gold.")
        return None

    def _execute_sell(self, command):
        item_id, count, vendor_id = command['item_id'], int(self._evaluate_expression(command['count'])), command['vendor_id']

        vendor = self.game_state.entities.get(vendor_id)
        if not vendor:
            print(f"Error: Vendor '{vendor_id}' not found.", file=sys.stderr)
            return None

        item_def = self.game_state.items.get(item_id)
        if not item_def:
            print(f"Error: Item '{item_id}' is not defined.", file=sys.stderr)
            return None

        player_item_count = sum(1 for item in self.game_state.inventory if item['id'] == item_id)
        if player_item_count < count:
            print(f"Error: You don't have {count} of '{item_id}' to sell. You have {player_item_count}.", file=sys.stderr)
            return None

        price = item_def.get('price', 0)
        sell_price = int(price * 0.5)
        total_gain = sell_price * count

        removed_count = 0
        new_inventory = []
        for item in self.game_state.inventory:
            if item['id'] == item_id and removed_count < count:
                removed_count += 1
            else:
                new_inventory.append(item)
        self.game_state.inventory = new_inventory

        self.game_state.variables['gold'] = self.game_state.variables.get('gold', 0) + total_gain

        print(f"You sold {count}x {item_def.get('name', item_id)} for {total_gain} gold.")
        return None

    def _execute_equip(self, command):
        item_id_to_equip = command['item_id']

        item_to_equip = None
        for item in self.game_state.inventory:
            if item.get('id') == item_id_to_equip:
                item_to_equip = item
                break

        if not item_to_equip:
            print(f"Error: Item '{item_id_to_equip}' not found in inventory.", file=sys.stderr)
            return

        item_type = item_to_equip.get('type')
        item_subtype = item_to_equip.get('subtype')

        slot_to_update = None
        if item_type == 'weapon':
            slot_to_update = 'equipped_weapon'
        elif item_type == 'shield':
            slot_to_update = 'equipped_shield'
        elif item_type == 'armor' and (item_subtype == 'body_armor' or not item_subtype):
            slot_to_update = 'equipped_armor'
        elif item_type == 'armor' and item_subtype == 'cloak':
            slot_to_update = 'equipped_cloak'
        elif item_type == 'equipment':
            self.game_state.equipped_misc.append(item_to_equip)
            self.game_state.inventory.remove(item_to_equip)
            print(f"Equipped {item_to_equip.get('name', item_id_to_equip)}.")
            return
        else:
            print(f"Error: Item '{item_id_to_equip}' of type '{item_type}' is not equippable.", file=sys.stderr)
            return

        currently_equipped = getattr(self.game_state, slot_to_update)
        if currently_equipped:
            self.game_state.inventory.append(currently_equipped)
            print(f"Unequipped {currently_equipped.get('name', 'item')}.")

        setattr(self.game_state, slot_to_update, item_to_equip)
        self.game_state.inventory.remove(item_to_equip)
        print(f"Equipped {item_to_equip.get('name', item_id_to_equip)}.")
        return None

    def _execute_unequip(self, command):
        item_id_to_unequip = command['item_id']

        slot_to_clear = None
        equipped_item = None

        if self.game_state.equipped_weapon and self.game_state.equipped_weapon.get('id') == item_id_to_unequip:
            slot_to_clear = 'equipped_weapon'
            equipped_item = self.game_state.equipped_weapon
        elif self.game_state.equipped_shield and self.game_state.equipped_shield.get('id') == item_id_to_unequip:
            slot_to_clear = 'equipped_shield'
            equipped_item = self.game_state.equipped_shield
        elif self.game_state.equipped_armor and self.game_state.equipped_armor.get('id') == item_id_to_unequip:
            slot_to_clear = 'equipped_armor'
            equipped_item = self.game_state.equipped_armor
        elif self.game_state.equipped_cloak and self.game_state.equipped_cloak.get('id') == item_id_to_unequip:
            slot_to_clear = 'equipped_cloak'
            equipped_item = self.game_state.equipped_cloak
        else:
            for item in self.game_state.equipped_misc:
                if item.get('id') == item_id_to_unequip:
                    equipped_item = item
                    break
            if equipped_item:
                 self.game_state.equipped_misc.remove(equipped_item)
                 self.game_state.inventory.append(equipped_item)
                 print(f"Unequipped {equipped_item.get('name', item_id_to_unequip)}.")
                 return None

        if not slot_to_clear:
            print(f"Error: Item '{item_id_to_unequip}' is not equipped.", file=sys.stderr)
            return None

        setattr(self.game_state, slot_to_clear, None)
        self.game_state.inventory.append(equipped_item)
        print(f"Unequipped {equipped_item.get('name', item_id_to_unequip)}.")
        return None

    def _level_up(self, entity_id):
        player = self.game_state.entities.get(entity_id)
        if not player:
            return

        # Get leveling constants from game state variables
        hp_gain = int(self._evaluate_expression('HP_GAIN_PER_LEVEL'))
        attack_gain = int(self._evaluate_expression('ATTACK_GAIN_PER_LEVEL'))
        crit_chance_gain = float(self._evaluate_expression('CRIT_CHANCE_GAIN_PER_LEVEL'))

        player['level'] = int(player.get('level', 1)) + 1

        old_max_hp = int(player.get('max_hp', 100))
        player['max_hp'] = old_max_hp + hp_gain
        player['health'] = player['max_hp'] # Full heal on level up

        player['strength'] = int(player.get('strength', 5)) + attack_gain
        player['crit_chance'] = float(player.get('crit_chance', 0.1)) + crit_chance_gain

        print(f"\n--- {entity_id} has reached Level {player['level']}! ---")
        print(f"Max HP increased from {old_max_hp} to {player['max_hp']}!")
        print(f"Strength increased to {player['strength']}!")
        print(f"Critical Chance increased to {player['crit_chance']:.2f}!")
        print("--------------------------------------------------")

        # Calculate XP for next level
        base_xp = int(self._evaluate_expression('BASE_XP_TO_LEVEL_UP'))
        scale_factor = float(self._evaluate_expression('XP_SCALE_FACTOR'))
        player['xp_to_next_level'] = int(base_xp * (scale_factor ** (player['level'] - 1)))


    def _execute_gain_xp(self, command):
        entity_id = self._evaluate_expression(command['entity_id'])
        amount = int(self._evaluate_expression(command['amount']))

        player = self.game_state.entities.get(entity_id)
        if not player:
            print(f"Error: Cannot grant XP to non-existent entity '{entity_id}'.", file=sys.stderr)
            return None

        current_xp = int(player.get('xp', 0))
        player['xp'] = current_xp + amount
        print(f"{entity_id} gained {amount} XP.")

        # Check for level up
        xp_to_next = int(player.get('xp_to_next_level', 100))
        while player['xp'] >= xp_to_next:
            player['xp'] -= xp_to_next
            self._level_up(entity_id)
            # After leveling up, the xp_to_next_level is recalculated inside _level_up
            xp_to_next = int(player.get('xp_to_next_level'))

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
            count_str, item_id = match_item.groups()
            required_count = int(count_str) if count_str else 1
            current_count = sum(1 for item in self.game_state.inventory if item.get('id') == item_id)
            return current_count >= required_count
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
    execution_thread = interpreter.run_from_file(filepath)

    if execution_thread and mode == 'singleplayer':
        execution_thread.join()
    elif execution_thread:
        try:
            while execution_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down.")
        finally:
            if interpreter.network:
                interpreter.network.shutdown()

if __name__ == "__main__":
    main()
