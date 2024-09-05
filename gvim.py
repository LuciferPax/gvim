import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel, Listbox, Label, END
import json
import re
import os
import importlib.util
from ctypes import windll, Structure, c_int, byref, sizeof, c_void_p, cast, POINTER

class EditorAPI:
    def __init__(self, editor):
        self.editor = editor
        self.event = {}

    def __init__(self, editor):
        self.editor = editor
        self.event = {}

    def update_event(self, name, value):
        """Update event with a name and value"""
        print(f"Event: {name} - {value}")
        self.event[name] = value

    def pop_event(self):
        """Clear the event after it is handled"""
        return self.event.popitem()
    
    def get_text(self):
        return self.editor.text_area.get(1.0, tk.END)
    
    def set_text(self, text):
        self.editor.text_area.delete(1.0, tk.END)
        self.editor.text_area.insert(1.0, text)

    def get_file_path(self):
        return self.editor.file_path

    def insert_text(self, position, text):
        self.editor.text_area.insert(position, text)

    def get_selection(self):
        try:
            return self.editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return ""
        
    def bind_key(self, key, callback):
        """binds a key but does not interfere with the editor's key bindings"""
        self.editor.text_area.bind(key, callback)

    def replace_selection(self, text):
        try:
            self.editor.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.editor.text_area.insert(tk.SEL_FIRST, text)
        except tk.TclError:
            pass

    def get_cursor_position(self):
        return self.editor.text_area.index(tk.INSERT)

    def set_cursor_position(self, position):
        self.editor.text_area.mark_set(tk.INSERT, position)
        self.editor.text_area.see(tk.INSERT)


class PluginManager:
    def __init__(self, editor):
        self.editor = editor
        self.plugins = []
        self.toggled_off_plugins = []
        self.plugin_dir = "plugins"
        self.api = EditorAPI(editor)

    def install_plugin(self, path):
        with open(path, 'r') as p, open(f'plugins/{path}', 'w') as f: 
            f.write(p.read())
            self.load_plugin(f'plugins/{path}')

    def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
        
        for file in os.listdir(self.plugin_dir):
            if file.endswith(".py"):
                plugin_path = os.path.join(self.plugin_dir, file)
                self.load_plugin(plugin_path)

    def uninstall_disable_plugin(self):
        # Modern and clean borderless plugin manager GUI
        self.plugin_window = Toplevel(self.editor.root)
        self.plugin_window.title("Plugin Manager")
        self.plugin_window.geometry("400x400")
        self.plugin_window.overrideredirect(True)  # Makes the window borderless
        self.plugin_window.config(bg=self.editor.current_scheme["background_color"])

        # Custom-styled header with drag functionality for moving the window
        header_frame = tk.Frame(self.plugin_window, bg=self.editor.current_scheme["background_color"])
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text="Manage Plugins", font=("Helvetica", 16, "bold"), 
                                fg=self.editor.current_scheme["foreground_color"], 
                                bg=self.editor.current_scheme["background_color"])
        header_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Allow dragging the borderless window
        header_frame.bind("<B1-Motion>", self.move_window)

        close_button = tk.Button(header_frame, text="X", command=self.plugin_window.destroy, 
                                 bg=self.editor.current_scheme["background_color"], 
                                 fg=self.editor.current_scheme["foreground_color"], 
                                 bd=0, relief="flat")
        close_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Styled plugin listbox
        self.plugin_list = Listbox(self.plugin_window, bg=self.editor.current_scheme["background_color"], 
                                   fg=self.editor.current_scheme["foreground_color"], 
                                   selectbackground=self.editor.current_scheme["line_bar_color"], 
                                   selectforeground=self.editor.current_scheme["foreground_color"], 
                                   font=("Helvetica", 12), relief="flat", borderwidth=0)
        self.plugin_list.pack(expand=True, fill='both', padx=10, pady=10)

        for plugin in self.plugins:
            self.plugin_list.insert(END, plugin.__name__)

        self.plugin_list.bind("<Double-Button-1>", self.toggle_plugin)

        # Plugin toggle switches
        toggle_frame = tk.Frame(self.plugin_window, bg=self.editor.current_scheme["background_color"])
        toggle_frame.pack(fill=tk.BOTH, pady=10)
        
        for i, plugin in enumerate(self.plugins):
            toggle_var = tk.IntVar(value=1 if plugin not in self.toggled_off_plugins else 0)
            toggle_button = ttk.Checkbutton(toggle_frame, variable=toggle_var, text=plugin.__name__, 
                                            style="Switch.TCheckbutton")
            toggle_button.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            toggle_button.configure(command=lambda var=toggle_var, idx=i: self.toggle_plugin_state(var, idx))

        # Styled delete button
        delete_button = ttk.Button(self.plugin_window, text="Delete", command=self.delete_plugin)
        delete_button.pack(pady=10)

    def toggle_plugin_state(self, toggle_var, index):
        plugin = self.plugins[index]
        if toggle_var.get() == 0:
            self.toggled_off_plugins.append(plugin)
        else:
            self.toggled_off_plugins.remove(plugin)

    def delete_plugin(self):
        selected_index = self.plugin_list.curselection()
        if selected_index:
            plugin = self.plugins[selected_index[0]]
            plugin_name = plugin.__name__
            plugin_path = f"plugins/{plugin_name}.py"
            os.remove(plugin_path)
            self.plugins.remove(plugin)
            self.plugin_list.delete(selected_index[0])

    def toggle_plugin(self, event=None):
        plugin = self.plugins[self.plugin_list.curselection()[0]]
        if plugin in self.toggled_off_plugins:
            self.toggled_off_plugins.remove(plugin)
        else:
            self.toggled_off_plugins.append(plugin)

    def load_plugin(self, plugin_path):
        plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            self.plugins.append(module)

    def execute_plugins(self):
        for plugin in self.plugins:
            plugin.run(self.api)

    def move_window(self, event):
        x, y = event.x_root, event.y_root
        self.plugin_window.geometry(f"+{x}+{y}")



