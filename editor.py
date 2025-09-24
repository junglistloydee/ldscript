import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog, scrolledtext
import json
import subprocess
import threading
import queue
from pathlib import Path
import sys
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field, asdict
from ld_parser import LdParser


APP_ROOT = Path(__file__).resolve().parent

# #########################################################################
# DEFINITIONS (Enums & Dataclasses)
# #########################################################################

class DataCategory(Enum):
    """Enum for data categories to prevent typos with string literals."""
    ENTITIES = "entities"
    ITEMS = "items"
    QUESTS = "quests"
    FUNCTIONS = "functions"
    DIALOGS = "dialogs"
    STRING_LISTS = "string_lists"
    DICTIONARIES = "dictionaries"

@dataclass
class Entity:
    stats: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Item:
    properties: Dict[str, Any] = field(default_factory=lambda: {"name": "New Item", "description": "", "price": 0})

@dataclass
class Quest:
    name: str = "New Quest"
    description: str = ""
    state: str = "inactive"

# #########################################################################
# MODEL - The central data store and logic for the application.
# #########################################################################

class ProjectModel:
    """
    Represents the single source of truth for all project data.
    Implements the observer pattern to notify views of changes.
    """
    def __init__(self):
        self._observers: List[Callable] = []
        self.filepath: Optional[Path] = None
        self.is_dirty: bool = False
        self._initialize_data()

    def _initialize_data(self):
        """Initializes or resets all data stores."""
        self.entities: Dict[str, Entity] = {}
        self.items: Dict[str, Item] = {}
        self.quests: Dict[str, Quest] = {}
        self.string_lists: Dict[str, List[str]] = {}
        self.dictionaries: Dict[str, Dict[str, str]] = {}
        self.functions: Dict[str, Any] = {}
        self.dialogs: Dict[str, Any] = {}
        self.dialogs_node_counter: int = 0
        self.functions_node_counter: int = 0
        self.is_dirty = False
        self.filepath = None
        self._notify_observers()

    def register_observer(self, callback: Callable):
        """Register a view to be notified of changes."""
        self._observers.append(callback)

    def _notify_observers(self, update_type: str = "full_update"):
        """Notify all registered views that the model has changed."""
        for callback in self._observers:
            callback(update_type)
        if self._observers:
            # Assumes first observer is the main app for title updates
            self._observers[0]("app_update")

    def _mark_dirty(self):
        """Marks the project as having unsaved changes."""
        if not self.is_dirty:
            self.is_dirty = True
            self._notify_observers("app_update")

    def new_project(self):
        """Resets the project to a new, empty state."""
        self._initialize_data()

    def load_project(self, filepath: str) -> None:
        """Loads project data from a JSON file."""
        self.filepath = Path(filepath)
        with self.filepath.open('r') as f:
            project_data = json.load(f)

        # Deserialize dicts back into dataclass objects
        self.entities = {k: Entity(**v) for k, v in project_data.get("entities", {}).items()}
        self.items = {k: Item(**v) for k, v in project_data.get("items", {}).items()}
        self.quests = {k: Quest(**v) for k, v in project_data.get("quests", {}).items()}
        self.string_lists = project_data.get("string_lists", {})
        self.dictionaries = project_data.get("dictionaries", {})
        
        self.functions = project_data.get("functions", {})
        self.dialogs = project_data.get("dialogs", {})
        self.dialogs_node_counter = project_data.get("dialogs_node_counter", 0)
        self.functions_node_counter = project_data.get("functions_node_counter", 0)
        
        self.is_dirty = False
        self._notify_observers()

    def load_from_parsed_ld(self, parsed_data: Dict[str, Any]):
        """Loads data from a parsed .ld file into the model."""
        self._initialize_data()

        # Convert parsed dicts into dataclass objects
        self.entities = {k: Entity(**v) for k, v in parsed_data.get("entities", {}).items()}
        self.items = {k: Item(properties=v) for k, v in parsed_data.get("items", {}).items()}

        # The quest parser returns a dict with 'id' and 'name', we need to map it
        # to the Quest dataclass which has name, description, state.
        self.quests = {}
        for k, v in parsed_data.get("quests", {}).items():
            self.quests[k] = Quest(
                name=v.get("name", "New Quest"),
                description=v.get("description", ""),
                state=v.get("state", "inactive")
            )

        self.functions = parsed_data.get("functions", {})
        self.dialogs = parsed_data.get("dialogs", {})

        # Since we don't parse node counters, we can try to infer them,
        # but for now, resetting is fine. A more robust solution could
        # parse the max ID number from the nodes.
        self.dialogs_node_counter = 0
        self.functions_node_counter = 0

        self.is_dirty = True
        self._notify_observers()

    def save_project(self, filepath: Optional[str] = None) -> None:
        """Saves project data to a JSON file."""
        if filepath:
            self.filepath = Path(filepath)
            
        if not self.filepath:
            raise ValueError("Filepath must be provided to save.")

        project_data = {
            # Serialize dataclasses to dicts for JSON compatibility
            "entities": {k: asdict(v) for k, v in self.entities.items()},
            "items": {k: asdict(v) for k, v in self.items.items()},
            "quests": {k: asdict(v) for k, v in self.quests.items()},
            "string_lists": self.string_lists,
            "dictionaries": self.dictionaries,
            "functions": self.functions,
            "dialogs": self.dialogs,
            "dialogs_node_counter": self.dialogs_node_counter,
            "functions_node_counter": self.functions_node_counter,
        }
        with self.filepath.open('w') as f:
            json.dump(project_data, f, indent=4)
        
        self.is_dirty = False
        self._notify_observers()

    # --- Private Generic Helpers ---
    def _get_data_store(self, category: DataCategory) -> Dict:
        return getattr(self, category.value)

    def _add_item(self, category: DataCategory, item_id: str, data_obj: Any):
        self._get_data_store(category)[item_id] = data_obj
        self._mark_dirty()
        self._notify_observers(f"{category.value}_update")

    def _delete_item(self, category: DataCategory, item_id: str):
        data_store = self._get_data_store(category)
        if item_id in data_store:
            del data_store[item_id]
            self._mark_dirty()
            self._notify_observers(f"{category.value}_update")

    def _update_item_id(self, category: DataCategory, old_id: str, new_id: str) -> bool:
        if not new_id or new_id == old_id:
            return False
        
        data_store = self._get_data_store(category)
        if new_id in data_store:
            messagebox.showerror("Error", f"ID '{new_id}' already exists.")
            return False
        
        data_store[new_id] = data_store.pop(old_id)
        # Update the 'id' field within the object itself if it exists
        if isinstance(data_store[new_id], dict) and 'id' in data_store[new_id]:
             data_store[new_id]['id'] = new_id
        self._mark_dirty()
        self._notify_observers(f"{category.value}_update")
        return True

    def _update_item_details(self, category: DataCategory, item_id: str, new_data_obj: Any):
        data_store = self._get_data_store(category)
        if item_id in data_store:
            data_store[item_id] = new_data_obj
            self._mark_dirty()

    # --- Public Explicit Methods for Entities, Items, Quests ---
    def add_data_item(self, category: DataCategory, item_id: str, data_obj: Any):
        self._add_item(category, item_id, data_obj)

    def delete_data_item(self, category: DataCategory, item_id: str):
        self._delete_item(category, item_id)

    def update_data_item_id(self, category: DataCategory, old_id: str, new_id: str) -> bool:
        return self._update_item_id(category, old_id, new_id)

    def update_data_item_details(self, category: DataCategory, item_id: str, new_data_obj: Any):
        self._update_item_details(category, item_id, new_data_obj)
        # No observer notification here as it's triggered by live tracing,
        # but it's necessary to persist the changes.
        self._notify_observers(f"{category.value}_update")

    # --- Entity-specific methods ---
    def update_entity_stat(self, entity_id: str, stat_name: str, new_value: Any, old_stat_name: Optional[str] = None):
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            # Prevent silent failure if a rename conflicts with an existing key
            if old_stat_name and old_stat_name != stat_name and stat_name in entity.stats:
                messagebox.showerror("Error", f"Stat '{stat_name}' already exists.")
                return False
            
            if old_stat_name and old_stat_name != stat_name:
                entity.stats.pop(old_stat_name, None)

            entity.stats[stat_name] = new_value
            self._mark_dirty()
            self._notify_observers(f"{DataCategory.ENTITIES.value}_update")
            return True
        return False

    def remove_entity_stat(self, entity_id: str, stat_name: str):
        if entity_id in self.entities and stat_name in self.entities[entity_id].stats:
            del self.entities[entity_id].stats[stat_name]
            self._mark_dirty()
            self._notify_observers(f"{DataCategory.ENTITIES.value}_update")
            
    # --- Logic Node (Functions/Dialogs) Specific Methods ---

    def get_next_node_id(self, category: DataCategory) -> str:
        """Generates a unique ID for a new logic node."""
        if category == DataCategory.DIALOGS:
            self.dialogs_node_counter += 1
            return f"dnode_{self.dialogs_node_counter}"
        elif category == DataCategory.FUNCTIONS:
            self.functions_node_counter += 1
            return f"fnode_{self.functions_node_counter}"
        # Fallback, should not be needed
        return f"node_{id(category)}"

    def _find_node_and_parent(self, nodes: List[Dict], node_id: str) -> Optional[tuple[Dict, List[Dict]]]:
        """Recursively finds a node and its parent list by ID."""
        for node in nodes:
            if node.get("id") == node_id:
                return node, nodes
            # Also check for else marker children
            child_nodes = node.get("nodes", [])
            else_marker_index = next((i for i, child in enumerate(child_nodes) if child.get("type") == "else_marker"), -1)

            if else_marker_index != -1:
                # Search both 'then' and 'else' blocks
                then_children = child_nodes[:else_marker_index]
                else_children = child_nodes[else_marker_index+1:]
                
                found_node, parent_list = self._find_node_and_parent(then_children, node_id)
                if found_node: return found_node, parent_list

                found_node, parent_list = self._find_node_and_parent(else_children, node_id)
                if found_node: return found_node, parent_list
            elif "nodes" in node:
                found_node, parent_list = self._find_node_and_parent(node["nodes"], node_id)
                if found_node:
                    return found_node, parent_list
        return None, None


    def add_logic_node(self, category: DataCategory, root_id: str, parent_node_id: str, node_data: Dict):
        """Adds a new logic node to a function or dialog."""
        data_store = self._get_data_store(category)
        root_item = data_store.get(root_id)
        if not root_item: return

        target_list = None
        if parent_node_id == root_id:
            target_list = root_item["nodes"]
        else:
            parent_node, _ = self._find_node_and_parent(root_item["nodes"], parent_node_id)
            if parent_node and "nodes" in parent_node:
                target_list = parent_node["nodes"]

        if target_list is not None:
            target_list.append(node_data)
            self._mark_dirty()
            self._notify_observers(f"{category.value}_update")

    def delete_logic_node(self, category: DataCategory, root_id: str, node_id: str):
        """Deletes a logic node from a function or dialog."""
        data_store = self._get_data_store(category)
        root_item = data_store.get(root_id)
        if not root_item: return

        # Check if we are deleting a root node
        if root_id == node_id:
            self._delete_item(category, root_id)
            return

        node, parent_list = self._find_node_and_parent(root_item["nodes"], node_id)
        if node and parent_list is not None:
            parent_list.remove(node)
            self._mark_dirty()
            self._notify_observers(f"{category.value}_update")

    def update_logic_node_properties(self, category: DataCategory, root_id: str, node_id: str, new_properties: Dict):
        """Updates the properties of a specific logic node."""
        data_store = self._get_data_store(category)
        root_item = data_store.get(root_id)
        if not root_item: return

        node, _ = self._find_node_and_parent(root_item["nodes"], node_id)
        if node:
            node.update(new_properties)
            self._mark_dirty()
            # Don't notify here, changes are live and would cause focus loss
            # A final notification can be sent when the user focuses out.
        
    def mark_logic_dirty(self, category: DataCategory):
        """Marks the project dirty and notifies observers for a logic update."""
        self._mark_dirty()
        self._notify_observers(f"{category.value}_update")

