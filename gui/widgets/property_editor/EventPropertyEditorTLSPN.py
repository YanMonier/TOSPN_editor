import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, \
	QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QGroupBox
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
from PySide2.QtCore import QSize

from PySide2.QtWidgets import (QSizePolicy, QComboBox, QFrame, QListWidgetItem, QVBoxLayout, QWidget, QLineEdit,
							   QSpinBox, QPushButton, QColorDialog, QSplitter, QLabel, QHBoxLayout, QDoubleSpinBox,
							   QDialog, QListWidget, QDialogButtonBox, QSpacerItem)
from PySide2.QtCore import Qt, Signal
from gui.graphics.graphics_TLSPN import GraphPlaceItemTLSPN , GraphTransitionItemTLSPN , GraphArcItemTLSPN , TempGraphLineTLSPN

from utils.other_utils import OutputParser


class EventPropertyEditorTLSPN (QWidget):
	def __init__(self):
		"""Initialize the event property editor."""
		super().__init__()
		self.setFixedWidth(300)
		self.widget_list = []

		# Layout
		self.layout = QVBoxLayout(self)
		self.layout.setAlignment(Qt.AlignTop)

		# Event list label
		self.event_label = QLabel("Event list:")
		self.layout.addWidget(self.event_label)

		# Add button
		self.add_button = QPushButton("+ Add Event")
		self.layout.addWidget(self.add_button)

		# List widget
		self.list_widget = QListWidget()
		self.layout.addWidget(self.list_widget)

		# Connect signals
		self.add_button.clicked.connect(self.add_item)

		# Current TLSPN reference
		self.TLSPN = None

	def set_TLSPN(self, TLSPN):
		"""Set the TLSPN model reference."""
		self.TLSPN = TLSPN
		self.reset_list()
		# Add existing events
		for event in self.TLSPN.events.values():
			if event.name != "λ":  # Don't show lambda event in the list
				self.add_to_list(event.name, event)

	def reset_list(self):
		"""Reset the list widget."""
		self.layout.removeWidget(self.list_widget)
		self.list_widget.deleteLater()
		self.list_widget = QListWidget()
		self.layout.addWidget(self.list_widget)
		self.widget_list = []

	def reset_self(self):
		"""Reset the entire editor."""
		self.TLSPN = None
		self.reset_list()

	def add_item(self):
		"""Open dialog to add a new event."""
		if not self.TLSPN:
			print("Debug: TLSPN is None")
			raise Exception("No TLSPN model set and opening add event dialog")

		print("Debug: Creating AddEventDialog")
		dialog = AddEventDialog(self.TLSPN)
		print("Debug: Dialog created")

		if dialog.exec_() == QDialog.Accepted:
			print("Debug: Dialog accepted")
			name = dialog.get_value()
			print(f"Debug: Got name value: {name}")
			if name and name != "λ":  # Don't allow adding lambda event
				print(f"Debug: Adding event with name: {name}")
				eventObject = self.TLSPN.add_event(name)
				print("Debug: Event added")
				self.add_to_list(name, eventObject)
				print("Debug: Event added to list")

	def add_to_list(self, name, event):
		"""Add a new event widget to the list."""
		item = QListWidgetItem(self.list_widget)

		# Create container widget
		container = QWidget()
		item_layout = QVBoxLayout(container)
		item_layout.setContentsMargins(0, 0, 0, 0)
		item_layout.setSpacing(0)

		# Create event widget
		widget = EventListItemWidget(name, event)
		widget.remove_requested.connect(lambda:self.remove_item(item, widget))
		widget.edit_requested.connect(lambda:self.edit_item(item, widget))
		item_layout.addWidget(widget)

		# Add separator line
		line = QFrame()
		line.setFrameShape(QFrame.HLine)
		line.setFrameShadow(QFrame.Sunken)
		item_layout.addWidget(line)

		# Set up container
		container.setLayout(item_layout)
		item.setSizeHint(container.sizeHint())
		self.list_widget.setItemWidget(item, container)
		self.widget_list.append(widget)

	def remove_item(self, item, widget):
		"""Remove an event from the list."""
		if not widget.eventItem.transitions:  # Only remove if no transitions use this event
			self.TLSPN.remove_event(widget.eventItem)
			row = self.list_widget.row(item)
			self.list_widget.takeItem(row)
			self.widget_list.remove(widget)

	def edit_item(self, item, widget):
		"""Open dialog to edit an event."""
		eventItem = widget.eventItem
		dialog = AddEventDialog(self.TLSPN, eventItem)
		if dialog.exec_() == QDialog.Accepted:
			new_name = dialog.get_value()
			if new_name and new_name != "λ":  # Don't allow renaming to lambda
				self.TLSPN.rename_event(eventItem, new_name)