class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x600")
        self.root.overrideredirect(True)

        self.offset_x = 0
        self.offset_y = 0

        # Default font and color scheme
        self.default_scheme = {
            "font_face": "Fira Code",
            "font_size": 14,
            "background_color": "#1E1E1E",
            "foreground_color": "#C6C6C6",
            "insertbackground_color": "#FFFFFF",
            "default_terminal_path": None,
            "line_bar_color": "#3E3E3E",
            "line_number_color": "#5A5A5A",
            "tab_size": 4,
            "line_number_font_size": 11,
            "line_number_bold": False,
            "line_number_italic": False
        }

        self.schemes = {"default": self.default_scheme}
        self.syntax_rules = []

        self.current_scheme = self.default_scheme.copy()

        self.root.config(bg=self.shift_color(self.current_scheme["background_color"], 7))
        self.text_font = (self.current_scheme["font_face"], self.current_scheme["font_size"])

        self.plugin_manager = PluginManager(self)
        
        self.create_menu_bar()

        # Frame to contain both the text area and the line numbers
        self.main_frame = tk.Frame(self.root, bg=self.current_scheme["background_color"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Line number bar
        self.line_number_bar = self.create_text_widget(self.main_frame, 2, "#3E3E3E", "#5A5A5A")
        self.line_number_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Text area
        self.text_area = self.create_text_widget(self.main_frame, None, self.current_scheme["background_color"], 
                                                 self.current_scheme["foreground_color"], is_editable=True, py=20)
        self.text_area.pack(expand='yes', fill='both')

        self.save_schemes_in_themes()
        if os.path.exists("themes/.schemelog"):
            self.load_previous_scheme()
        else:
            self.load_default_color_scheme()

        # Bindings for updating line numbers and syntax highlighting
        for event in ('<KeyRelease>', '<KeyPress>', '<MouseWheel>', '<Configure>'):
            self.text_area.bind(event, self.update_line_numbers_on_change)
        
        # Bindings for syntax highlighting
        self.text_area.bind("<KeyRelease>", self.apply_syntax_highlighting)

        #binding to move the window
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        self.file_path = None

        # Initialize and load plugins
        self.plugin_manager.load_plugins()
        self.plugin_manager.execute_plugins()

        # Menu bar

    def start_move(self, event):
        """Record the initial position when the user clicks to start moving the window."""
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        """Move the window smoothly based on the difference from the initial click position."""
        new_x = event.x_root - self.offset_x
        new_y = event.y_root - self.offset_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def minimize_window(self):
        self.root.iconify()

    def load_previous_scheme(self):
        with open("themes/.schemelog", "r") as f:
            scheme = f.read()
            self.load_color_scheme(scheme)

    def update_line_numbers(self):
        line_count = self.text_area.get('1.0', 'end').count('\n')
        self.line_number_bar.config(state=tk.NORMAL)
        self.line_number_bar.delete('1.0', tk.END)
        for i in range(1, line_count + 2):
            self.line_number_bar.insert(tk.END, f'{i}\n')
        
        # Add tag to center text
        self.line_number_bar.tag_configure("center", justify='center')
        self.line_number_bar.tag_add("center", 1.0, tk.END)
        
        self.line_number_bar.config(state=tk.DISABLED)

    def create_text_widget(self, parent, width, bg, fg, is_editable=False, px=5, py=20):
        state = tk.NORMAL if is_editable else tk.DISABLED
        return tk.Text(parent, width=width, padx=px, pady=py, takefocus=0, border=0, 
                   background=bg, foreground=fg, wrap=tk.NONE, undo=True, autoseparators=True,
                   font=("Helvetica", 11), relief="flat", state=state)

    def update_line_numbers_on_change(self, event=None):
        self.update_line_numbers()
        self.apply_syntax_highlighting()
        self.line_number_bar.yview_moveto(self.text_area.yview()[0])

    def apply_color_scheme(self, event=None):
        selected_scheme = self.scheme_select_combobox.get()
        with open("themes/.schemelog", "w") as f:
            f.write(selected_scheme)
        self.load_color_scheme(selected_scheme)
        self.scheme_select.destroy()

    def install(self):
        json_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if json_file:
            with open(json_file) as f:
                data = json.load(f)
            self.save_scheme(data)
            if 'syntaxes' in data:
                self.save_syntaxes(data['syntaxes'])
            self.save_schemes_in_themes()
            messagebox.showinfo("Success", "Scheme Package installed successfully")

    def save_scheme(self, data):
        name = data['name']
        with open(f'themes/{name}.json', 'w') as f:
            json.dump(data['theme'], f)

    def iterate_plugins(self, data):
        plugins = data.get("plugins", [])
        for plugin in plugins:
            try:
                with open(plugin, 'r') as p, open(f'plugins/{plugin}', 'w') as f: 
                    f.write(p.read())
                    self.plugin_manager.load_plugin(f'plugins/{plugin}')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install plugin: {e}")

    def save_syntaxes(self, syntaxes):
        for lang, syntax_rules in syntaxes.items():
            for syntax in syntax_rules:
                self.update_syntax_file(syntax, lang)

    def update_syntax_file(self, syntax, lang):
        scope = syntax['scope']
        for file in os.listdir('extensions'):
            with open(f'extensions/{file}', 'r') as f:
                file_data = json.load(f)
                if file_data['scope'] == scope:
                    if messagebox.askyesno("Overwrite", f"Overwrite {file} with {lang} syntax?"):
                        with open(f'extensions/{file}', 'w') as f:
                            json.dump(syntax, f)

    def save_schemes_in_themes(self):
        for theme in os.listdir("themes"):
            if theme.endswith(".json"):
                with open(f"themes/{theme}", "r") as file:
                    name = theme.split(".")[0]
                    self.schemes[name] = json.load(file)

    def shift_color(self, color, shift):
        color = color.lstrip("#")
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + shift)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"

    def scheme_select(self):
        self.scheme_select = tk.Toplevel(self.root)
        self.scheme_select.title("Select Scheme")
        self.scheme_select.geometry("300x150")
        self.scheme_select.resizable(False, False)
        self.scheme_select.config(bg=self.current_scheme["background_color"])

        label = tk.Label(self.scheme_select, text="Select Scheme", font=("Helvetica", 14, "bold"),
                         bg=self.current_scheme["background_color"], 
                         fg=self.current_scheme["foreground_color"])
        label.pack(pady=10)

        style = self.create_combobox_style()
        self.scheme_select_combobox = ttk.Combobox(self.scheme_select, values=list(self.schemes.keys()), 
                                                   style="CustomCombobox", width=20)
        self.scheme_select_combobox.pack(pady=10)
        self.scheme_select_combobox.bind("<<ComboboxSelected>>", self.apply_color_scheme)

    def create_combobox_style(self):
        style = ttk.Style()
        style.theme_use('default')
        shifted_background = self.shift_color(self.current_scheme["background_color"], 7)
        style.layout("CustomCombobox", style.layout("TCombobox"))
        style.configure("CustomCombobox",
                        fieldbackground=shifted_background,
                        background=shifted_background,
                        foreground=self.current_scheme["foreground_color"],
                        selectbackground=self.shift_color(self.current_scheme["background_color"], 5),
                        selectforeground=self.current_scheme["foreground_color"],
                        arrowcolor=self.current_scheme["foreground_color"],
                        borderwidth=0,
                        relief="flat")
        style.map("CustomCombobox", fieldbackground=[('readonly', shifted_background)],
                  selectbackground=[('readonly', self.shift_color(self.current_scheme["background_color"], 5))],
                  selectforeground=[('readonly', self.current_scheme["foreground_color"])],
                  arrowcolor=[('readonly', self.current_scheme["foreground_color"])])
        return style

    def update_line_numbers(self):
        line_count = self.text_area.get('1.0', 'end').count('\n')
        self.line_number_bar.config(state=tk.NORMAL)
        self.line_number_bar.delete('1.0', tk.END)
        for i in range(1, line_count + 2):
            self.line_number_bar.insert(tk.END, f'{i}\n')

        # Add tag to center text
        self.line_number_bar.tag_configure("center", justify='center')
        self.line_number_bar.tag_add("center", 1.0, tk.END)

        self.line_number_bar.config(state=tk.DISABLED)


    def new_file(self):
        self.file_path = filedialog.asksaveasfilename(filetypes=[("All Files", "*.*")])
        if self.file_path:
            self.text_area.delete(1.0, tk.END)
            self.update_title()
            self.load_syntax_for_extension()

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if self.file_path:
            self.plugin_manager.api.update_event("open_file", self.file_path)
            with open(self.file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, file.read())
            self.update_title()
            self.load_syntax_for_extension()

    def save_file(self):
        if self.file_path:
            try:
                with open(self.file_path, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Success", "File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        self.file_path = filedialog.asksaveasfilename(filetypes=[("All Files", "*.*")])
        if self.file_path:
            self.save_file()
            self.update_title()

    def update_title(self):
        self.root.title(f"gVim - {self.file_path if self.file_path else 'Untitled'}")

    def load_syntax_for_extension(self):
        file_extension = os.path.splitext(self.file_path)[1][1:]
        for file in os.listdir("extensions"):
            with open(f"extensions/{file}", "r") as f:
                data = json.load(f)
                if file_extension in data["scope"]:
                    self.load_syntax_rules(f"extensions/{file}")
                    self.apply_syntax_highlighting()

    def load_syntax_rules(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            self.syntax_rules = data["rules"]

    def apply_syntax_highlighting(self, event=None):
        self.text_area.tag_remove('syntax', "1.0", tk.END)
        text = self.text_area.get("1.0", tk.END)
        sorted_rules = sorted(self.syntax_rules, key=lambda x: x.get("priority", 0), reverse=True)

        for rule in sorted_rules:
            pattern = rule["pattern"]
            styles = self.get_styles(rule)
            for match in re.finditer(pattern, text, re.MULTILINE):
                start_index = f"1.0 + {match.start()} chars"
                end_index = f"1.0 + {match.end()} chars"
                tag_name = f"syntax_{match.start()}"
                self.text_area.tag_add(tag_name, start_index, end_index)
                self.text_area.tag_config(tag_name, **styles)

    def get_styles(self, rule):
        styles = {"foreground": rule["color"], "font": self.text_font}
        if "bold" in rule and rule["bold"]:
            styles["font"] = self.text_font + ("bold",)
        if "italic" in rule and rule["italic"]:
            styles["font"] = self.text_font + ("italic",)
        if "underline" in rule and rule["underline"]:
            styles["underline"] = True
        return styles

    def load_color_scheme(self, scheme_name="default"):
        if scheme_name in self.schemes:
            self.update_scheme(self.schemes[scheme_name])

    def load_default_color_scheme(self):
        self.load_color_scheme("default")

    def create_menu_bar(self):
        # Create a custom frame to act as the menu bar
        self.menu_bar_frame = tk.Frame(self.root, bg=self.current_scheme["line_bar_color"], height=30, padx=20)
        self.menu_bar_frame.pack(side="top", fill="x")
        self.menu_bar_frame.pack_propagate(False)

        # Create menu buttons (acting like menu items)
        file_button = tk.Menubutton(self.menu_bar_frame, text="File", bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"], relief="flat")
        file_button.grid(row=0, column=0, padx=5, pady=5)

        file_menu = tk.Menu(file_button, tearoff=0, bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"])
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Open Terminal Here", command=self.open_terminal)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_editor)
        file_button.config(menu=file_menu)

        # Add more menu buttons like Extensions
        extensions_button = tk.Menubutton(self.menu_bar_frame, text="Extensions", bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"], relief="flat")
        extensions_button.grid(row=0, column=1, padx=5, pady=5)

        extensions_menu = tk.Menu(extensions_button, tearoff=0, bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"])
        extensions_menu.add_command(label="Select color scheme", command=self.scheme_select)
        extensions_menu.add_command(label="Install package", command=self.install)
        extensions_menu.add_separator()
        extensions_menu.add_command(label="Install plugin", command=self.plugin_manager.install_plugin)
        extensions_menu.add_command(label="Uninstall/disable plugins", command=self.plugin_manager.uninstall_disable_plugin)
        extensions_button.config(menu=extensions_menu)

        # Add Window button for minimize and close
        window_button = tk.Menubutton(self.menu_bar_frame, text="Window", bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"], relief="flat")
        window_button.grid(row=0, column=2, padx=5, pady=5)

        window_menu = tk.Menu(window_button, tearoff=0, bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"])
        window_menu.add_command(label="Minimize", command=self.minimize_window)
        window_menu.add_command(label="Close", command=self.exit_editor)
        window_button.config(menu=window_menu)



    def open_terminal(self):
        terminal_path = self.current_scheme["default_terminal_path"]
        if terminal_path:
            self.run_terminal_command(terminal_path)
        else:
            messagebox.showerror("Error", "No terminal path provided in the current scheme")

    def run_terminal_command(self, terminal_path):
        try:
            if terminal_path == "cmd":
                os.system(f"start cmd /K cd {os.path.dirname(self.file_path)}")
            elif terminal_path == "powershell":
                os.system(f"start powershell -noexit -command Set-Location {os.path.dirname(self.file_path)}")
            else:
                os.system(f"start {terminal_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open terminal: {e}")

    def exit_editor(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()

    def update_scheme(self, scheme):
        # Update the current scheme with the new one
        self.current_scheme.update(scheme)
    
        # Update the text area colors
        self.text_font = (self.current_scheme["font_face"], self.current_scheme["font_size"])
        self.text_area.config(
            fg=self.current_scheme["foreground_color"],
            bg=self.current_scheme["background_color"],
            insertbackground=self.current_scheme["insertbackground_color"],
            font=self.text_font
        )
    
        # Update the line number bar colors
        self.line_number_bar.config(
            bg=self.current_scheme["line_bar_color"],
            fg=self.current_scheme["line_number_color"],
            font=(self.current_scheme["font_face"], self.current_scheme["line_number_font_size"])
        )
        font = self.line_number_bar.cget("font")
        if self.current_scheme["line_number_bold"]:
            font += " bold"
        if self.current_scheme["line_number_italic"]:
            font += " italic"
        self.line_number_bar.config(font=font)
    
        # Update menu bar colors
        self.update_menu_bar_colors()

    def update_menu_bar_colors(self):
        """Update the background and text colors of the menu bar and its items."""
        self.menu_bar_frame.config(bg=self.current_scheme["line_bar_color"])
        for child in self.menu_bar_frame.winfo_children():
            child.config(bg=self.current_scheme["line_bar_color"], fg=self.current_scheme["foreground_color"])


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
