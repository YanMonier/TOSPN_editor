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


class PlacePropertyEditor(QWidget):
    def __init__(self):
        """Initialize the place property editor."""
        super().__init__()
        self.setFixedWidth(300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)


        # Properties section (hidden by default)
        self.place_properties_section = QWidget()
        self.place_properties_layout = QVBoxLayout(self.place_properties_section)

        # ID field
        self.id_field = QLabel("Place ID: ")
        self.place_properties_layout.addWidget(self.id_field)

        # Name section
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("Place name: ")
        # self.name_field.setPlaceholderText("Place name:")
        self.change_name_button = QPushButton("Change name")
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.change_name_button)
        self.change_name_button.clicked.connect(self.change_name)
        self.place_properties_layout.addLayout(self.name_layout)

        # Token section
        self.token_layout = QHBoxLayout()
        self.token_field = QSpinBox()
        self.token_field.setRange(0, 1000000)
        self.token_label = QLabel("Number of tokens:")
        self.token_layout.addWidget(self.token_label)
        self.token_layout.addWidget(self.token_field)
        self.place_properties_layout.addLayout(self.token_layout)

        # Connect signals
        #self.name_field.textChanged.connect(self.update_name)
        self.token_field.valueChanged.connect(self.update_tokens)

        # Add to layout
        self.place_properties_section.setLayout(self.place_properties_layout)
        self.layout.addWidget(self.place_properties_section)
        self.place_properties_section.hide()
        
        # Current place reference
        self.current_place = None
        self.current_graphic = None
    
    def on_change(self, subject, event_type, data):
        """Handle changes in the place model."""
        if event_type == "name_changed":
            if f'Place name: {data["new"]}' != self.name_label.text():
                self.name_label.setText(f'Place name: {data["new"]}')
        elif event_type == "token_changed":
            if data != self.token_field.value():
                self.token_field.setValue(data)
    
    def update_name(self, new_name):
        """Update the place name."""
        if self.current_place and new_name != self.current_place.name:
            if self.validate_name(new_name):
                self.current_place.TOSPN.rename_place(self.current_place, new_name)
            else:
                self.name_label.setText(f'Place name: {self.current_place.name}')
    
    def update_tokens(self, new_value):
        """Update the number of tokens."""
        if self.current_place and new_value != self.current_place.token_number:
            self.current_place.set_init_token_number(new_value)

    
    def validate_name(self, name):
        """Validate a place name."""
        if not name:
            return False
        
        # Check for reserved words and characters
        invalid_terms = ["OR", "AND", "(", ")", "FM", "FD"]
        if any(term in name for term in invalid_terms) or " " in name:
            return False
        
        # Check uniqueness (excluding current place)
        for place in self.current_place.TOSPN.places.values():
            if place != self.current_place and place.name == name:
                return False
        
        return True

    def update_properties(self, graphic_place):
        """Update the editor with a new place."""
        # Remove listener from old place
        if self.current_place:
            self.current_place.remove_listener(self)
        
        # Update references
        self.current_graphic = graphic_place
        self.current_place = graphic_place.place
        
        # Add as listener to new place
        self.current_place.add_listener(self)
        
        # Show properties section
        self.place_properties_section.show()

        # Update fields
        self.id_field.setText(f"Place ID: P.{self.current_place.id}")
        self.name_label.setText(f"Place name: {self.current_place.name}")
        self.token_field.setValue(self.current_place.token_number)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(f"Selected color: {color.name()}")  # Update your object's color here

    def change_name(self,name):
        """Open the dialog to edit an existing item."""

        dialog = ChangePlaceNameDialog(self.current_place.TOSPN,self.current_place)
        if dialog.exec_() == QDialog.Accepted:
            new_value = dialog.get_value()

            self.current_place.TOSPN.rename_place(self.current_place, new_value)
            self.current_graphic.update()



class ChangePlaceNameDialog(QDialog):
    """Dialog for adding or editing an item."""
    def __init__(self, TOSPN, placeItem=None):
        super().__init__()
        self.TOSPN = TOSPN
        self.current_place = placeItem
        if placeItem == None:
            initial_value = ""
        else:
            initial_value = placeItem.name
        self.setWindowTitle("Change Place name")
        self.setModal(True)
        self.initial_value = initial_value

        # Layout and Widgets
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Enter new name:")
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
        """Validate the place name."""
        # Check if empty
        if not value:
            return False
        
            
        # Check for invalid characters and reserved words
        invalid_terms = ["OR", "AND", "(", ")", "FM", "FD", "or", "and"]
        if any(term in value.upper() for term in invalid_terms) or " " in value:
            return False
            
        # Check uniqueness (excluding current place)
        for place in self.TOSPN.places.values():
            if place != self.current_place and place.name.upper() == value.upper():
                return False
                
        return True

    def get_value(self):
        """Return the input value."""
        return self.line_edit.text()
