from PySide2.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QListWidget, QListWidgetItem, QLineEdit,
    QPushButton, QLabel, QDialog, QDialogButtonBox, QFrame, QSizePolicy
)
from PySide2.QtCore import Signal
from PySide2.QtCore import QSize, Qt


class AddItemDialog(QDialog):
    """Dialog for adding or editing an item."""
    def __init__(self, initial_value=""):
        super().__init__()
        self.setWindowTitle("Edit Item" if initial_value else "Add New Item")
        self.setModal(True)

        # Layout and Widgets
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Enter Parameter (e.g., Number > 0):")
        self.line_edit = QLineEdit(initial_value)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.buttons)

        # Disable the OK button initially if no initial value
        self.ok_button = self.buttons.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(bool(initial_value))

        # Connect signals
        self.line_edit.textChanged.connect(self.validate_input)
        self.buttons.accepted.connect(self.accept)  # OK button closes the dialog
        self.buttons.rejected.connect(self.reject)  # Cancel button closes the dialog

    def validate_input(self):
        """Enable OK button only if the input is valid."""
        if self.validate(self.line_edit.text()):
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def validate(self, value):
        """Validation logic: Ensure the input is a positive number."""
        try:
            return float(value) > 0
        except ValueError:
            return False

    def get_value(self):
        """Return the input value."""
        return self.line_edit.text()


class ListItemWidget(QWidget):
    """Custom widget for a list item, with remove and edit capabilities."""
    remove_requested = Signal()  # Signal emitted when the remove button is clicked
    edit_requested = Signal()  # Signal emitted when the value is clicked

    def __init__(self, value):
        super().__init__()
        self.layout = QHBoxLayout(self)

        # Editable value field (read-only)
        self.value_label = QLabel(value)
        self.value_label.setWordWrap(True)  # Ensure text wraps
        self.value_label.setMaximumWidth(50)  # You can adjust the width here as needed


        self.layout.addWidget(self.value_label)
        self.layout.setAlignment(self.value_label, Qt.AlignLeft)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Left, Top, Right, Bottom margins
        self.layout.setSpacing(0)

        # Remove button
        self.remove_button = QPushButton("-")
        self.remove_button.setFixedSize(50, 20)
        self.layout.addWidget(self.remove_button)

        # Connect signals
        self.value_label.mouseDoubleClickEvent = self.request_edit  # Double-click to request edit
        self.remove_button.clicked.connect(self.remove_requested.emit)



    def mousePressEvent(self, event):
        """Emit a signal to request editing if clicked on the widget."""
        self.edit_requested.emit()

    def request_edit(self, event):
        """Emit a signal to request editing."""
        self.edit_requested.emit()

    def set_value(self, value):
        """Set the displayed value."""
        self.value_label.setText(value)

    def sizeHint(self):
        """Override sizeHint to return the correct size based on QLabel content."""
        # Return the size hint based on the width of the label and the height of the content
        return self.value_label.sizeHint()


class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Property Editor")

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.list_widget)

        # Add button
        self.add_button = QPushButton("+ Add Item")
        self.layout.addWidget(self.add_button)

        # Connect signals
        self.add_button.clicked.connect(self.add_item)

    def add_item(self):
        """Open the dialog to add a new item."""
        dialog = AddItemDialog()
        if dialog.exec_() == QDialog.Accepted:
            value = dialog.get_value()
            self.add_to_list(value)

    def add_to_list(self, value):
        """Add a new custom widget to the list."""
        item = QListWidgetItem(self.list_widget)

        # Create the custom widget
        widget = ListItemWidget(value)
        widget.remove_requested.connect(lambda: self.remove_item(item))
        widget.edit_requested.connect(lambda: self.edit_item(item, widget))

        # Add a horizontal line (QFrame) between items
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        #line.setFixedWidth(100)

        # Create a layout for the item and the separator line
        container = QWidget()
        item_layout = QVBoxLayout(container)
        item_layout.setContentsMargins(0, 0, 0, 0)  # Left, Top, Right, Bottom margins
        item_layout.setSpacing(0)  # Spacing between items
        item_layout.addWidget(widget)  # Add the item widget
        item_layout.addWidget(line)  # Add a separator line

        # Set the layout for the item
        container.setLayout(item_layout)

        # Set the widget for the list item and ensure it takes the correct size hint
        #container.setFixedSize(200, 10)
        item.setSizeHint(container.sizeHint())  # Ensure proper sizing based on the custom widget's size hint

        self.list_widget.setItemWidget(item, container)
        #self.list_widget.update()

    def remove_item(self, item):
        """Remove an item from the list."""
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)

    def edit_item(self, item, widget):
        """Open the dialog to edit an existing item."""
        current_value = widget.value_label.text()
        dialog = AddItemDialog(current_value)
        if dialog.exec_() == QDialog.Accepted:
            new_value = dialog.get_value()
            widget.set_value(new_value)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
