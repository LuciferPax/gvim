# Simple Text Editor - README

## Overview

This is a simple text editor built using Python's Tkinter library. It supports basic text editing features and syntax highlighting based on custom JSON configuration files.

## Features

- Basic text editing (open, save, new file)
- Line number display
- Syntax highlighting using custom JSON files located in Extensions folder
- Custom schemes located in themes folder

## Installation

1. Ensure you have Python 3.x installed.
2. Install the required libraries (if not already available):
   ```bash
   pip install tk
   ```

## Usage

1. Clone onto your current matchine
2. cd into the folder
3. Run the text editor with the follow command:
   ```bash
   python gvim.py
   ```

## Custom Syntax Json examples

- Cpp example:
  ```json
  {
    "scope": ["c++", "cpp"],
    "rules": [
      {
        "pattern": "\\b(namespace|using|typedef|class|struct|enum|if|else|else if|for|while|do|try|catch|finally|return|throw|switch|case|break|continue|default|int|char|unsigned|signed|long|double|bool|float|void)\\b",
        "color": "#E8E466",
        "description": "Keywords for control structures and definitions",
        "bold": true,
        "priority": 5
      },
      {
        "pattern": "#[^\\s]+",
        "color": "#BA80E7",
        "description": "Preprocessor directives",
        "priority": 4
      },
      {
        "pattern": "\"[^\"]*\"",
        "color": "#6CD567",
        "description": "String literals",
        "priority": 3
      },
      {
        "pattern": "\\b(\\+\\+|\\+|\\-\\-|\\-|\\*|\\/|\\%|\\=|\\+=|\\-=|\\*=|\\/=|\\%=|\\&\\&|\\|\\||\\!|\\=\\=|\\!\\=|\\<|\\>|\\<\\=|\\>\\=|\\&|\\||\\^|\\~|\\<\\<|\\>\\>|\\>\\>\\>)\\b",
        "color": "#E8E466",
        "description": "Operators",
        "bold": false,
        "priority": 6
      },
      {
        "pattern": "\\b[A-Za-z_][A-Za-z0-9_]*\\b(?=\\s*\\:\\:)",
        "color": "#E8E466",
        "description": "Namespace or class names",
        "bold": false,
        "priority": 7
      }
    ]
  }
  ```

## Notes

- Cpp syntax syntax json provided in extensions folder
- 5 custom schemes provided in themes folder
