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

## Packages

- Packages are single json files that contain a theme and syntax highlighting files.
- Package example:
  ```json
  {
    "name": "onedarkpro",
    "theme": {
      "background": "#282c34",
      "foreground": "#abb2bf",
      "cursor": "#528bff",
      "black": "#282c34",
      "red": "#e06c75",
      "green": "#98c379",
      "yellow": "#e5c07b",
      "blue": "#61afef",
      "magenta": "#c678dd",
      "cyan": "#56b6c2",
      "white": "#abb2bf",
      "brightBlack": "#5c6370",
      "brightRed": "#e06c75",
      "brightGreen": "#98c379",
      "brightYellow": "#e5c07b",
      "brightBlue": "#61afef",
      "brightMagenta": "#c678dd",
      "brightCyan": "#56b6c2",
      "brightWhite": "#dcdfe4"
    },
    "syntaxes": {
      "c++": [
        {
          "scope": ["c++", "cpp"],
          "rules": [
            {
              "pattern": "//.*",
              "color": "#888888",
              "description": "Comments",
              "priority": 1
            },
            {
              "pattern": "\\b(namespace|using|typedef|class|struct|enum|if|else|for|while|do|try|catch|finally|return|throw|switch|case|break|continue|default|int|char|unsigned|signed|long|double|bool|float|void)\\b",
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
      ]
    }
  }
  ```
