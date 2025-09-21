import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import json
import subprocess
import threading
import queue
import os
import sys
from tkinter import scrolledtext
from ld_parser import LdParser

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LDScript Visual Editor")
        self.geometry("1200x800")

        # Create main menu
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New Project", command=self.new_project)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open Project", command=self.open_project)
        self.file_menu.add_command(label="Save Project", command=self.save_project)
        self.file_menu.add_command(label="Import .ld File", command=self.import_ld_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Game menu
        self.game_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.game_menu.add_command(label="Generate main.ld File", command=self.generate_code)
        self.game_menu.add_command(label="Run Game", command=self.run_game)
        self.menu_bar.add_cascade(label="Game", menu=self.game_menu)

        # Create the tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create and add the functional tabs
        self.entities_tab = EntitiesTab(self.notebook)
        self.notebook.add(self.entities_tab, text="Entities")

        self.items_tab = ItemsTab(self.notebook)
        self.notebook.add(self.items_tab, text="Items")

        self.quests_tab = QuestsTab(self.notebook)
        self.notebook.add(self.quests_tab, text="Quests")

        self.functions_tab = FunctionsTab(self.notebook, self)
        self.notebook.add(self.functions_tab, text="Functions")

        self.dialogs_tab = DialogsTab(self.notebook, self)
        self.notebook.add(self.dialogs_tab, text="Dialogs & Logic")

    def new_project(self):
        if messagebox.askyesno("New Project", "Are you sure you want to start a new project?\nAll unsaved changes will be lost."):
            self.entities_tab.clear_data()
            self.items_tab.clear_data()
            self.quests_tab.clear_data()
            self.functions_tab.clear_data()
            self.dialogs_tab.clear_data()

    def open_project(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("LDScript Project Files", "*.json"), ("All Files", "*.*")],
            title="Open Project"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                project_data = json.load(f)

            self.entities_tab.load_data(project_data.get("entities", {}))
            self.items_tab.load_data(project_data.get("items", {}))
            self.quests_tab.load_data(project_data.get("quests", {}))
            self.functions_tab.load_data(
                project_data.get("functions", {}),
                project_data.get("functions_node_counter", 0)
            )
            self.dialogs_tab.load_data(
                project_data.get("dialogs", {}),
                project_data.get("dialogs_node_counter", 0)
            )
            messagebox.showinfo("Success", "Project loaded successfully.")

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid project file. Could not decode JSON.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")

    def save_project(self):
        project_data = {
            "entities": self.entities_tab.entities_data,
            "items": self.items_tab.items_data,
            "quests": self.quests_tab.quests_data,
            "functions": self.functions_tab.functions_data,
            "dialogs": self.dialogs_tab.dialogs_data,
            "dialogs_node_counter": self.dialogs_tab.node_counter,
            "functions_node_counter": self.functions_tab.node_counter,
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("LDScript Project Files", "*.json"), ("All Files", "*.*")],
            title="Save Project"
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(project_data, f, indent=4)
                messagebox.showinfo("Success", "Project saved successfully.")
            except TypeError as e:
                messagebox.showerror("Error", f"Could not serialize project data: {e}")
            except IOError as e:
                messagebox.showerror("Error", f"Could not save project file: {e}")

    def import_ld_file(self):
        if not messagebox.askyesno("Confirm Import", "Importing a .ld file will overwrite the current project.\nAre you sure you want to continue?"):
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("LDScript Files", "*.ld"), ("All Files", "*.*")],
            title="Import .ld File"
        )
        if not filepath:
            return

        try:
            parser = LdParser()
            project_data = parser.parse(filepath)

            # Clear existing data
            self.entities_tab.clear_data()
            self.items_tab.clear_data()
            self.quests_tab.clear_data()
            self.functions_tab.clear_data()
            self.dialogs_tab.clear_data()

            # Load new data
            self.entities_tab.load_data(project_data.get("entities", {}))
            self.items_tab.load_data(project_data.get("items", {}))
            self.quests_tab.load_data(project_data.get("quests", {}))

            # For functions and dialogs, the node counter will be rebuilt during the load
            self.functions_tab.load_data(project_data.get("functions", {}), 0)
            self.dialogs_tab.load_data(project_data.get("dialogs", {}), 0)

            messagebox.showinfo("Success", "Successfully imported .ld file.")

        except (SyntaxError, FileNotFoundError) as e:
            messagebox.showerror("Import Error", f"Failed to import file:\n{e}")
        except Exception as e:
            messagebox.showerror("Import Error", f"An unexpected error occurred: {e}")

    def generate_code(self):
        final_code = self._get_generated_code()
        if not final_code:
            messagebox.showerror("Error", "Nothing to generate.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".ld",
            filetypes=[("LDScript Files", "*.ld"), ("All Files", "*.*")],
            title="Save Generated Code"
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(final_code)
                messagebox.showinfo("Success", f"Code successfully generated at:\n{filepath}")
            except IOError as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def _get_generated_code(self):
        code = []

        code.append("# --- Item Definitions ---")
        for item_id, item_data in self.items_tab.items_data.items():
            code.append(f"item {item_id}")
            code.append(f"    name \"{item_data.get('name', '')}\"")
            code.append(f"    description \"{item_data.get('description', '')}\"")
            code.append(f"    price {item_data.get('price', 0)}")
            code.append("end item\n")

        code.append("# --- Quest Definitions ---")
        for quest_id, quest_data in self.quests_tab.quests_data.items():
            code.append(f"quest {quest_id} \"{quest_data.get('name', '')}\"")
            code.append(f"    description \"{quest_data.get('description', '')}\"")
            code.append(f"    state {quest_data.get('state', 'inactive')}")
            code.append("end quest\n")

        code.append("# --- Entity Definitions ---")
        for entity_id, entity_data in self.entities_tab.entities_data.items():
            code.append(f"entity {entity_id}")
            for stat, value in entity_data.get("stats", {}).items():
                if isinstance(value, str) and not value.isnumeric():
                    code.append(f"    stat {stat} \"{value}\"")
                else:
                    code.append(f"    stat {stat} {value}")
            code.append("end entity\n")

        code.append("# --- Function Definitions ---")
        for func_id, func_data in self.functions_tab.functions_data.items():
            code.append(f"function {func_id}")
            code.extend(self._generate_node_list_code(func_data.get("nodes", []), 1))
            code.append("end function\n")

        code.append("# --- Dialog Definitions ---")
        for dialog_id, dialog_data in self.dialogs_tab.dialogs_data.items():
            code.append(f"dialog {dialog_id}")
            code.extend(self._generate_node_list_code(dialog_data.get("nodes", []), 1))
            code.append("end dialog\n")

        return "\n".join(code)

    def _generate_node_list_code(self, nodes, indent_level):
        code = []
        indent = "    " * indent_level
        for node in nodes:
            node_type = node.get("type")
            if node_type == "say":
                code.append(f"{indent}say \"{node.get('text', '')}\"")
            elif node_type == "set_quest":
                code.append(f"{indent}set quest {node.get('quest_id', '')} to {node.get('state', '')}")
            elif node_type == "give":
                code.append(f"{indent}give {node.get('count', 1)} {node.get('item_id', '?')}")
            elif node_type == "take":
                code.append(f"{indent}take {node.get('count', 1)} {node.get('item_id', '?')}")
            elif node_type == "call_function":
                code.append(f"{indent}call {node.get('name', '')}")
            elif node_type == "option":
                code.append(f"{indent}option \"{node.get('text', '')}\"")
                code.extend(self._generate_node_list_code(node.get("nodes", []), indent_level + 1))
                code.append(f"{indent}end option")
            elif node_type == "if":
                code.append(f"{indent}if {node.get('condition', 'true')}")

                child_nodes = node.get("nodes", [])
                else_marker_index = -1
                for i, child in enumerate(child_nodes):
                    if child.get("type") == "else_marker":
                        else_marker_index = i
                        break

                if else_marker_index != -1:
                    then_nodes = child_nodes[:else_marker_index]
                    else_nodes = child_nodes[else_marker_index+1:]
                    code.extend(self._generate_node_list_code(then_nodes, indent_level + 1))
                    code.append(f"{indent}else")
                    code.extend(self._generate_node_list_code(else_nodes, indent_level + 1))
                else:
                    code.extend(self._generate_node_list_code(child_nodes, indent_level + 1))

                code.append(f"{indent}end")

        return code

    def run_game(self):
        script_code = self._get_generated_code()
        if not script_code:
            messagebox.showerror("Error", "There is no game logic to run.")
            return

        temp_filepath = "temp_main.ld"
        with open(temp_filepath, "w") as f:
            f.write(script_code)

        self._show_game_console(temp_filepath)

    def _show_game_console(self, filepath_to_run):
        console_window = tk.Toplevel(self)
        console_window.title("Game Console")
        console_window.geometry("800x600")

        text_area = scrolledtext.ScrolledText(console_window, wrap=tk.WORD, bg="black", fg="white")
        text_area.pack(expand=True, fill="both")
        text_area.configure(state='disabled')

        output_queue = queue.Queue()

        process_thread = threading.Thread(
            target=self._run_process_in_thread,
            args=(filepath_to_run, output_queue)
        )
        process_thread.daemon = True
        process_thread.start()

        self.after(100, self._check_queue, text_area, output_queue)

    def _check_queue(self, text_area, output_queue):
        try:
            while True:
                line = output_queue.get_nowait()
                text_area.configure(state='normal')
                text_area.insert(tk.END, line)
                text_area.see(tk.END)
                text_area.configure(state='disabled')
        except queue.Empty:
            pass
        self.after(100, self._check_queue, text_area, output_queue)

    def _run_process_in_thread(self, filepath, output_queue):
        command = [sys.executable, "ldscript_interpreter.py", filepath]
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for line in process.stdout:
                output_queue.put(line)
            process.stdout.close()
            process.wait()
        except FileNotFoundError:
            output_queue.put("Error: 'python' command not found. Is Python installed and in your PATH?\n")
        except Exception as e:
            output_queue.put(f"An unexpected error occurred: {e}\n")
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

class EntitiesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.entities_data = {}
        self.selected_entity_id = None
        self._setup_ui()

    def _setup_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')

        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=1)
        ttk.Label(list_frame, text="Entities").pack(pady=5)
        self.entity_listbox = tk.Listbox(list_frame)
        self.entity_listbox.pack(expand=True, fill='both', padx=5, pady=5)
        self.entity_listbox.bind('<<ListboxSelect>>', self.on_entity_select)

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Add Entity", command=self.add_entity).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(button_frame, text="Delete Entity", command=self.delete_entity).pack(side='left', fill='x', expand=True, padx=2)

        details_frame = ttk.Frame(paned_window)
        paned_window.add(details_frame, weight=3)
        ttk.Label(details_frame, text="Entity Details").pack(pady=5)

        id_frame = ttk.Frame(details_frame)
        id_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(id_frame, text="ID:").pack(side='left', padx=5)
        self.entity_id_var = tk.StringVar()
        self.entity_id_entry = ttk.Entry(id_frame, textvariable=self.entity_id_var)
        self.entity_id_entry.pack(side='left', expand=True, fill='x')
        self.entity_id_entry.bind('<FocusOut>', self.update_entity_id)

        stats_label = ttk.Label(details_frame, text="Stats")
        stats_label.pack(pady=5)
        stats_frame = ttk.Frame(details_frame)
        stats_frame.pack(expand=True, fill='both', padx=5, pady=5)
        self.stats_tree = ttk.Treeview(stats_frame, columns=('Stat', 'Value'), show='headings')
        self.stats_tree.heading('Stat', text='Stat')
        self.stats_tree.heading('Value', text='Value')
        self.stats_tree.pack(expand=True, fill='both')

        stats_button_frame = ttk.Frame(details_frame)
        stats_button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(stats_button_frame, text="Add Stat", command=self.add_stat).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(stats_button_frame, text="Remove Stat", command=self.remove_stat).pack(side='left', fill='x', expand=True, padx=2)

    def clear_data(self):
        self.entities_data = {}
        self.selected_entity_id = None
        self.entity_listbox.delete(0, tk.END)
        self.clear_details()

    def load_data(self, data):
        self.clear_data()
        self.entities_data = data
        for entity_id in self.entities_data:
            self.entity_listbox.insert(tk.END, entity_id)

    def add_entity(self):
        new_id = simpledialog.askstring("Add Entity", "Enter new entity ID:")
        if new_id:
            if new_id in self.entities_data:
                messagebox.showerror("Error", f"Entity ID '{new_id}' already exists.")
                return

            self.entities_data[new_id] = {"stats": {}}
            self.entity_listbox.insert(tk.END, new_id)

    def delete_entity(self):
        selected_indices = self.entity_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No entity selected to delete.")
            return

        entity_id = self.entity_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{entity_id}'?"):
            del self.entities_data[entity_id]
            self.entity_listbox.delete(selected_indices[0])
            self.clear_details()

    def on_entity_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return

        self.selected_entity_id = event.widget.get(selection[0])
        self.update_details_form()

    def update_details_form(self):
        if not self.selected_entity_id:
            self.clear_details()
            return

        self.entity_id_var.set(self.selected_entity_id)

        self.stats_tree.delete(*self.stats_tree.get_children())
        entity_data = self.entities_data.get(self.selected_entity_id, {})
        for stat, value in entity_data.get("stats", {}).items():
            self.stats_tree.insert('', tk.END, values=(stat, value))

    def update_entity_id(self, event):
        if not self.selected_entity_id:
            return

        new_id = self.entity_id_var.get()
        if not new_id or new_id == self.selected_entity_id:
            return

        if new_id in self.entities_data:
            messagebox.showerror("Error", f"Entity ID '{new_id}' already exists.")
            self.entity_id_var.set(self.selected_entity_id)
            return

        self.entities_data[new_id] = self.entities_data.pop(self.selected_entity_id)

        selected_index = self.entity_listbox.get(0, tk.END).index(self.selected_entity_id)
        self.entity_listbox.delete(selected_index)
        self.entity_listbox.insert(selected_index, new_id)
        self.entity_listbox.selection_set(selected_index)

        self.selected_entity_id = new_id

    def add_stat(self):
        if not self.selected_entity_id:
            messagebox.showinfo("Info", "Select an entity first.")
            return

        stat_name = simpledialog.askstring("Add Stat", "Enter stat name:")
        if not stat_name: return

        stat_value = simpledialog.askstring("Add Stat", f"Enter value for '{stat_name}':")
        if stat_value is None: return

        self.entities_data[self.selected_entity_id]["stats"][stat_name] = stat_value
        self.update_details_form()

    def remove_stat(self):
        selected_item = self.stats_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Select a stat to remove.")
            return

        stat_name = self.stats_tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove the stat '{stat_name}'?"):
            del self.entities_data[self.selected_entity_id]["stats"][stat_name]
            self.update_details_form()

    def clear_details(self):
        self.entity_id_var.set("")
        self.stats_tree.delete(*self.stats_tree.get_children())
        self.selected_entity_id = None


class ItemsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.items_data = {}
        self.selected_item_id = None
        self._setup_ui()

    def _setup_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')

        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=1)
        ttk.Label(list_frame, text="Items").pack(pady=5)
        self.item_listbox = tk.Listbox(list_frame)
        self.item_listbox.pack(expand=True, fill='both', padx=5, pady=5)
        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Add Item", command=self.add_item).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(button_frame, text="Delete Item", command=self.delete_item).pack(side='left', fill='x', expand=True, padx=2)

        details_frame = ttk.Frame(paned_window)
        paned_window.add(details_frame, weight=3)
        ttk.Label(details_frame, text="Item Details").pack(pady=5)

        form_frame = ttk.Frame(details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)

        self.item_id_var = tk.StringVar()
        self.item_name_var = tk.StringVar()
        self.item_desc_var = tk.StringVar()
        self.item_price_var = tk.StringVar()

        fields = {"ID": self.item_id_var, "Name": self.item_name_var, "Description": self.item_desc_var, "Price": self.item_price_var}
        for label_text, var in fields.items():
            row = ttk.Frame(form_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=f"{label_text}:", width=12, anchor='w').pack(side='left')
            entry = ttk.Entry(row, textvariable=var)
            entry.pack(side='left', expand=True, fill='x')
            if label_text == "ID":
                entry.bind('<FocusOut>', self.update_item_id)
            else:
                var.trace_add("write", self.update_item_details)

    def clear_data(self):
        self.items_data = {}
        self.selected_item_id = None
        self.item_listbox.delete(0, tk.END)
        self.clear_details()

    def load_data(self, data):
        self.clear_data()
        self.items_data = data
        for item_id in self.items_data:
            self.item_listbox.insert(tk.END, item_id)

    def add_item(self):
        new_id = simpledialog.askstring("Add Item", "Enter new item ID:")
        if new_id:
            if new_id in self.items_data:
                messagebox.showerror("Error", f"Item ID '{new_id}' already exists.")
                return

            self.items_data[new_id] = {"name": "", "description": "", "price": "0"}
            self.item_listbox.insert(tk.END, new_id)

    def delete_item(self):
        selected_indices = self.item_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No item selected to delete.")
            return

        item_id = self.item_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{item_id}'?"):
            del self.items_data[item_id]
            self.item_listbox.delete(selected_indices[0])
            self.clear_details()

    def on_item_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return

        self.selected_item_id = event.widget.get(selection[0])
        self.update_details_form()

    def update_details_form(self):
        if not self.selected_item_id or self.selected_item_id not in self.items_data:
            self.clear_details()
            return

        for var in [self.item_name_var, self.item_desc_var, self.item_price_var]:
            if var.trace_info():
                var.trace_vdelete("w", var.trace_info()[0][1])

        item_data = self.items_data[self.selected_item_id]
        self.item_id_var.set(self.selected_item_id)
        self.item_name_var.set(item_data.get("name", ""))
        self.item_desc_var.set(item_data.get("description", ""))
        self.item_price_var.set(item_data.get("price", "0"))

        self.item_name_var.trace_add("write", self.update_item_details)
        self.item_desc_var.trace_add("write", self.update_item_details)
        self.item_price_var.trace_add("write", self.update_item_details)

    def update_item_id(self, event):
        if not self.selected_item_id:
            return

        new_id = self.item_id_var.get()
        if not new_id or new_id == self.selected_item_id:
            return

        if new_id in self.items_data:
            messagebox.showerror("Error", f"Item ID '{new_id}' already exists.")
            self.item_id_var.set(self.selected_item_id)
            return

        self.items_data[new_id] = self.items_data.pop(self.selected_item_id)

        selected_index = self.item_listbox.get(0, tk.END).index(self.selected_item_id)
        self.item_listbox.delete(selected_index)
        self.item_listbox.insert(selected_index, new_id)
        self.item_listbox.selection_set(selected_index)

        self.selected_item_id = new_id

    def update_item_details(self, *args):
        if not self.selected_item_id:
            return

        if self.selected_item_id not in self.items_data:
            return

        self.items_data[self.selected_item_id] = {
            "name": self.item_name_var.get(),
            "description": self.item_desc_var.get(),
            "price": self.item_price_var.get()
        }

    def clear_details(self):
        self.selected_item_id = None
        self.item_id_var.set("")
        self.item_name_var.set("")
        self.item_desc_var.set("")
        self.item_price_var.set("")


class QuestsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.quests_data = {}
        self.selected_quest_id = None
        self._setup_ui()

    def _setup_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')

        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=1)
        ttk.Label(list_frame, text="Quests").pack(pady=5)
        self.quest_listbox = tk.Listbox(list_frame)
        self.quest_listbox.pack(expand=True, fill='both', padx=5, pady=5)
        self.quest_listbox.bind('<<ListboxSelect>>', self.on_quest_select)

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Add Quest", command=self.add_quest).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(button_frame, text="Delete Quest", command=self.delete_quest).pack(side='left', fill='x', expand=True, padx=2)

        details_frame = ttk.Frame(paned_window)
        paned_window.add(details_frame, weight=3)
        ttk.Label(details_frame, text="Quest Details").pack(pady=5)

        form_frame = ttk.Frame(details_frame)
        form_frame.pack(fill='x', padx=5, pady=5)

        self.quest_id_var = tk.StringVar()
        self.quest_name_var = tk.StringVar()
        self.quest_desc_var = tk.StringVar()
        self.quest_state_var = tk.StringVar()

        id_row = ttk.Frame(form_frame)
        id_row.pack(fill='x', pady=2)
        ttk.Label(id_row, text="ID:", width=12, anchor='w').pack(side='left')
        id_entry = ttk.Entry(id_row, textvariable=self.quest_id_var)
        id_entry.pack(side='left', expand=True, fill='x')
        id_entry.bind('<FocusOut>', self.update_quest_id)

        name_row = ttk.Frame(form_frame)
        name_row.pack(fill='x', pady=2)
        ttk.Label(name_row, text="Name:", width=12, anchor='w').pack(side='left')
        ttk.Entry(name_row, textvariable=self.quest_name_var).pack(side='left', expand=True, fill='x')

        desc_row = ttk.Frame(form_frame)
        desc_row.pack(fill='x', pady=2)
        ttk.Label(desc_row, text="Description:", width=12, anchor='w').pack(side='left')
        ttk.Entry(desc_row, textvariable=self.quest_desc_var).pack(side='left', expand=True, fill='x')

        state_row = ttk.Frame(form_frame)
        state_row.pack(fill='x', pady=2)
        ttk.Label(state_row, text="State:", width=12, anchor='w').pack(side='left')
        state_combo = ttk.Combobox(state_row, textvariable=self.quest_state_var, values=['inactive', 'active', 'completed'])
        state_combo.pack(side='left', expand=True, fill='x')

        self.quest_name_var.trace_add("write", self.update_quest_details)
        self.quest_desc_var.trace_add("write", self.update_quest_details)
        self.quest_state_var.trace_add("write", self.update_quest_details)

    def clear_data(self):
        self.quests_data = {}
        self.selected_quest_id = None
        self.quest_listbox.delete(0, tk.END)
        self.clear_details()

    def load_data(self, data):
        self.clear_data()
        self.quests_data = data
        for quest_id in self.quests_data:
            self.quest_listbox.insert(tk.END, quest_id)

    def add_quest(self):
        new_id = simpledialog.askstring("Add Quest", "Enter new quest ID:")
        if new_id:
            if new_id in self.quests_data:
                messagebox.showerror("Error", f"Quest ID '{new_id}' already exists.")
                return

            self.quests_data[new_id] = {"name": "New Quest", "description": "", "state": "inactive"}
            self.quest_listbox.insert(tk.END, new_id)

    def delete_quest(self):
        selected_indices = self.quest_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No quest selected to delete.")
            return

        quest_id = self.quest_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{quest_id}'?"):
            del self.quests_data[quest_id]
            self.quest_listbox.delete(selected_indices[0])
            self.clear_details()

    def on_quest_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        self.selected_quest_id = event.widget.get(selection[0])
        self.update_details_form()

    def update_details_form(self):
        if not self.selected_quest_id or self.selected_quest_id not in self.quests_data:
            self.clear_details()
            return

        for var in [self.quest_name_var, self.quest_desc_var, self.quest_state_var]:
            if var.trace_info():
                var.trace_vdelete("w", var.trace_info()[0][1])

        quest_data = self.quests_data[self.selected_quest_id]
        self.quest_id_var.set(self.selected_quest_id)
        self.quest_name_var.set(quest_data.get("name", ""))
        self.quest_desc_var.set(quest_data.get("description", ""))
        self.quest_state_var.set(quest_data.get("state", "inactive"))

        self.quest_name_var.trace_add("write", self.update_quest_details)
        self.quest_desc_var.trace_add("write", self.update_quest_details)
        self.quest_state_var.trace_add("write", self.update_quest_details)

    def update_quest_id(self, event):
        if not self.selected_quest_id: return
        new_id = self.quest_id_var.get()
        if not new_id or new_id == self.selected_quest_id: return

        if new_id in self.quests_data:
            messagebox.showerror("Error", f"Quest ID '{new_id}' already exists.")
            self.quest_id_var.set(self.selected_quest_id)
            return

        self.quests_data[new_id] = self.quests_data.pop(self.selected_quest_id)

        selected_index = self.quest_listbox.get(0, tk.END).index(self.selected_quest_id)
        self.quest_listbox.delete(selected_index)
        self.quest_listbox.insert(selected_index, new_id)
        self.quest_listbox.selection_set(selected_index)

        self.selected_quest_id = new_id

    def update_quest_details(self, *args):
        if not self.selected_quest_id or self.selected_quest_id not in self.quests_data:
            return

        self.quests_data[self.selected_quest_id] = {
            "name": self.quest_name_var.get(),
            "description": self.quest_desc_var.get(),
            "state": self.quest_state_var.get()
        }

    def clear_details(self):
        self.selected_quest_id = None
        self.quest_id_var.set("")
        self.quest_name_var.set("")
        self.quest_desc_var.set("")
        self.quest_state_var.set("")


class FunctionsTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.clear_data()

        # Main layout
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')

        # Left frame for the tree view
        tree_frame = ttk.Frame(paned_window)
        paned_window.add(tree_frame, weight=2)

        tree_button_frame = ttk.Frame(tree_frame)
        tree_button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(tree_button_frame, text="Add Function", command=self.add_function).pack(side='left')

        self.tree = ttk.Treeview(tree_frame, show='tree', columns=("type",))
        self.tree.column("#0", width=300, stretch=tk.YES)
        self.tree.column("type", width=0, stretch=tk.NO)
        self.tree.pack(expand=True, fill='both', padx=5, pady=5)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", self.on_node_select)

        self._create_context_menu()

        # Right frame for properties
        self.properties_frame = ttk.Frame(paned_window)
        paned_window.add(self.properties_frame, weight=1)

        self.properties_widgets = {}

    def clear_data(self):
        self.functions_data = {}
        self.node_map = {}
        # We share the node counter with the dialogs tab to prevent ID collisions
        if hasattr(self.app, 'dialogs_tab'):
            self.node_counter = self.app.dialogs_tab.node_counter
        else:
            self.node_counter = 0

        if hasattr(self, 'tree'):
            for i in self.tree.get_children():
                self.tree.delete(i)

    def load_data(self, data, node_counter):
        self.clear_data()
        self.functions_data = data
        self.node_counter = node_counter
        self.refresh_tree_from_data()

    def refresh_tree_from_data(self):
        self.node_map = {}
        for func_id, func_data in self.functions_data.items():
            self.node_map[func_id] = func_data
            self.tree.insert('', 'end', iid=func_id, text=f"function {func_id}", values=("function",), open=True)
            self._recursive_build_tree(func_data["nodes"], func_id)

    def _recursive_build_tree(self, nodes, parent_iid):
        for node_data in nodes:
            self.node_counter += 1
            node_iid = f"node_{self.node_counter}"
            self.node_map[node_iid] = node_data

            is_open = "nodes" in node_data
            self.tree.insert(parent_iid, 'end', iid=node_iid, values=(node_data["type"],), open=is_open)
            self.refresh_node_text(node_iid)
            if is_open:
                self._recursive_build_tree(node_data.get("nodes", []), node_iid)

    def on_node_select(self, event):
        self.update_properties_panel()

    def update_properties_panel(self):
        for widget in self.properties_frame.winfo_children():
            widget.destroy()
        self.properties_widgets = {}

        selection = self.tree.selection()
        if not selection: return

        self.selected_node_id = selection[0]
        node_data = self.node_map.get(self.selected_node_id)
        if not node_data: return

        ttk.Label(self.properties_frame, text=f"Properties: {node_data['type']}").pack(pady=5)

        if node_data["type"] == "say":
            self._create_property_entry("Text:", node_data, "text")
        elif node_data["type"] == "set_quest":
            self._create_property_combobox("Quest ID:", node_data, "quest_id", list(self.app.quests_tab.quests_data.keys()))
            self._create_property_combobox("State:", node_data, "state", ["inactive", "active", "completed"])
        elif node_data["type"] in ["give", "take"]:
            self._create_property_combobox("Item ID:", node_data, "item_id", list(self.app.items_tab.items_data.keys()))
            self._create_property_entry("Count:", node_data, "count")
        elif node_data["type"] == "if":
            self._create_property_entry("Condition:", node_data, "condition")
        elif node_data["type"] == "call_function":
            self._create_property_combobox("Function ID:", node_data, "name", list(self.app.functions_tab.functions_data.keys()))

    def _create_property_entry(self, label, node_data, key):
        ttk.Label(self.properties_frame, text=label).pack(anchor='w', padx=5)
        var = tk.StringVar(value=node_data.get(key, ""))
        entry = ttk.Entry(self.properties_frame, textvariable=var)
        entry.pack(fill='x', padx=5, pady=2)
        var.trace_add("write", lambda *args: self.update_node_data(node_data, key, var.get()))
        self.properties_widgets[key] = var

    def _create_property_combobox(self, label, node_data, key, values):
        ttk.Label(self.properties_frame, text=label).pack(anchor='w', padx=5)
        var = tk.StringVar(value=node_data.get(key, ""))
        combo = ttk.Combobox(self.properties_frame, textvariable=var, values=values if values else [""])
        combo.pack(fill='x', padx=5, pady=2)
        var.trace_add("write", lambda *args: self.update_node_data(node_data, key, var.get()))
        self.properties_widgets[key] = var

    def update_node_data(self, node_data, key, new_value):
        node_data[key] = new_value
        self.refresh_node_text(self.selected_node_id)

    def refresh_node_text(self, node_id):
        node_data = self.node_map.get(node_id)
        if not node_data: return

        node_type = node_data.get("type", "")
        text = f"Unknown: {node_type}"
        if node_type == "function":
            text = f'function {node_data.get("id", "")}'
        elif node_type == "say":
            text = f'say "{node_data.get("text", "")}"'
        elif node_type == "set_quest":
            text = f'set quest {node_data.get("quest_id", "?")} to {node_data.get("state", "?")}'
        elif node_type == "give":
            text = f'give {node_data.get("count", 1)} {node_data.get("item_id", "?")}'
        elif node_type == "take":
            text = f'take {node_data.get("count", 1)} {node_data.get("item_id", "?")}'
        elif node_type == "if":
            text = f'if {node_data.get("condition", "...")}'
        elif node_type == "else_marker":
            text = '---- ELSE ----'
        elif node_type == "call_function":
            text = f'call {node_data.get("name", "?")}'

        self.tree.item(node_id, text=text)


    def add_function(self):
        func_id = simpledialog.askstring("Add Function", "Enter new function ID:")
        if func_id and func_id not in self.functions_data:
            func_data = {"type": "function", "id": func_id, "nodes": []}
            self.functions_data[func_id] = func_data
            self.node_map[func_id] = func_data
            self.tree.insert('', 'end', iid=func_id, text=f"function {func_id}", values=("function",), open=True)
        elif func_id:
            messagebox.showerror("Error", f"Function ID '{func_id}' already exists.")

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Add Say", command=self.add_say_node)
        self.context_menu.add_command(label="Add If Block", command=self.add_if_node)
        self.context_menu.add_command(label="Add Call Function", command=self.add_call_function_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Set Quest", command=self.add_set_quest_node)
        self.context_menu.add_command(label="Add Give Item", command=self.add_give_node)
        self.context_menu.add_command(label="Add Take Item", command=self.add_take_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Else Marker", command=self.add_else_marker_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Node", command=self.delete_node)

    def show_context_menu(self, event):
        self.selected_node_id = self.tree.identify_row(event.y)
        if not self.selected_node_id: return
        self.tree.selection_set(self.selected_node_id)

        node_data = self.node_map.get(self.selected_node_id)
        if not node_data: return
        node_type = node_data.get("type")

        can_have_children = node_type in ["function", "if"]

        for item in ["Add Say", "Add If Block", "Add Set Quest", "Add Give Item", "Add Take Item", "Add Call Function"]:
             self.context_menu.entryconfig(item, state="normal" if can_have_children else "disabled")

        parent_id = self.tree.parent(self.selected_node_id)
        parent_data = self.node_map.get(parent_id) if parent_id else None
        parent_type = parent_data.get("type") if parent_data else None

        if node_type == 'if' or parent_type == 'if':
            parent_node_id = self.selected_node_id if node_type == 'if' else parent_id
            has_else = any(self.node_map[child_id].get("type") == "else_marker" for child_id in self.tree.get_children(parent_node_id))
            self.context_menu.entryconfig("Add Else Marker", state="disabled" if has_else else "normal")
        else:
            self.context_menu.entryconfig("Add Else Marker", state="disabled")

        is_deletable = node_type != "function"
        self.context_menu.entryconfig("Delete Node", state="normal" if is_deletable else "disabled")
        self.context_menu.post(event.x_root, event.y_root)

    def _add_node(self, node_data, parent_id=None):
        if parent_id is None:
            parent_id = self.selected_node_id

        if not parent_id: return
        parent_data = self.node_map.get(parent_id)
        if parent_data is None or "nodes" not in parent_data: return

        parent_data["nodes"].append(node_data)
        self.node_counter += 1
        new_node_id = f"node_{self.node_counter}"
        self.node_map[new_node_id] = node_data

        self.tree.insert(parent_id, 'end', iid=new_node_id, values=(node_data["type"],), open="nodes" in node_data)
        self.refresh_node_text(new_node_id)
        self.app.dialogs_tab.node_counter = self.node_counter

    def add_say_node(self):
        text = simpledialog.askstring("Add Say Node", "Enter the text to say:")
        if text is not None: self._add_node({"type": "say", "text": text})

    def add_if_node(self):
        condition = simpledialog.askstring("Add If Block", "Enter the condition:")
        if condition is not None: self._add_node({"type": "if", "condition": condition, "nodes": []})

    def add_set_quest_node(self):
        if not self.app.quests_tab.quests_data:
            messagebox.showinfo("Info", "No quests created yet.")
            return
        self._add_node({"type": "set_quest", "quest_id": "", "state": "active"})

    def add_give_node(self):
        if not self.app.items_tab.items_data:
            messagebox.showinfo("Info", "No items created yet.")
            return
        self._add_node({"type": "give", "item_id": "", "count": 1})

    def add_take_node(self):
        if not self.app.items_tab.items_data:
            messagebox.showinfo("Info", "No items created yet.")
            return
        self._add_node({"type": "take", "item_id": "", "count": 1})

    def add_call_function_node(self):
        if not self.app.functions_tab.functions_data:
            messagebox.showinfo("Info", "No functions created yet.")
            return
        self._add_node({"type": "call_function", "name": ""})

    def add_else_marker_node(self):
        parent_id = self.selected_node_id
        if self.node_map.get(parent_id, {}).get('type') != 'if':
            parent_id = self.tree.parent(self.selected_node_id)
        if self.node_map.get(parent_id, {}).get('type') == 'if':
            self._add_node({"type": "else_marker"}, parent_id=parent_id)

    def delete_node(self):
        if not self.selected_node_id: return
        if not messagebox.askyesno("Confirm", "Delete selected node?"): return

        parent_id = self.tree.parent(self.selected_node_id)
        if parent_id:
            parent_data = self.node_map.get(parent_id)
            node_data = self.node_map.get(self.selected_node_id)
            if parent_data and node_data and node_data in parent_data.get("nodes", []):
                parent_data["nodes"].remove(node_data)

        self._recursive_unmap(self.selected_node_id)
        self.tree.delete(self.selected_node_id)
        self.update_properties_panel()

    def _recursive_unmap(self, node_id):
        for child_id in self.tree.get_children(node_id):
            self._recursive_unmap(child_id)
        self.node_map.pop(node_id, None)


class DialogsTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.clear_data()

        # Main layout
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(expand=True, fill='both')

        # Left frame for the tree view
        tree_frame = ttk.Frame(paned_window)
        paned_window.add(tree_frame, weight=2)

        tree_button_frame = ttk.Frame(tree_frame)
        tree_button_frame.pack(fill='x', padx=5, pady=5)
        add_dialog_button = ttk.Button(tree_button_frame, text="Add Dialog", command=self.add_dialog)
        add_dialog_button.pack(side='left')

        self.tree = ttk.Treeview(tree_frame, show='tree', columns=("type",))
        self.tree.column("#0", width=300, stretch=tk.YES)
        self.tree.column("type", width=0, stretch=tk.NO)
        self.tree.pack(expand=True, fill='both', padx=5, pady=5)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", self.on_node_select)

        self._create_context_menu()

        # Right frame for properties
        self.properties_frame = ttk.Frame(paned_window)
        paned_window.add(self.properties_frame, weight=1)

        self.properties_widgets = {}

    def clear_data(self):
        self.dialogs_data = {}
        self.node_map = {}
        self.node_counter = 0
        if hasattr(self, 'tree'):
            for i in self.tree.get_children():
                self.tree.delete(i)

    def load_data(self, data, node_counter):
        self.clear_data()
        self.dialogs_data = data
        self.node_counter = node_counter
        self.refresh_tree_from_data()

    def refresh_tree_from_data(self):
        self.node_map = {}
        for dialog_id, dialog_data in self.dialogs_data.items():
            self.node_map[dialog_id] = dialog_data
            self.tree.insert('', 'end', iid=dialog_id, text=f"dialog {dialog_id}", values=("dialog",), open=True)
            self._recursive_build_tree(dialog_data["nodes"], dialog_id)

    def _recursive_build_tree(self, nodes, parent_iid):
        for node_data in nodes:
            self.node_counter += 1
            node_iid = f"node_{self.node_counter}"
            self.node_map[node_iid] = node_data

            is_open = "nodes" in node_data
            self.tree.insert(parent_iid, 'end', iid=node_iid, values=(node_data["type"],), open=is_open)
            self.refresh_node_text(node_iid)
            if is_open:
                self._recursive_build_tree(node_data["nodes"], node_iid)

    def on_node_select(self, event):
        self.update_properties_panel()

    def update_properties_panel(self):
        for widget in self.properties_frame.winfo_children():
            widget.destroy()
        self.properties_widgets = {}

        selection = self.tree.selection()
        if not selection: return

        self.selected_node_id = selection[0]
        node_data = self.node_map.get(self.selected_node_id)
        if not node_data: return

        ttk.Label(self.properties_frame, text=f"Properties: {node_data['type']}").pack(pady=5)

        if node_data["type"] in ["say", "option"]:
            self._create_property_entry("Text:", node_data, "text")
        elif node_data["type"] == "set_quest":
            self._create_property_combobox("Quest ID:", node_data, "quest_id", list(self.app.quests_tab.quests_data.keys()))
            self._create_property_combobox("State:", node_data, "state", ["inactive", "active", "completed"])
        elif node_data["type"] in ["give", "take"]:
            self._create_property_combobox("Item ID:", node_data, "item_id", list(self.app.items_tab.items_data.keys()))
            self._create_property_entry("Count:", node_data, "count")
        elif node_data["type"] == "if":
            self._create_property_entry("Condition:", node_data, "condition")
        elif node_data["type"] == "call_function":
            self._create_property_combobox("Function ID:", node_data, "name", list(self.app.functions_tab.functions_data.keys()))

    def _create_property_entry(self, label, node_data, key):
        ttk.Label(self.properties_frame, text=label).pack(anchor='w', padx=5)
        var = tk.StringVar(value=node_data.get(key, ""))
        entry = ttk.Entry(self.properties_frame, textvariable=var)
        entry.pack(fill='x', padx=5, pady=2)
        var.trace_add("write", lambda *args: self.update_node_data(node_data, key, var.get()))
        self.properties_widgets[key] = var

    def _create_property_combobox(self, label, node_data, key, values):
        ttk.Label(self.properties_frame, text=label).pack(anchor='w', padx=5)
        var = tk.StringVar(value=node_data.get(key, ""))
        combo = ttk.Combobox(self.properties_frame, textvariable=var, values=values if values else [""])
        combo.pack(fill='x', padx=5, pady=2)
        var.trace_add("write", lambda *args: self.update_node_data(node_data, key, var.get()))
        self.properties_widgets[key] = var

    def update_node_data(self, node_data, key, new_value):
        node_data[key] = new_value
        self.refresh_node_text(self.selected_node_id)

    def refresh_node_text(self, node_id):
        node_data = self.node_map.get(node_id)
        if not node_data: return

        node_type = node_data.get("type", "")
        text = f"Unknown node type: {node_type}"
        if node_type == "dialog":
            text = f'dialog {node_data.get("id", "")}'
        elif node_type == "say":
            text = f'say "{node_data.get("text", "")}"'
        elif node_type == "option":
            text = f'option "{node_data.get("text", "")}"'
        elif node_type == "set_quest":
            text = f'set quest {node_data.get("quest_id", "?")} to {node_data.get("state", "?")}'
        elif node_type == "give":
            text = f'give {node_data.get("count", 1)} {node_data.get("item_id", "?")}'
        elif node_type == "take":
            text = f'take {node_data.get("count", 1)} {node_data.get("item_id", "?")}'
        elif node_type == "if":
            text = f'if {node_data.get("condition", "...")}'
        elif node_type == "else_marker":
            text = '---- ELSE ----'
        elif node_type == "call_function":
            text = f'call {node_data.get("name", "?")}'

        self.tree.item(node_id, text=text)

    def add_dialog(self):
        dialog_id = simpledialog.askstring("Add Dialog", "Enter new dialog ID:")
        if dialog_id and dialog_id not in self.dialogs_data:
            dialog_data = {"type": "dialog", "id": dialog_id, "nodes": []}
            self.dialogs_data[dialog_id] = dialog_data
            self.node_map[dialog_id] = dialog_data
            self.tree.insert('', 'end', iid=dialog_id, text=f"dialog {dialog_id}", values=("dialog",), open=True)
        elif dialog_id:
            messagebox.showerror("Error", f"Dialog ID '{dialog_id}' already exists.")

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Add Say", command=self.add_say_node)
        self.context_menu.add_command(label="Add Option", command=self.add_option_node)
        self.context_menu.add_command(label="Add If Block", command=self.add_if_node)
        self.context_menu.add_command(label="Add Call Function", command=self.add_call_function_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Set Quest", command=self.add_set_quest_node)
        self.context_menu.add_command(label="Add Give Item", command=self.add_give_node)
        self.context_menu.add_command(label="Add Take Item", command=self.add_take_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Else Marker", command=self.add_else_marker_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Node", command=self.delete_node)

    def show_context_menu(self, event):
        self.selected_node_id = self.tree.identify_row(event.y)
        if not self.selected_node_id: return
        self.tree.selection_set(self.selected_node_id)

        node_type = self.tree.item(self.selected_node_id, 'values')[0]
        can_have_children = node_type in ["dialog", "option", "if"]

        for item in ["Add Say", "Add Option", "Add Set Quest", "Add Give Item", "Add Take Item", "Add If Block", "Add Call Function"]:
             self.context_menu.entryconfig(item, state="normal" if can_have_children else "disabled")

        # Special logic for 'Add Else Marker'
        parent_id = self.tree.parent(self.selected_node_id)
        parent_type = self.tree.item(parent_id, 'values')[0] if parent_id else ""
        if node_type == 'if' or parent_type == 'if':
            # Check if an else marker already exists
            parent_node = self.selected_node_id if node_type == 'if' else parent_id
            has_else = any(self.node_map[child_id].get("type") == "else_marker" for child_id in self.tree.get_children(parent_node))
            self.context_menu.entryconfig("Add Else Marker", state="disabled" if has_else else "normal")
        else:
            self.context_menu.entryconfig("Add Else Marker", state="disabled")

        self.context_menu.entryconfig("Delete Node", state="disabled" if not self.tree.parent(self.selected_node_id) else "normal")
        self.context_menu.post(event.x_root, event.y_root)

    def add_say_node(self):
        text = simpledialog.askstring("Add Say Node", "Enter the text to say:")
        if text is not None:
            self._add_node({"type": "say", "text": text})

    def add_option_node(self):
        text = simpledialog.askstring("Add Option Node", "Enter the option text:")
        if text is not None:
            self._add_node({"type": "option", "text": text, "nodes": []})

    def add_if_node(self):
        condition = simpledialog.askstring("Add If Block", "Enter the condition (e.g., player.health > 10):")
        if condition is not None:
            self._add_node({"type": "if", "condition": condition, "nodes": []})

    def add_call_function_node(self):
        if not self.app.functions_tab.functions_data:
            messagebox.showinfo("Info", "No functions created yet.")
            return
        self._add_node({"type": "call_function", "name": ""})

    def add_set_quest_node(self):
        quest_ids = list(self.app.quests_tab.quests_data.keys())
        if not quest_ids:
            messagebox.showinfo("Info", "No quests created. Please create a quest in the Quests tab first.")
            return
        self._add_node({"type": "set_quest", "quest_id": quest_ids[0], "state": "active"})

    def add_give_node(self):
        item_ids = list(self.app.items_tab.items_data.keys())
        if not item_ids:
            messagebox.showinfo("Info", "No items created. Please create an item in the Items tab first.")
            return
        self._add_node({"type": "give", "item_id": item_ids[0], "count": 1})

    def add_take_node(self):
        item_ids = list(self.app.items_tab.items_data.keys())
        if not item_ids:
            messagebox.showinfo("Info", "No items created. Please create an item in the Items tab first.")
            return
        self._add_node({"type": "take", "item_id": item_ids[0], "count": 1})

    def add_else_marker_node(self):
        parent_id = self.selected_node_id
        if self.tree.item(parent_id, 'values')[0] != 'if':
            parent_id = self.tree.parent(self.selected_node_id)

        if self.tree.item(parent_id, 'values')[0] == 'if':
            self._add_node({"type": "else_marker"}, parent_id=parent_id)

    def _add_node(self, node_data, parent_id=None):
        if parent_id is None:
            parent_id = self.selected_node_id

        if not parent_id: return
        parent_data = self.node_map.get(parent_id)
        if parent_data is None or "nodes" not in parent_data: return

        parent_data["nodes"].append(node_data)
        self.node_counter += 1
        new_node_id = f"node_{self.node_counter}"
        self.node_map[new_node_id] = node_data

        self.tree.insert(parent_id, 'end', iid=new_node_id, values=(node_data["type"],), open="nodes" in node_data)
        self.refresh_node_text(new_node_id)

    def delete_node(self):
        if not self.selected_node_id: return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete the selected node and all its children?"):
            return

        parent_id = self.tree.parent(self.selected_node_id)
        if parent_id:
            parent_data = self.node_map.get(parent_id)
            node_data = self.node_map.get(self.selected_node_id)
            if parent_data and node_data and node_data in parent_data.get("nodes", []):
                parent_data["nodes"].remove(node_data)

        self._recursive_unmap(self.selected_node_id)
        self.tree.delete(self.selected_node_id)
        self.update_properties_panel()

    def _recursive_unmap(self, node_id):
        for child_id in self.tree.get_children(node_id):
            self._recursive_unmap(child_id)
        self.node_map.pop(node_id, None)


if __name__ == "__main__":
    app = App()
    app.mainloop()
