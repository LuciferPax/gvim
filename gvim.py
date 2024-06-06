import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import json
import re
import os
import subprocess

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Text Editor")
        self.root.geometry("900x600")

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
            "line_number_font_size": 14,
            "line_number_bold": False,
            "line_number_italic": False
        }
        self.current_scheme = self.default_scheme.copy()

        # Font initialization
        self.text_font = (self.current_scheme["font_face"], self.current_scheme["font_size"])

        # Frame to contain both the text area and the line numbers
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Line number bar
        self.line_number_bar = tk.Text(self.main_frame, width=4, padx=3, takefocus=0, border=0, background="#3E3E3E", foreground="#5A5A5A", wrap=tk.NONE)
        self.line_number_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Text area
        self.text_area = tk.Text(self.main_frame, wrap='word', fg=self.current_scheme["foreground_color"], bg=self.current_scheme["background_color"], font=self.text_font, insertbackground=self.current_scheme["insertbackground_color"], undo=True, autoseparators=True)
        self.text_area.pack(expand='yes', fill='both')

        # Scroll bars
        self.text_area.bind('<KeyRelease>', self.update_line_numbers_on_change)
        self.text_area.bind('<KeyPress>', self.update_line_numbers_on_change)
        self.text_area.bind('<MouseWheel>', self.update_line_numbers_on_change)
        self.text_area.bind('<Configure>', self.update_line_numbers_on_change)
        
        self.text_area.tag_configure('center', justify='center')

        self.schemes = {
            "default": self.default_scheme,
            "neovim": {
                "font_face": "Fira Code",
                "font_size": 14,
                "background_color": "#1E1E1E",
                "foreground_color": "#C6C6C6",
                "insertbackground_color": "#FFFFFF",
                "default_terminal_path": None
            }
        }

        self.syntax_rules = []

        # Initial color scheme
        self.load_default_color_scheme()
        self.save_schemes_in_themes()

        # Menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open Terminal Here", command=self.open_terminal)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_editor)

        self.syntax_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Scheme", menu=self.syntax_menu)
        self.syntax_menu.add_command(label="Select Scheme", command=self.scheme_select)

        self.file_path = None

    def update_line_numbers_on_change(self, event=None):
        self.update_line_numbers()
        self.apply_syntax_highlighting()
        self.line_number_bar.yview_moveto(self.text_area.yview()[0])

    def apply_color_scheme(self):
        selected_scheme = self.scheme_select_combobox.get()
        self.load_color_scheme(selected_scheme)
        self.scheme_select.destroy()

    def save_schemes_in_themes(self):
        themes = os.listdir("themes")
        for theme in themes:
            if theme.endswith(".json"):
                with open(f"themes/{theme}", "r") as file:
                    name = theme.split(".")[0]
                    self.schemes[name] = json.load(file)

    def scheme_select(self):
        # dropdown with apply button to change the color scheme
        self.scheme_select = tk.Toplevel(self.root)
        self.scheme_select.title("Select Scheme")
        self.scheme_select.geometry("300x100")
        self.scheme_select.resizable(False, False)

        self.scheme_select_label = tk.Label(self.scheme_select, text="Select Scheme")
        self.scheme_select_label.pack()

        self.scheme_select_combobox = ttk.Combobox(self.scheme_select, values=list(self.schemes.keys()))
        self.scheme_select_combobox.pack()

        self.scheme_select_apply_button = tk.Button(self.scheme_select, text="Apply", command=self.apply_color_scheme)
        self.scheme_select_apply_button.pack()

    def update_line_numbers(self):
        line_count = self.text_area.get('1.0', 'end').count('\n')
        self.line_number_bar.config(state=tk.NORMAL)
        self.line_number_bar.delete('1.0', tk.END)
        for line in range(1, line_count + 2):
            self.line_number_bar.insert(tk.END, f'{line}\n')
        self.line_number_bar.config(state=tk.DISABLED)

    def new_file(self):
        self.file_path = filedialog.asksaveasfilename(
          filetypes=[("All Files", "*.*")]
        )
        if self.file_path:
            self.text_area.delete(1.0, tk.END)
            self.update_title()

            file_extension = os.path.splitext(self.file_path)[1][1:]
            for file in os.listdir("extensions"):
                with open(f"extensions/{file}", "r") as f:
                    data = json.load(f)
                    if file_extension in data["scope"]:
                        self.load_syntax_rules(f"extensions/{file}")
                        self.apply_syntax_highlighting()

    def open_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")]
        )
        if self.file_path:
            self.text_area.delete(1.0, tk.END)
            with open(self.file_path, 'r') as file:
                self.text_area.insert(1.0, file.read())
            self.update_title()

            file_extension = os.path.splitext(self.file_path)[1][1:]
            for file in os.listdir("extensions"):
                with open(f"extensions/{file}", "r") as f:
                    data = json.load(f)
                    if file_extension in data["scope"]:
                        self.load_syntax_rules(f"extensions/{file}")
                        self.apply_syntax_highlighting()

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
        self.file_path = filedialog.asksaveasfilename(
            filetypes=[("All Files", "*.*")]
        )
        if self.file_path:
            self.save_file()
            self.update_title()

    def update_title(self):
        self.root.title(f"Simple Text Editor - {self.file_path if self.file_path else 'Untitled'}")

    def load_syntax_rules(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            self.syntax_rules = data["rules"]


    def apply_syntax_highlighting(self, event=None):
    # Clear previous tags
        for tag in self.text_area.tag_names():
            self.text_area.tag_delete(tag)

        text = self.text_area.get("1.0", tk.END)

        # Sort syntax rules based on priority
        sorted_rules = sorted(self.syntax_rules, key=lambda x: x.get("priority", 0), reverse=True)

        for rule in sorted_rules:
            pattern = rule["pattern"]
            color = rule["color"]
            styles = {
                "foreground": color,
                "font": self.text_font
            }
            if "bold" in rule and rule["bold"]:
                styles["font"] = self.text_font + ("bold",)
            if "italic" in rule and rule["italic"]:
                styles["font"] = self.text_font + ("italic",)
            if "underline" in rule and rule["underline"]:
                styles["underline"] = True

            for match in re.finditer(pattern, text, re.MULTILINE):
                start_index = f"1.0 + {match.start()} chars"
                end_index = f"1.0 + {match.end()} chars"
                tag_name = f"{pattern}_{match.start()}"
                self.text_area.tag_add(tag_name, start_index, end_index)
                self.text_area.tag_config(tag_name, **styles)
            
        

    def load_color_scheme(self, scheme_name="default"):
        if scheme_name in self.schemes:
            self.update_scheme(self.schemes[scheme_name])

    def load_default_color_scheme(self):
        self.load_color_scheme("default")

    def load_neovim_color_scheme(self):
        self.load_color_scheme("neovim")

    def open_terminal(self, terminal_type=None):
        if self.current_scheme["default_terminal_path"]:
            terminal_path = self.current_scheme["default_terminal_path"]
            if terminal_path:
                if terminal_path == "cmd":
                    os.system(f"start cmd /K cd {os.path.dirname(self.file_path)}")
                elif terminal_path == "powershell":
                    os.system(f"start powershell -noexit -command Set-Location {os.path.dirname(self.file_path)}")
                else:
                    os.system(f"start {terminal_path}")
            else:
                messagebox.showerror("Error", "No terminal path provided in the current scheme")

    def exit_editor(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()

    def update_scheme(self, scheme):
        self.current_scheme.update(scheme)
        self.text_font = (self.current_scheme["font_face"], self.current_scheme["font_size"])
        self.text_area.config(
            fg=self.current_scheme["foreground_color"],
            bg=self.current_scheme["background_color"],
            insertbackground=self.current_scheme["insertbackground_color"],
            font=self.text_font
        )
        self.line_number_bar.config(
            bg=self.current_scheme["line_bar_color"],
            fg=self.current_scheme["line_number_color"],
            font=(self.current_scheme["font_face"], self.current_scheme["line_number_font_size"])
        )
        if self.current_scheme["line_number_bold"]:
            font = self.line_number_bar.cget("font") + " bold"
        else:
            font = self.line_number_bar.cget("font")
        if self.current_scheme["line_number_italic"]:
            font += " italic"
        self.line_number_bar.config(font=font)

        # Adjust tab size
        self.text_area.config(tabs=self.current_scheme["tab_size"])

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