class EventListItemWidget(QWidget):
	"""Widget for displaying and editing an event in the list."""
	remove_requested = Signal()
	edit_requested = Signal()

	def __init__(self, name, eventItem):
		super().__init__()
		self.eventItem = eventItem

		# Layout
		self.layout = QHBoxLayout(self)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.setSpacing(0)

		# Name label
		self.name_label = QLabel(name)
		self.name_label.setWordWrap(True)
		self.name_label.setMaximumWidth(150)
		self.layout.addWidget(self.name_label)
		self.layout.setAlignment(self.name_label, Qt.AlignLeft)

		# Remove button
		self.remove_button = QPushButton("-")
		self.remove_button.setFixedSize(50, 20)
		self.layout.addWidget(self.remove_button)

		# Connect signals
		self.name_label.mouseDoubleClickEvent = self.request_edit
		self.remove_button.clicked.connect(self.remove_requested.emit)

		# Add as listener to the event
		self.eventItem.add_listener(self)

	def on_change(self, subject, event_type, data):
		"""Handle changes in the event model."""
		if event_type == "event_name_changed":
			self.name_label.setText(data["new"])

	def mousePressEvent(self, event):
		"""Handle mouse press events."""
		self.edit_requested.emit()

	def request_edit(self, event):
		"""Handle edit requests."""
		self.edit_requested.emit()

	def set_value(self, name):
		"""Update the event name."""
		self.eventItem.change_name(name)

	def sizeHint(self):
		"""Return the widget's size hint."""
		return self.name_label.sizeHint()


class AddEventDialog(QDialog):
	"""Dialog for adding or editing an event."""

	def __init__(self, TLSPN, eventItem=None):
		print("Debug: Initializing AddEventDialog")
		super().__init__()
		print(f"Debug: TLSPN: {TLSPN}")
		print(f"Debug: event: {eventItem}")
		self.TLSPN = TLSPN
		self.eventItem = eventItem

		if self.eventItem == None:
			self.initial_name = ""
		else:
			self.initial_name = eventItem.name
		print(f"Debug: initial_name: {self.initial_name}")
		self.setWindowTitle("Edit Event" if self.eventItem else "Add New Event")
		self.setModal(True)

		# Layout
		self.layout = QVBoxLayout(self)

		# Name field
		self.label = QLabel("Enter event name:")
		self.line_edit = QLineEdit(self.initial_name)
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.line_edit)

		# Buttons
		self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		self.layout.addWidget(self.buttons)

		# Set up OK button
		self.ok_button = self.buttons.button(QDialogButtonBox.Ok)
		self.ok_button.setEnabled(False)  # Start disabled until valid input

		# Connect signals
		self.line_edit.textChanged.connect(self.validate_input)
		self.buttons.accepted.connect(self.accept)
		self.buttons.rejected.connect(self.reject)

	def validate_input(self):
		"""Validate the input name."""
		name = self.line_edit.text()
		self.ok_button.setEnabled(self.validate_name(name))

	def validate_name(self, name):
		"""Check if the name is valid."""
		# Check if empty or contains invalid characters
		if not name or "?" in name or " " in name:
			return False

		# Don't allow lambda event name
		if name == "λ":
			return False

		# Check if name is unique (except for current event)
		if name != self.initial_name and name in self.TLSPN.event_names:
			return False

		if name != self.initial_name and name in self.TLSPN.output_names:
			return False

		return True

	def get_value(self):
		"""Return the event name."""
		return self.line_edit.text()
