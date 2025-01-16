from PySide2.QtWidgets import QMenuBar, QMenu, QAction
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

class Menu:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = self.main_window.menuBar()

        # Create menus
        self.create_file_menu()
        self.create_edit_menu()
        self.create_help_menu()

    def create_file_menu(self):
        file_menu = QMenu("File", self.menu_bar)
        self.menu_bar.addMenu(file_menu)

        # Define actions
        new_action = QAction("New", self.main_window)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self.main_window)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self.main_window)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self.main_window)
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)

    def create_edit_menu(self):
        edit_menu = QMenu("Edit", self.menu_bar)
        self.menu_bar.addMenu(edit_menu)

        # Define actions
        cut_action = QAction("Cut", self.main_window)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self.main_window)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self.main_window)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_action)
        edit_menu.addAction(paste_action)

    def create_help_menu(self):
        help_menu = QMenu("Help", self.menu_bar)
        self.menu_bar.addMenu(help_menu)

        # Define actions
        about_action = QAction("About", self.main_window)
        about_action.triggered.connect(self.about_app)
        help_menu.addAction(about_action)

    # Slot methods
    def new_file(self):
        print("New file created")

    def open_file(self):
        print("Open file action triggered")

    def save_file(self):
        print("Save file action triggered")

    def exit_app(self):
        print("Exiting application")
        self.main_window.close()

    def cut_action(self):
        print("Cut action triggered")

    def copy_action(self):
        print("Copy action triggered")

    def paste_action(self):
        print("Paste action triggered")

    def about_app(self):
        print("About application dialog")