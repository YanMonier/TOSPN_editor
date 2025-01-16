from PySide2.QtWidgets import (
	QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget, QDialog,
	QLineEdit, QLabel, QDialogButtonBox, QWidget, QListWidgetItem
)
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt


class AddItemDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Add New Item")
		self.setModal(True)

		# Layout and Widgets
		self.layout = QVBoxLayout(self)
		self.label = QLabel("Enter Parameter (e.g., Number > 0):")
		self.line_edit = QLineEdit()
		self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

		self.layout.addWidget(self.label)
		self.layout.addWidget(self.line_edit)
		self.layout.addWidget(self.buttons)

		# Disable the OK button initially
		self.ok_button = self.buttons.button(QDialogButtonBox.Ok)
		self.ok_button.setEnabled(False)

		# Connect signals
		self.line_edit.textChanged.connect(self.validate_input)
		self.buttons.accepted.connect(self.accept)  # Ensure "OK" closes the dialog
		self.buttons.rejected.connect(self.reject)  # Cancel closes the dialog

	def get_value(self):
		return self.line_edit.text()

	def validate_input(self):
		"""Validate the input and enable/disable the OK button."""
		if self.validate():
			self.ok_button.setEnabled(True)
		else:
			self.ok_button.setEnabled(False)

	def validate(self):
		"""Example validation: input must be a positive number."""
		try:
			value = float(self.get_value())
			return value > 0
		except ValueError:
			return False


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Property Editor")

		# Main widget and layout
		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)
		self.layout = QVBoxLayout(self.central_widget)

		# List widget
		self.list_widget = QListWidget()
		self.layout.addWidget(self.list_widget)

		# Add button
		self.add_button = QPushButton("+ Add Item")
		self.layout.addWidget(self.add_button)

		# Connect signals
		self.add_button.clicked.connect(self.add_item)

	def add_item(self):
		dialog = AddItemDialog()
		if dialog.exec_() == QDialog.Accepted:
			value = dialog.get_value()
			if dialog.validate():
				self.add_to_list(value, valid=True)
			else:
				self.add_to_list(value, valid=False)

	def add_to_list(self, value, valid):
		item = QListWidgetItem(value)
		if not valid:
			item.setForeground(QColor('red'))  # Highlight invalid item
		self.list_widget.addItem(item)


if __name__ == "__main__":
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec_()
