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


class ArcPropertyEditorTLSPN (QWidget):
	def __init__(self):
		"""Initialize the place property editor."""
		super().__init__()
		self.setFixedWidth(300)

		# Layout
		self.layout = QVBoxLayout(self)
		self.layout.setAlignment(Qt.AlignTop)

		# Properties section (hidden by default)
		self.arc_properties_section = QWidget()
		self.arc_properties_layout = QVBoxLayout(self.arc_properties_section)

		# ID field
		self.id_field = QLabel("Arc ID: ")
		self.arc_properties_layout.addWidget(self.id_field)


		# weight section
		self.weight_layout = QHBoxLayout()
		self.weight_field = QSpinBox()
		self.weight_field.setRange(0, 1000000)
		self.weight_label = QLabel("Weight:")
		self.weight_layout.addWidget(self.weight_label)
		self.weight_layout.addWidget(self.weight_field)
		self.arc_properties_layout.addLayout(self.weight_layout)

		# Connect signals
		# self.name_field.textChanged.connect(self.update_name)
		self.weight_field.valueChanged.connect(self.update_weight)

		# Add to layout
		self.arc_properties_section.setLayout(self.arc_properties_layout)
		self.layout.addWidget(self.arc_properties_section)
		self.arc_properties_section.hide()

		# Current place reference
		self.current_arc = None
		self.current_graphic = None

	def on_change(self, subject, event_type, data):
		"""Handle changes in the place model."""
		if event_type == "weight_changed":
			if data != self.weight_field.value():
				self.weight_field.setValue(data)


	def update_weight(self, new_value):
		"""Update the number of tokens."""
		if self.current_arc and new_value != self.current_arc.weight:
			self.current_arc.set_weight(new_value)



	def update_properties(self, graphic_arc):
		"""Update the editor with a new place."""
		# Remove listener from old place
		if self.current_arc:
			self.current_arc.remove_listener(self)

		# Update references
		self.current_arc = graphic_arc
		self.current_arc = graphic_arc.arc

		# Add as listener to new place
		self.current_arc.add_listener(self)

		# Show properties section
		self.arc_properties_section.show()

		# Update fields
		self.id_field.setText(f"Arc ID: A.{self.current_arc.id}")
		self.weight_field.setValue(self.current_arc.weight)