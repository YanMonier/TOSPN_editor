from PySide2.QtWidgets import QToolBar, QAction, QToolButton
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

class CustomToolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Main Toolbar")

        # Add actions to the toolbar
        self.add_action("Open", "open.png", self.open_file)
        self.add_action("Save", "save.png", self.save_file)
        self.add_action("Zoom In", "zoom_in.png", self.zoom_in)
        self.add_action("Zoom Out", "zoom_out.png", self.zoom_out)
        self.add_action("Toggle Edit Mode", "edit_mode.png", self.toggle_edit_mode)

    def add_action(self, name, icon, callback):
        """
        Create a QAction with an icon and a callback, and add it to the toolbar.
        """
        action = QAction(QIcon(f"assets/{icon}"), name, self)
        action.triggered.connect(callback)  # Connect the action's triggered signal to the callback
        self.addAction(action)

    def open_file(self):
        """
        Action to open a file (to be implemented).
        """
        print("Open file clicked")

    def save_file(self):
        """
        Action to save a file (to be implemented).
        """
        print("Save file clicked")

    def zoom_in(self):
        """
        Action to zoom in (to be implemented).
        """
        print("Zoom in clicked")

    def zoom_out(self):
        """
        Action to zoom out (to be implemented).
        """
        print("Zoom out clicked")

    def toggle_edit_mode(self):
        """
        Action to toggle edit mode (to be implemented).
        """
        print("Edit mode toggled")