# #########################################################################
# CODE GENERATOR - Decoupled logic for creating the .ld file.
# #########################################################################

class LdCodeGenerator:
    """Handles the generation of the final .ld script from the project model."""
    def __init__(self, model: ProjectModel):
        self.model = model

    def generate(self) -> str:
        """Generates the full LDScript code."""
        code = [
            self._generate_string_lists(),
            self._generate_dictionaries(),
            self._generate_items(),
            self._generate_quests(),
            self._generate_entities(),
            self._generate_functions(),
            self._generate_dialogs(),
        ]
        return "\n".join(filter(None, code))

    def _generate_string_lists(self) -> str:
        lines = ["# --- String List Definitions ---"]
        if not self.model.string_lists: return ""
        for list_id, str_list in self.model.string_lists.items():
            lines.append(f"string_list {list_id}")
            for item in str_list:
                lines.append(f"    \"{item}\"")
            lines.append("end string_list\n")
        return "\n".join(lines)

    def _generate_dictionaries(self) -> str:
        lines = ["# --- Dictionary Definitions ---"]
        if not self.model.dictionaries: return ""
        for dict_id, a_dict in self.model.dictionaries.items():
            lines.append(f"dictionary {dict_id}")
            for key, value in a_dict.items():
                val_str = f"\"{value}\"" if isinstance(value, str) and not value.isnumeric() else value
                lines.append(f"    {key} {val_str}")
            lines.append("end dictionary\n")
        return "\n".join(lines)

    def _generate_properties_recursive(self, properties: Dict[str, Any], indent_level: int) -> List[str]:
        lines = []
        indent = "    " * indent_level
        for key, value in properties.items():
            if isinstance(value, dict):
                lines.append(f"{indent}{key}")
                lines.extend(self._generate_properties_recursive(value, indent_level + 1))
                lines.append(f"{indent}end {key}")
            else:
                val_str = f"\"{value}\"" if isinstance(value, str) and not str(value).isnumeric() else value
                lines.append(f"{indent}{key} {val_str}")
        return lines

    def _generate_items(self) -> str:
        lines = ["# --- Item Definitions ---"]
        if not self.model.items: return ""
        for item_id, item_obj in self.model.items.items():
            lines.append(f"item {item_id}")
            lines.extend(self._generate_properties_recursive(item_obj.properties, 1))
            lines.append("end item\n")
        return "\n".join(lines)

    def _generate_quests(self) -> str:
        lines = ["# --- Quest Definitions ---"]
        if not self.model.quests: return ""
        for quest_id, quest_obj in self.model.quests.items():
            lines.append(f"quest {quest_id} \"{quest_obj.name}\"")
            lines.append(f"    description \"{quest_obj.description}\"")
            lines.append(f"    state {quest_obj.state}")
            lines.append("end quest\n")
        return "\n".join(lines)

    def _generate_entities(self) -> str:
        lines = ["# --- Entity Definitions ---"]
        if not self.model.entities: return ""
        for entity_id, entity_obj in self.model.entities.items():
            lines.append(f"entity {entity_id}")
            for stat, value in entity_obj.stats.items():
                val_str = f"\"{value}\"" if isinstance(value, str) and not value.isnumeric() else value
                lines.append(f"    stat {stat} {val_str}")
            lines.append("end entity\n")
        return "\n".join(lines)

    def _generate_functions(self) -> str:
        lines = ["# --- Function Definitions ---"]
        if not self.model.functions: return ""
        for func_id, data in self.model.functions.items():
            lines.append(f"function {func_id}")
            lines.extend(self._generate_node_list_code(data.get("nodes", []), 1))
            lines.append("end function\n")
        return "\n".join(lines)
        
    def _generate_dialogs(self) -> str:
        lines = ["# --- Dialog Definitions ---"]
        if not self.model.dialogs: return ""
        for dialog_id, data in self.model.dialogs.items():
            lines.append(f"dialog {dialog_id}")
            lines.extend(self._generate_node_list_code(data.get("nodes", []), 1))
            lines.append("end dialog\n")
        return "\n".join(lines)

    def _generate_node_list_code(self, nodes: List[Dict], indent_level: int) -> List[str]:
        code, indent = [], "    " * indent_level
        for node in nodes:
            node_type = node.get("type")
            if node_type == "say": code.append(f"{indent}say \"{node.get('text', '')}\"")
            elif node_type == "set_quest": code.append(f"{indent}set quest {node.get('quest_id', '')} to {node.get('state', '')}")
            elif node_type == "give": code.append(f"{indent}give {node.get('count', 1)} {node.get('item_id', '?')}")
            elif node_type == "take": code.append(f"{indent}take {node.get('count', 1)} {node.get('item_id', '?')}")
            elif node_type == "call_function": code.append(f"{indent}call {node.get('name', '')}")
            elif node_type == "option":
                code.append(f"{indent}option \"{node.get('text', '')}\"")
                code.extend(self._generate_node_list_code(node.get("nodes", []), indent_level + 1))
                code.append(f"{indent}end option")
            elif node_type == "if":
                code.append(f"{indent}if {node.get('condition', 'true')}")
                child_nodes = node.get("nodes", [])
                else_marker_index = next((i for i, child in enumerate(child_nodes) if child.get("type") == "else_marker"), -1)
                
                if else_marker_index != -1:
                    code.extend(self._generate_node_list_code(child_nodes[:else_marker_index], indent_level + 1))
                    code.append(f"{indent}else")
                    code.extend(self._generate_node_list_code(child_nodes[else_marker_index+1:], indent_level + 1))
                else:
                    code.extend(self._generate_node_list_code(child_nodes, indent_level + 1))
                code.append(f"{indent}end")
        return code

