my_project/ 
│
├── main.py               # Entry point of the application
├── gui/                  # Folder for GUI-related code
│   ├── __init__.py       # Mark this folder as a package
│   ├── main_window.py    # Main window class, contains the GUI layout, menu, and toolbar
│   ├── toolbar.py        # Toolbar-related code, like toolbar actions and buttons
│   ├── menu.py           # Menu bar-related code
│   ├── widgets.py        # Custom widgets (e.g., custom buttons, draggable items, etc.)
│   ├── dialogs.py        # Dialog windows (e.g., File dialogs, settings dialogs, etc.)
│   └── graphics.py       # Graphics view and scene-related code
│
├── utils/                # Utility functions or helpers
│   ├── __init__.py       # Mark this folder as a package
│   └── file_utils.py     # For file operations, e.g., saving/loading data
│
├── assets/               # Folder for icons, images, stylesheets, etc.
│   ├── icon.png
│   └── style.qss
│
└── requirements.txt      # List of dependencies (if using pip)