import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QGroupBox
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
from PySide2.QtCore import QSize

from PySide2.QtWidgets import (QSizePolicy, QComboBox, QFrame, QListWidgetItem, QVBoxLayout, QWidget, QLineEdit, QSpinBox, QPushButton, QColorDialog, QSplitter, QLabel, QHBoxLayout, QDoubleSpinBox, QDialog, QListWidget,QDialogButtonBox,QSpacerItem)
from PySide2.QtCore import Qt, Signal
from gui.graphics.graphics_TOSPN import GraphPlaceItem, GraphTransitionItem, GraphArcItem, TempGraphLine

from utils.other_utils import OutputParser

class PropertyEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # Placeholder for no selection
        self.no_selection_label = QLabel("No object selected")
        self.layout.addWidget(self.no_selection_label)

        # Properties section (hidden by default)
        self.properties_section = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_section)

        # Example fields (dynamic in a real app)
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Object Name")
        self.properties_layout.addWidget(QLabel("Name:"))
        self.properties_layout.addWidget(self.name_field)

        self.x_field = QSpinBox()
        self.x_field.setRange(-1000, 1000)
        self.properties_layout.addWidget(QLabel("X Position:"))
        self.properties_layout.addWidget(self.x_field)

        #self.color_button = QPushButton("Select Color")
        #self.color_button.clicked.connect(self.choose_color)
        #self.properties_layout.addWidget(self.color_button)

        self.properties_section.setLayout(self.properties_layout)
        self.layout.addWidget(self.properties_section)
        self.properties_section.hide()  # Hidden by default

    def update_properties(self, obj):
        """Update the panel to show properties of the selected object."""
        if obj is None:
            self.properties_section.hide()
            self.no_selection_label.show()
        else:
            self.no_selection_label.hide()
            self.properties_section.show()

            # Example: Populate fields dynamically
            self.name_field.setText(obj.get("name", "Unnamed"))
            self.x_field.setValue(obj.get("x", 0))

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(f"Selected color: {color.name()}")  # Update your object's color here





