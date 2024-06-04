# Simple Text Editor - README

## Overview
This is a simple text editor built using Python's Tkinter library. It supports basic text editing features and syntax highlighting based on custom JSON configuration files.

## Features
- Basic text editing (open, save, new file)
- Line number display
- Syntax highlighting using custom JSON files
- Configurable color schemes
- Open terminal in the current file's directory

## Installation
1. Ensure you have Python 3.x installed.
2. Install the required libraries (if not already available):
   ```bash
   pip install tk

## Usage
Run the text editor with the follow command:
   ```bash
   python gvim.py
   
## Custom Syntax Json examples
```json
{
    "scheme": {
        "font_face": "Consolas",
        "font_size": 12,
        "background_color": "#0D1117",
        "foreground_color": "#C6C6C6",
        "insertbackground_color": "#FFFFFF",
        "default_terminal_path": "cmd",
        "line_bar_color": "#21262d",
        "line_number_color": "#6e7681",
        "tab_size": 4,
        "line_number_font_size": 12,
        "line_number_bold": true,
        "line_number_italic": false
    },
 
    "syntax_rules": [
        {
            "pattern": "\\b(import|from|def|class|if|else|elif|for|while|try|except|finally|raise|return|yield|with|as|assert|break|continue|pass|lambda)\\b",
            "color": "#E8E466",
            "description": "Keywords for control structures and definitions",
            "bold": true,
            "priority": 1
        }
    ]
}