# #########################################################################
# VIEW - The UI components for the application.
# #########################################################################

class BaseDataTab(ttk.Frame):
    """
    A base class for tabs that manage a list of data items (Entities, Items, Quests).
    """
    def __init__(self, parent: ttk.Notebook, model: ProjectModel, item_name: str, category: DataCategory):
        super().__init__(parent)
        self.model = model
        self.item_name = item_name
        self.category = category
        self.selected_id: Optional[str] = None
        self._new_item_counter: int = 0
        self.model.register_observer(self.update_view)
        self._setup_ui()

    def _setup_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')
        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=1)
        ttk.Label(list_frame, text=f"{self.item_name}s").pack(pady=5)
        self.listbox = tk.Listbox(list_frame, exportselection=False)
        self.listbox.pack(expand=True, fill='both', padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_item_select)
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text=f"Add {self.item_name}", command=self.add_item_inline).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(button_frame, text=f"Delete {self.item_name}", command=self.delete_item).pack(side='left', fill='x', expand=True, padx=2)
        self.details_frame = ttk.Frame(paned_window)
        paned_window.add(self.details_frame, weight=3)
        ttk.Label(self.details_frame, text=f"{self.item_name} Details").pack(pady=5)
        self._setup_details_frame()

    def update_view(self, update_type: str):
        if update_type in [f"{self.category.value}_update", "full_update"]:
            self.refresh_listbox()
    
    def refresh_listbox(self):
        current_selection = self.listbox.curselection()
        selected_id = self.listbox.get(current_selection[0]) if current_selection else None
        self.listbox.delete(0, tk.END)
        data_store = getattr(self.model, self.category.value)
        new_selection_index = -1
        for i, item_id in enumerate(sorted(data_store.keys())):
            self.listbox.insert(tk.END, item_id)
            if item_id == selected_id:
                new_selection_index = i
        if new_selection_index != -1:
            self.listbox.selection_set(new_selection_index)
            self.listbox.see(new_selection_index)
        else:
            self.clear_details_form()

    def add_item_inline(self):
        self._new_item_counter += 1
        data_store = getattr(self.model, self.category.value)
        temp_id = f"_new_{self.item_name.lower()}_{self._new_item_counter}"
        while temp_id in data_store:
            self._new_item_counter += 1
            temp_id = f"_new_{self.item_name.lower()}_{self._new_item_counter}"
        
        new_item_data = self._get_new_item_data_obj()
        self.model.add_data_item(self.category, temp_id, new_item_data)
        self.after(50, self._select_last_item)

    def _select_last_item(self):
        last_index = self.listbox.size() - 1
        if last_index >= 0:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(last_index)
            self.listbox.see(last_index)
            self.on_item_select(None)
            self._focus_on_main_field()

    def delete_item(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", f"No {self.item_name.lower()} selected to delete.")
            return
        item_id = self.listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{item_id}'?"):
            self.model.delete_data_item(self.category, item_id)
            self.clear_details_form()

    def on_item_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            self.clear_details_form()
            self.selected_id = None
            return
        self.selected_id = self.listbox.get(selection[0])
        self.update_details_form()

    def handle_id_change(self, new_id_var: tk.StringVar):
        new_id = new_id_var.get()
        if self.selected_id and self.selected_id != new_id:
            if not self.model.update_data_item_id(self.category, self.selected_id, new_id):
                new_id_var.set(self.selected_id)
            else:
                self.selected_id = new_id

    # --- Methods to be implemented by subclasses ---
    def _setup_details_frame(self): raise NotImplementedError
    def _get_new_item_data_obj(self) -> Any: raise NotImplementedError
    def update_details_form(self): raise NotImplementedError
    def clear_details_form(self): raise NotImplementedError
    def _focus_on_main_field(self): raise NotImplementedError


class EntitiesTab(BaseDataTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, item_name="Entity", category=DataCategory.ENTITIES)
        self._new_stat_counter = 0

    def update_view(self, update_type: str):
        """Override to also refresh details form on update."""
        if update_type in [f"{self.category.value}_update", "full_update"]:
            self.refresh_listbox()
            if self.selected_id:
                self.update_details_form()

    def _setup_details_frame(self):
        form_frame = ttk.Frame(self.details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        self.entity_id_var = tk.StringVar()
        self.id_entry = self._create_form_row(form_frame, "ID:", self.entity_id_var)
        self.id_entry.bind("<FocusOut>", lambda e: self.handle_id_change(self.entity_id_var))
        
        ttk.Label(self.details_frame, text="Stats").pack(pady=5)
        stats_frame = ttk.Frame(self.details_frame)
        stats_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.stats_tree = ttk.Treeview(stats_frame, columns=('Stat', 'Value'), show='headings')
        self.stats_tree.heading('Stat', text='Stat')
        self.stats_tree.heading('Value', text='Value')
        self.stats_tree.pack(expand=True, fill='both')
        self.stats_tree.bind("<Double-1>", self.on_tree_double_click)

        stats_button_frame = ttk.Frame(self.details_frame)
        stats_button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(stats_button_frame, text="Add Stat", command=self.add_stat).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(stats_button_frame, text="Remove Stat", command=self.remove_stat).pack(side='left', fill='x', expand=True, padx=2)

    def _edit_cell(self, item_id: str, column_index: int):
        """Programmatically starts editing a cell in the treeview."""
        if not item_id: return
        
        column_id = f"#{column_index + 1}"
        x, y, width, height = self.stats_tree.bbox(item_id, column_id)
        
        val = self.stats_tree.item(item_id, "values")[column_index]
        entry_var = tk.StringVar(value=val)
        entry = ttk.Entry(self.stats_tree, textvariable=entry_var)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def on_focus_out(event):
            new_value = entry_var.get()
            entry.destroy()
            
            current_values = list(self.stats_tree.item(item_id, "values"))
            old_stat_name = current_values[0]

            if column_index == 0: # Editing stat name
                # If name didn't change, do nothing
                if new_value == old_stat_name: return
                # Pass old name to model for rename operation
                self.model.update_entity_stat(self.selected_id, new_value, current_values[1], old_stat_name)
            else: # Editing stat value
                self.model.update_entity_stat(self.selected_id, old_stat_name, new_value)
        
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", on_focus_out)

    def on_tree_double_click(self, event):
        if self.stats_tree.identify_region(event.x, event.y) != "cell": return
        
        column_id = self.stats_tree.identify_column(event.x)
        column_index = int(column_id.replace('#', '')) - 1
        selected_iid = self.stats_tree.focus()

        self._edit_cell(selected_iid, column_index)

    def _create_form_row(self, parent, label_text, string_var):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
        entry = ttk.Entry(row, textvariable=string_var)
        entry.pack(side='left', expand=True, fill='x')
        return entry

    def _get_new_item_data_obj(self) -> Entity:
        return Entity()

    def _focus_on_main_field(self):
        self.id_entry.focus_set()
        self.id_entry.selection_range(0, tk.END)

    def update_details_form(self):
        if not self.selected_id: return
        self.entity_id_var.set(self.selected_id)
        
        # Preserve selection
        selected_stat_iid = self.stats_tree.focus()

        self.stats_tree.delete(*self.stats_tree.get_children())
        entity_obj = self.model.entities.get(self.selected_id)
        if entity_obj:
            for stat, value in sorted(entity_obj.stats.items()):
                self.stats_tree.insert('', tk.END, iid=stat, values=(stat, value))
        
        # Restore selection if it still exists
        if self.stats_tree.exists(selected_stat_iid):
            self.stats_tree.focus(selected_stat_iid)
            self.stats_tree.selection_set(selected_stat_iid)

    def clear_details_form(self):
        self.selected_id = None
        self.entity_id_var.set("")
        self.stats_tree.delete(*self.stats_tree.get_children())

    def add_stat(self):
        """Adds a new stat inline without a popup."""
        if not self.selected_id: return
        
        # 1. Create a unique temporary name for the new stat
        self._new_stat_counter += 1
        temp_stat_name = f"new_stat_{self._new_stat_counter}"
        while temp_stat_name in self.model.entities[self.selected_id].stats:
            self._new_stat_counter += 1
            temp_stat_name = f"new_stat_{self._new_stat_counter}"

        # 2. Add the temporary stat to the model, which triggers a view update
        if self.model.update_entity_stat(self.selected_id, temp_stat_name, "0"):
            # 3. After the UI has had a moment to update, find the new row and edit it
            self.after(50, self._trigger_edit_on_new_stat, temp_stat_name)
    
    def _trigger_edit_on_new_stat(self, stat_name: str):
        """Finds the new stat in the tree and starts the editing process."""
        new_item_id = None
        for iid in self.stats_tree.get_children():
            if self.stats_tree.item(iid, "values")[0] == stat_name:
                new_item_id = iid
                break
        
        if new_item_id:
            self.stats_tree.see(new_item_id)
            self.stats_tree.focus(new_item_id)
            self.stats_tree.selection_set(new_item_id)
            self._edit_cell(new_item_id, 0) # Edit the 'Stat' name column

    def remove_stat(self):
        if not self.selected_id or not self.stats_tree.selection(): return
        selected_item = self.stats_tree.selection()[0]
        stat_name = self.stats_tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm", f"Remove the stat '{stat_name}'?"):
            self.model.remove_entity_stat(self.selected_id, stat_name)


class ItemsTab(BaseDataTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, item_name="Item", category=DataCategory.ITEMS)
        self._new_prop_counter = 0

    def _setup_details_frame(self):
        form_frame = ttk.Frame(self.details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        self.item_id_var = tk.StringVar()
        self.id_entry = self._create_form_row(form_frame, "ID:", self.item_id_var)
        self.id_entry.bind("<FocusOut>", lambda e: self.handle_id_change(self.item_id_var))

        ttk.Label(self.details_frame, text="Properties").pack(pady=5)
        tree_frame = ttk.Frame(self.details_frame)
        tree_frame.pack(expand=True, fill='both', padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=('Property', 'Value'), show='headings')
        self.tree.heading('Property', text='Property')
        self.tree.heading('Value', text='Value')
        self.tree.pack(expand=True, fill='both')
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        button_frame = ttk.Frame(self.details_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Add Property", command=self.add_property).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(button_frame, text="Remove Property", command=self.remove_property).pack(side='left', fill='x', expand=True, padx=2)

    def _create_form_row(self, parent, label_text, string_var):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
        entry = ttk.Entry(row, textvariable=string_var)
        entry.pack(side='left', expand=True, fill='x')
        return entry

    def _get_new_item_data_obj(self) -> Item:
        return Item()

    def _focus_on_main_field(self):
        self.id_entry.focus_set()
        self.id_entry.selection_range(0, tk.END)

    def update_details_form(self):
        if not self.selected_id: return
        self.item_id_var.set(self.selected_id)
        
        selected_iid = self.tree.focus()
        self.tree.delete(*self.tree.get_children())
        item_obj = self.model.items.get(self.selected_id)
        if item_obj:
            for key, value in sorted(item_obj.properties.items()):
                self.tree.insert('', tk.END, iid=key, values=(key, value))

        if self.tree.exists(selected_iid):
            self.tree.focus(selected_iid)
            self.tree.selection_set(selected_iid)

    def clear_details_form(self):
        self.selected_id = None
        self.item_id_var.set("")
        self.tree.delete(*self.tree.get_children())

    def add_property(self):
        if not self.selected_id: return
        self._new_prop_counter += 1
        temp_key = f"new_property_{self._new_prop_counter}"
        while temp_key in self.model.items[self.selected_id].properties:
            self._new_prop_counter += 1
            temp_key = f"new_property_{self._new_prop_counter}"

        self.model.items[self.selected_id].properties[temp_key] = " "
        self.model._mark_dirty()
        self.update_details_form()
        self.after(50, self._trigger_edit_on_new, temp_key)

    def _trigger_edit_on_new(self, key: str):
        if self.tree.exists(key):
            self.tree.see(key)
            self.tree.focus(key)
            self.tree.selection_set(key)
            self._edit_cell(key, 0)

    def remove_property(self):
        if not self.selected_id or not self.tree.selection(): return
        selected_item = self.tree.selection()[0]
        key_to_remove = self.tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm", f"Remove the property '{key_to_remove}'?"):
            del self.model.items[self.selected_id].properties[key_to_remove]
            self.model._mark_dirty()
            self.update_details_form()

    def on_tree_double_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        column_id = self.tree.identify_column(event.x)
        column_index = int(column_id.replace('#', '')) - 1
        selected_iid = self.tree.focus()
        self._edit_cell(selected_iid, column_index)

    def _edit_cell(self, item_id: str, column_index: int):
        if not item_id: return
        x, y, width, height = self.tree.bbox(item_id, f"#{column_index + 1}")
        val = self.tree.item(item_id, "values")[column_index]
        entry_var = tk.StringVar(value=val)
        entry = ttk.Entry(self.tree, textvariable=entry_var)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def on_focus_out(event):
            new_value = entry_var.get()
            entry.destroy()
            current_values = list(self.tree.item(item_id, "values"))
            old_key = current_values[0]

            item_properties = self.model.items[self.selected_id].properties

            if column_index == 0: # Key changed
                if new_value != old_key:
                    if new_value in item_properties:
                        messagebox.showerror("Error", f"Property '{new_value}' already exists.")
                        return
                    item_properties[new_value] = current_values[1]
                    del item_properties[old_key]
            else: # Value changed
                item_properties[old_key] = new_value

            self.model._mark_dirty()
            self.update_details_form()

        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", on_focus_out)


class QuestsTab(BaseDataTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, item_name="Quest", category=DataCategory.QUESTS)
        
    def _setup_details_frame(self):
        form_frame = ttk.Frame(self.details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        self.quest_id_var = tk.StringVar()
        self.quest_name_var = tk.StringVar()
        self.quest_desc_var = tk.StringVar()
        self.quest_state_var = tk.StringVar()
        self.id_entry = self._create_form_row(form_frame, "ID:", self.quest_id_var)
        self.id_entry.bind("<FocusOut>", lambda e: self.handle_id_change(self.quest_id_var))
        self._create_form_row(form_frame, "Name:", self.quest_name_var)
        self._create_form_row(form_frame, "Description:", self.quest_desc_var)
        self._create_combobox_row(form_frame, "State:", self.quest_state_var, ['inactive', 'active', 'completed'])
        for var in [self.quest_name_var, self.quest_desc_var, self.quest_state_var]:
            var.trace_add("write", self.update_quest_details)

    def _create_form_row(self, parent, label_text, string_var):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
        entry = ttk.Entry(row, textvariable=string_var)
        entry.pack(side='left', expand=True, fill='x')
        return entry

    def _create_combobox_row(self, parent, label_text, string_var, values):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
        combo = ttk.Combobox(row, textvariable=string_var, values=values, state='readonly')
        combo.pack(side='left', expand=True, fill='x')
        return combo

    def _get_new_item_data_obj(self) -> Quest:
        return Quest()

    def _focus_on_main_field(self):
        self.id_entry.focus_set()
        self.id_entry.selection_range(0, tk.END)

    def _manage_trace(self, action: str):
        for var in [self.quest_name_var, self.quest_desc_var, self.quest_state_var]:
            try:
                trace_info = var.trace_info()
                if trace_info:
                    if action == 'add':
                        var.trace_add("write", self.update_quest_details)
                    elif action == 'remove':
                        var.trace_vdelete("w", trace_info[0][1])
            except (IndexError, tk.TclError):
                pass
            
    def update_details_form(self):
        if not self.selected_id or self.selected_id not in self.model.quests: return
        self._manage_trace('remove')
        quest_obj = self.model.quests[self.selected_id]
        self.quest_id_var.set(self.selected_id)
        self.quest_name_var.set(quest_obj.name)
        self.quest_desc_var.set(quest_obj.description)
        self.quest_state_var.set(quest_obj.state)
        self._manage_trace('add')

    def update_quest_details(self, *args):
        if not self.selected_id or self.selected_id not in self.model.quests: return
        new_data_obj = Quest(
            name=self.quest_name_var.get(),
            description=self.quest_desc_var.get(),
            state=self.quest_state_var.get()
        )
        self.model.update_data_item_details(self.category, self.selected_id, new_data_obj)

    def clear_details_form(self):
        self.selected_id = None
        self._manage_trace('remove')
        self.quest_id_var.set("")
        self.quest_name_var.set("")
        self.quest_desc_var.set("")
        self.quest_state_var.set("")


class BaseLogicTab(ttk.Frame):
    """
    A base class for tabs that manage nested logic nodes (Functions, Dialogs).
    """
    def __init__(self, parent: ttk.Notebook, model: ProjectModel, root_name: str, category: DataCategory):
        super().__init__(parent)
        self.model = model
        self.root_name = root_name
        self.category = category
        self.allowed_node_types: List[str] = ["say", "give", "take", "set_quest", "call_function", "if"]

        self._new_item_counter: int = 0
        self.node_map: Dict[str, Any] = {}
        self.selected_node_id: Optional[str] = None
        self.property_vars: List[tk.Variable] = []

        self.model.register_observer(self.update_view)
        self._setup_ui()
    
    def _setup_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')
        tree_container = ttk.Frame(paned_window)
        paned_window.add(tree_container, weight=2)
        
        top_controls = ttk.Frame(tree_container)
        top_controls.pack(fill='x', padx=5, pady=5)
        ttk.Button(top_controls, text=f"Add {self.root_name}", command=self.add_root_item).pack(side='left')
        
        self.tree = ttk.Treeview(tree_container, show='tree')
        self.tree.column("#0", minwidth=200, stretch=tk.YES)
        self.tree.pack(expand=True, fill='both', padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_node_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.properties_frame = ttk.Frame(paned_window)
        paned_window.add(self.properties_frame, weight=1)

    def update_view(self, update_type: str):
        if update_type in [f"{self.category.value}_update", "full_update"]:
            self.refresh_tree_from_data()

    def refresh_tree_from_data(self):
        selected_id = self.tree.selection()[0] if self.tree.selection() else None
        self.tree.delete(*self.tree.get_children())
        self.node_map.clear()
        
        data_store = self.model._get_data_store(self.category)
        
        for item_id, item_data in sorted(data_store.items()):
            self.node_map[item_id] = item_data
            self.tree.insert('', 'end', iid=item_id, text=f"{self.root_name}: {item_id}", open=True, tags=('root_node',))
            self._populate_tree(item_id, item_data.get("nodes", []))
        
        if selected_id and self.tree.exists(selected_id):
            self.tree.selection_set(selected_id)
            self.tree.focus(selected_id)
            self.tree.see(selected_id)
        else:
            self.clear_properties_panel()
    
    def _populate_tree(self, parent_iid: str, nodes: List[Dict]):
        for node in nodes:
            node_id = node.get("id")
            if not node_id: continue 
            display_text = self._get_node_display_text(node)
            self.tree.insert(parent_iid, 'end', iid=node_id, text=display_text, open=True)
            self.node_map[node_id] = node
            
            if node.get("type") == "if":
                child_nodes = node.get("nodes", [])
                else_marker_index = next((i for i, child in enumerate(child_nodes) if child.get("type") == "else_marker"), -1)
                
                if else_marker_index != -1:
                    self._populate_tree(node_id, child_nodes[:else_marker_index])
                    else_id = child_nodes[else_marker_index]["id"]
                    self.tree.insert(node_id, 'end', iid=else_id, text="ELSE")
                    self.node_map[else_id] = child_nodes[else_marker_index]
                    self._populate_tree(node_id, child_nodes[else_marker_index+1:])
                else:
                    if "nodes" in node: self._populate_tree(node_id, node.get("nodes", []))
            elif "nodes" in node:
                self._populate_tree(node_id, node.get("nodes", []))

    def _get_node_display_text(self, node: Dict) -> str:
        """Generates a readable string for a node to display in the tree."""
        ntype = node.get("type")
        if ntype == "say": return f"Say: \"{node.get('text', '')[:30]}...\""
        if ntype == "give": return f"Give {node.get('count', 1)} x {node.get('item_id', '?')}"
        if ntype == "take": return f"Take {node.get('count', 1)} x {node.get('item_id', '?')}"
        if ntype == "set_quest": return f"Set Quest {node.get('quest_id', '?')} to {node.get('state', '?')}"
        if ntype == "call_function": return f"Call Function: {node.get('name', '?')}"
        if ntype == "if": return f"If: {node.get('condition', '')}"
        if ntype == "option": return f"Option: \"{node.get('text', '')[:30]}...\""
        return node.get("type", "Unknown Node").replace("_", " ").title()

    def on_node_select(self, event):
        self.clear_properties_panel()
        selection = self.tree.selection()
        if not selection: 
            self.selected_node_id = None
            return
        self.selected_node_id = selection[0]
        self.build_properties_panel()
        
    def build_properties_panel(self):
        """Creates the property editor widgets for the selected node."""
        if not self.selected_node_id: return
        
        node_data = self.node_map.get(self.selected_node_id)
        if not node_data: return

        root_id = self._get_selected_root_id()
        if not root_id: return
        
        # Callback to save changes from the UI
        def save_changes(prop_name: str, var: tk.Variable):
            self.model.update_logic_node_properties(self.category, root_id, self.selected_node_id, {prop_name: var.get()})
        
        def finalize_changes(event):
            self.model.mark_logic_dirty(self.category)

        node_type = node_data.get("type")
        
        # Build UI based on node type
        if node_type == "say" or node_type == "option":
            self._create_property_editor("text", node_data, save_changes, finalize_changes, widget_type='entry')
        elif node_type == "if":
            self._create_property_editor("condition", node_data, save_changes, finalize_changes, widget_type='entry')
        elif node_type == "give" or node_type == "take":
            self._create_property_editor("count", node_data, save_changes, finalize_changes, widget_type='entry')
            self._create_property_editor("item_id", node_data, save_changes, finalize_changes, widget_type='combo', options=list(self.model.items.keys()))
        elif node_type == "set_quest":
            self._create_property_editor("quest_id", node_data, save_changes, finalize_changes, widget_type='combo', options=list(self.model.quests.keys()))
            self._create_property_editor("state", node_data, save_changes, finalize_changes, widget_type='combo', options=['inactive', 'active', 'completed'])
        elif node_type == "call_function":
            self._create_property_editor("name", node_data, save_changes, finalize_changes, widget_type='combo', options=list(self.model.functions.keys()))

    def _create_property_editor(self, prop_name: str, node_data: Dict, save_callback, final_callback, widget_type:str, options:Optional[List[str]] = None):
        """Helper to create a label and widget for a single property."""
        frame = ttk.Frame(self.properties_frame)
        frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(frame, text=f"{prop_name.replace('_', ' ').title()}:", width=12).pack(side='left')
        
        var = tk.StringVar(value=node_data.get(prop_name, ""))
        self.property_vars.append(var)
        var.trace_add('write', lambda *args, p=prop_name, v=var: save_callback(p, v))

        widget = None
        if widget_type == 'entry':
            widget = ttk.Entry(frame, textvariable=var)
        elif widget_type == 'combo' and options is not None:
            widget = ttk.Combobox(frame, textvariable=var, values=options, state='readonly')
        
        if widget:
            widget.pack(side='left', fill='x', expand=True)
            widget.bind("<FocusOut>", final_callback)

    def show_context_menu(self, event):
        """Displays a right-click context menu on the tree."""
        selection = self.tree.identify_row(event.y)
        if not selection: return
        self.tree.selection_set(selection)
        
        node_data = self.node_map.get(selection, {})
        node_type = node_data.get("type", "root")
        
        menu = tk.Menu(self, tearoff=0)
        
        # Populate add options
        can_have_children = "nodes" in node_data or node_type == "root"
        if can_have_children:
            for ntype in self.allowed_node_types:
                menu.add_command(label=f"Add {ntype.replace('_',' ').title()}", command=lambda nt=ntype: self.add_new_node(nt))
            
            if node_type == "if" and not any(n.get("type") == "else_marker" for n in node_data.get("nodes", [])):
                menu.add_separator()
                menu.add_command(label="Add Else", command=lambda: self.add_new_node("else_marker"))

        # Delete option
        menu.add_separator()
        menu.add_command(label="Delete Node", command=self.delete_selected_node)
        
        menu.tk_popup(event.x_root, event.y_root)

    def add_new_node(self, node_type: str):
        if not self.selected_node_id: return
        
        root_id = self._get_selected_root_id()
        if not root_id: return
        
        new_node_id = self.model.get_next_node_id(self.category)
        
        # Default data structures for new nodes
        new_node_data = {"id": new_node_id, "type": node_type}
        if node_type in ["if", "option"]: new_node_data["nodes"] = []
        if node_type == "say" or node_type == "option": new_node_data["text"] = ""
        if node_type == "if": new_node_data["condition"] = "true"
        if node_type == "give" or node_type == "take":
            new_node_data["count"] = 1
            new_node_data["item_id"] = ""
        if node_type == "set_quest":
            new_node_data["quest_id"] = ""
            new_node_data["state"] = "active"
        if node_type == "call_function": new_node_data["name"] = ""

        self.model.add_logic_node(self.category, root_id, self.selected_node_id, new_node_data)

    def delete_selected_node(self):
        if not self.selected_node_id: return
        root_id = self._get_selected_root_id()
        if not root_id: return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the selected node and all its children?"):
            self.model.delete_logic_node(self.category, root_id, self.selected_node_id)
            self.clear_properties_panel()

    def clear_properties_panel(self):
        self.property_vars.clear()
        for widget in self.properties_frame.winfo_children():
            widget.destroy()

    def add_root_item(self):
        self._new_item_counter += 1
        data_store = self.model._get_data_store(self.category)
        temp_id = f"_new_{self.root_name.lower()}_{self._new_item_counter}"
        while temp_id in data_store:
            self._new_item_counter += 1
            temp_id = f"_new_{self.root_name.lower()}_{self._new_item_counter}"
        
        new_data = {"type": self.root_name.lower(), "id": temp_id, "nodes": []}
        self.model.add_data_item(self.category, temp_id, new_data)
        self.after(50, self._trigger_edit_on_new_item, temp_id)

    def _trigger_edit_on_new_item(self, item_id: str):
        if self.tree.exists(item_id):
            self.tree.see(item_id)
            self.tree.focus(item_id)
            self.tree.selection_set(item_id)
            self._edit_cell(item_id)

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id or self.tree.identify_region(event.x, event.y) != 'tree': return
        
        # Only allow editing root nodes this way
        if item_id in self.model._get_data_store(self.category):
            self._edit_cell(item_id)

    def _edit_cell(self, item_id: str):
        if not self.tree.exists(item_id): return
        
        x, y, width, height = self.tree.bbox(item_id, '#0')
        prefix_len = len(f"{self.root_name}: ")
        original_text = self.tree.item(item_id, "text")[prefix_len:]

        entry_var = tk.StringVar(value=original_text)
        entry = ttk.Entry(self.tree, textvariable=entry_var)
        entry.place(x=x, y=y, width=width, height=height)
        
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def on_commit(event):
            new_id = entry_var.get()
            entry.destroy()
            if item_id != new_id:
                self.model.update_data_item_id(self.category, item_id, new_id)
        
        entry.bind("<FocusOut>", on_commit)
        entry.bind("<Return>", on_commit)

    def _get_selected_root_id(self) -> Optional[str]:
        """Traverses up the tree to find the top-level root ID."""
        if not self.selected_node_id: return None
        
        current_id = self.selected_node_id
        while current_id:
            if current_id in self.model._get_data_store(self.category):
                return current_id
            current_id = self.tree.parent(current_id)
        return None

class FunctionsTab(BaseLogicTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, root_name="Function", category=DataCategory.FUNCTIONS)

class DialogsTab(BaseLogicTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, root_name="Dialog", category=DataCategory.DIALOGS)
        self.allowed_node_types.append("option")


class StringListsTab(BaseDataTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, item_name="String List", category=DataCategory.STRING_LISTS)

    def _setup_details_frame(self):
        form_frame = ttk.Frame(self.details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        self.list_id_var = tk.StringVar()
        self.id_entry = self._create_form_row(form_frame, "ID:", self.list_id_var)
        self.id_entry.bind("<FocusOut>", lambda e: self.handle_id_change(self.list_id_var))

        ttk.Label(self.details_frame, text="Values (one per line)").pack(pady=5)
        self.text_widget = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, height=10)
        self.text_widget.pack(expand=True, fill='both', padx=5, pady=5)
        self.text_widget.bind("<<Modified>>", self.on_text_modified)

    def _create_form_row(self, parent, label_text, string_var):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
        entry = ttk.Entry(row, textvariable=string_var)
        entry.pack(side='left', expand=True, fill='x')
        return entry

    def _get_new_item_data_obj(self):
        return []

    def _focus_on_main_field(self):
        self.id_entry.focus_set()
        self.id_entry.selection_range(0, tk.END)

    def update_details_form(self):
        if not self.selected_id or self.selected_id not in self.model.string_lists:
            self.clear_details_form()
            return

        self.list_id_var.set(self.selected_id)
        list_data = self.model.string_lists[self.selected_id]

        # Temporarily disable the modified event to prevent feedback loop
        self.text_widget.unbind("<<Modified>>")
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', "\n".join(list_data))
        self.text_widget.edit_modified(False) # Reset modified flag
        self.text_widget.bind("<<Modified>>", self.on_text_modified)

    def clear_details_form(self):
        self.selected_id = None
        self.list_id_var.set("")
        self.text_widget.unbind("<<Modified>>")
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.edit_modified(False)
        self.text_widget.bind("<<Modified>>", self.on_text_modified)

    def on_text_modified(self, event):
        if not self.selected_id: return

        content = self.text_widget.get('1.0', tk.END).strip()
        new_list_data = [line for line in content.split("\n") if line.strip()]

        # Directly update the model without using the generic update method
        self.model.string_lists[self.selected_id] = new_list_data
        self.model._mark_dirty()

        # Reset the modified flag to allow future events
        self.text_widget.edit_modified(False)


class DictionariesTab(BaseDataTab):
    def __init__(self, parent: ttk.Notebook, model: ProjectModel):
        super().__init__(parent, model, item_name="Dictionary", category=DataCategory.DICTIONARIES)
        self._new_key_counter = 0

    def update_view(self, update_type: str):
        if update_type in [f"{self.category.value}_update", "full_update"]:
            self.refresh_listbox()
            if self.selected_id:
                self.update_details_form()

    def _setup_details_frame(self):
        form_frame = ttk.Frame(self.details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        self.dict_id_var = tk.StringVar()
        self.id_entry = self._create_form_row(form_frame, "ID:", self.dict_id_var)
        self.id_entry.bind("<FocusOut>", lambda e: self.handle_id_change(self.dict_id_var))

        ttk.Label(self.details_frame, text="Key-Value Pairs").pack(pady=5)
        tree_frame = ttk.Frame(self.details_frame)
        tree_frame.pack(expand=True, fill='both', padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=('Key', 'Value'), show='headings')
        self.tree.heading('Key', text='Key')
        self.tree.heading('Value', text='Value')
        self.tree.pack(expand=True, fill='both')
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        button_frame = ttk.Frame(self.details_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Add Pair", command=self.add_pair).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(button_frame, text="Remove Pair", command=self.remove_pair).pack(side='left', fill='x', expand=True, padx=2)

    def _create_form_row(self, parent, label_text, string_var):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
        entry = ttk.Entry(row, textvariable=string_var)
        entry.pack(side='left', expand=True, fill='x')
        return entry

    def _get_new_item_data_obj(self):
        return {}

    def _focus_on_main_field(self):
        self.id_entry.focus_set()
        self.id_entry.selection_range(0, tk.END)

    def update_details_form(self):
        if not self.selected_id: return
        self.dict_id_var.set(self.selected_id)

        selected_iid = self.tree.focus()
        self.tree.delete(*self.tree.get_children())
        dict_obj = self.model.dictionaries.get(self.selected_id)
        if dict_obj:
            for key, value in sorted(dict_obj.items()):
                self.tree.insert('', tk.END, iid=key, values=(key, value))

        if self.tree.exists(selected_iid):
            self.tree.focus(selected_iid)
            self.tree.selection_set(selected_iid)

    def clear_details_form(self):
        self.selected_id = None
        self.dict_id_var.set("")
        self.tree.delete(*self.tree.get_children())

    def add_pair(self):
        if not self.selected_id: return
        self._new_key_counter += 1
        temp_key = f"new_key_{self._new_key_counter}"
        while temp_key in self.model.dictionaries[self.selected_id]:
            self._new_key_counter += 1
            temp_key = f"new_key_{self._new_key_counter}"

        self.model.dictionaries[self.selected_id][temp_key] = "0"
        self.model._mark_dirty()
        self.update_details_form()
        self.after(50, self._trigger_edit_on_new_pair, temp_key)

    def _trigger_edit_on_new_pair(self, key: str):
        if self.tree.exists(key):
            self.tree.see(key)
            self.tree.focus(key)
            self.tree.selection_set(key)
            self._edit_cell(key, 0)

    def remove_pair(self):
        if not self.selected_id or not self.tree.selection(): return
        selected_item = self.tree.selection()[0]
        key_to_remove = self.tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm", f"Remove the key '{key_to_remove}'?"):
            del self.model.dictionaries[self.selected_id][key_to_remove]
            self.model._mark_dirty()
            self.update_details_form()

    def on_tree_double_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        column_id = self.tree.identify_column(event.x)
        column_index = int(column_id.replace('#', '')) - 1
        selected_iid = self.tree.focus()
        self._edit_cell(selected_iid, column_index)

    def _edit_cell(self, item_id: str, column_index: int):
        if not item_id: return
        x, y, width, height = self.tree.bbox(item_id, f"#{column_index + 1}")
        val = self.tree.item(item_id, "values")[column_index]
        entry_var = tk.StringVar(value=val)
        entry = ttk.Entry(self.tree, textvariable=entry_var)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def on_focus_out(event):
            new_value = entry_var.get()
            entry.destroy()
            current_values = list(self.tree.item(item_id, "values"))
            old_key = current_values[0]

            if column_index == 0: # Key changed
                if new_value != old_key:
                    if new_value in self.model.dictionaries[self.selected_id]:
                        messagebox.showerror("Error", f"Key '{new_value}' already exists.")
                        return
                    self.model.dictionaries[self.selected_id][new_value] = current_values[1]
                    del self.model.dictionaries[self.selected_id][old_key]
            else: # Value changed
                self.model.dictionaries[self.selected_id][old_key] = new_value

            self.model._mark_dirty()
            self.update_details_form()

        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", on_focus_out)


# #########################################################################
# CONTROLLER - The main application window that orchestrates everything.
# #########################################################################

class App(tk.Tk):
    """The main application window (Controller)."""
    def __init__(self):
        super().__init__()
        self.title("LDScript Visual Editor")
        self.geometry("1200x800")
        self.project_model = ProjectModel()
        self.project_model.register_observer(self.update_app_view)
        self._setup_menu()
        self._setup_notebook()
        self._setup_statusbar()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.update_app_view("app_update") # Initial title set

    def _setup_menu(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Import .ld File...", command=self.import_ld_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save Project As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        game_menu = tk.Menu(self.menu_bar, tearoff=0)
        game_menu.add_command(label="Generate main.ld File", command=self.generate_code)
        game_menu.add_command(label="Run Game", command=self.run_game)
        self.menu_bar.add_cascade(label="Game", menu=game_menu)
        
    def _setup_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        self.notebook.add(EntitiesTab(self.notebook, self.project_model), text="Entities")
        self.notebook.add(ItemsTab(self.notebook, self.project_model), text="Items")
        self.notebook.add(QuestsTab(self.notebook, self.project_model), text="Quests")
        self.notebook.add(StringListsTab(self.notebook, self.project_model), text="String Lists")
        self.notebook.add(DictionariesTab(self.notebook, self.project_model), text="Dictionaries")
        self.notebook.add(FunctionsTab(self.notebook, self.project_model), text="Functions")
        self.notebook.add(DialogsTab(self.notebook, self.project_model), text="Dialogs & Logic")
        
    def _setup_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_app_view(self, update_type: str):
        if update_type == "app_update":
            dirty_char = "*" if self.project_model.is_dirty else ""
            filename = self.project_model.filepath.name if self.project_model.filepath else "Untitled"
            self.title(f"{filename}{dirty_char} - LDScript Visual Editor")

    def _check_unsaved_changes(self) -> bool:
        if not self.project_model.is_dirty:
            return True
        response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them?")
        if response is True: return self.save_project()
        return response is False

    def new_project(self):
        if self._check_unsaved_changes():
            self.project_model.new_project()
            self.show_status("New project created.")

    def open_project(self):
        if not self._check_unsaved_changes(): return
        filepath = filedialog.askopenfilename(filetypes=[("LDScript Project Files", "*.json")])
        if not filepath: return
        try:
            self.project_model.load_project(filepath)
            self.show_status(f"Project loaded: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")
            self.project_model.new_project()

    def import_ld_project(self):
        if not self._check_unsaved_changes():
            return
        filepath = filedialog.askopenfilename(
            title="Import .ld File",
            filetypes=[("LDScript Files", "*.ld"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            parser = LdParser()
            parsed_data = parser.parse(filepath)

            # This method will be created in the next step
            self.project_model.load_from_parsed_ld(parsed_data)

            self.show_status(f"Successfully imported {filepath}")
            # Mark as dirty so the user is prompted to save it in the editor's format
            self.project_model._mark_dirty()
            # Clear the filepath so "Save" prompts for a new .json file location
            self.project_model.filepath = None
            self.update_app_view("app_update")

        except (FileNotFoundError, SyntaxError) as e:
            messagebox.showerror("Import Error", f"Failed to import file: {e}")
        except Exception as e:
            messagebox.showerror("Import Error", f"An unexpected error occurred: {e}")
            self.project_model.new_project() # Reset on critical failure

    def save_project(self) -> bool:
        if not self.project_model.filepath:
            return self.save_project_as()
        try:
            self.project_model.save_project()
            self.show_status(f"Project saved: {self.project_model.filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")
            return False

    def save_project_as(self) -> bool:
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("LDScript Project Files", "*.json")])
        if filepath:
            try:
                self.project_model.save_project(filepath)
                self.show_status(f"Project saved to: {filepath}")
                return True
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file: {e}")
        return False

    def generate_code(self):
        generator = LdCodeGenerator(self.project_model)
        final_code = generator.generate()
        if not final_code.strip():
            messagebox.showerror("Error", "Nothing to generate.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".ld", filetypes=[("LDScript Files", "*.ld")])
        if filepath:
            Path(filepath).write_text(final_code)
            self.show_status(f"Code successfully generated at: {filepath}")

    def run_game(self):
        generator = LdCodeGenerator(self.project_model)
        script_code = generator.generate()
        if not script_code.strip():
            messagebox.showerror("Error", "There is no game logic to run.")
            return
        temp_filepath = APP_ROOT / "temp_main.ld"
        temp_filepath.write_text(script_code)
        self._show_game_console(str(temp_filepath))

    def _show_game_console(self, filepath_to_run):
        """Opens a new terminal to run the game, handling different platforms."""
        command = [sys.executable, str(APP_ROOT / "ldscript_interpreter.py"), filepath_to_run]

        console_window = tk.Toplevel(self)
        console_window.title("Game Console")
        console_window.geometry("800x600")

        text_area = scrolledtext.ScrolledText(console_window, wrap=tk.WORD, bg="black", fg="white")
        text_area.pack(expand=True, fill='both')
        text_area.configure(state='disabled')

        def run_in_thread():
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read stdout
            for line in iter(process.stdout.readline, ''):
                self.after(0, lambda l=line: update_text(l))

            # Read stderr
            for line in iter(process.stderr.readline, ''):
                 self.after(0, lambda l=line: update_text(l, is_error=True))

            process.stdout.close()
            process.stderr.close()
            process.wait()
            self.after(0, lambda: update_text("\n--- SCRIPT FINISHED ---"))

        def update_text(line, is_error=False):
            text_area.configure(state='normal')
            if is_error:
                text_area.insert(tk.END, line, 'error')
            else:
                text_area.insert(tk.END, line)
            text_area.see(tk.END)
            text_area.configure(state='disabled')

        text_area.tag_config('error', foreground='red')

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def show_status(self, message: str, duration_ms: int = 4000):
        self.status_var.set(message)
        self.after(duration_ms, lambda: self.status_var.set("Ready"))

    def _on_closing(self):
        if self._check_unsaved_changes():
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
