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

class TransitionPropertyEditor(QWidget):
    def __init__(self):
        """Initialize the transition property editor."""
        super().__init__()
        self.setFixedWidth(300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # Properties section (hidden by default)
        self.transition_properties_section = QWidget()
        self.transition_properties_layout = QVBoxLayout(self.transition_properties_section)

        # ID field
        self.id_field = QLabel("Transition ID: ")
        self.transition_properties_layout.addWidget(self.id_field)

        # Name section
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("Transition name: ")
        self.name_field = QLineEdit()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_field)
        self.transition_properties_layout.addLayout(self.name_layout)

        # Event section
        self.event_layout = QHBoxLayout()
        self.event_label = QLabel("Event: ")
        self.event_combo = QComboBox()
        self.event_layout.addWidget(self.event_label)
        self.event_layout.addWidget(self.event_combo)
        self.transition_properties_layout.addLayout(self.event_layout)

        # Timing section
        self.timing_group = QGroupBox("Timing")
        self.timing_layout = QVBoxLayout()
        
        # Min time
        self.min_time_layout = QHBoxLayout()
        self.min_time_label = QLabel("Minimum time:")
        self.min_time_field = QDoubleSpinBox()
        self.min_time_field.setRange(0, 1000000)
        self.min_time_layout.addWidget(self.min_time_label)
        self.min_time_layout.addWidget(self.min_time_field)
        self.timing_layout.addLayout(self.min_time_layout)
        
        # Max time
        self.max_time_layout = QHBoxLayout()
        self.max_time_label = QLabel("Maximum time:")
        self.max_time_field = QDoubleSpinBox()
        self.max_time_field.setRange(0, 1000000)
        self.max_time_layout.addWidget(self.max_time_label)
        self.max_time_layout.addWidget(self.max_time_field)
        self.timing_layout.addLayout(self.max_time_layout)
        
        self.timing_group.setLayout(self.timing_layout)
        self.transition_properties_layout.addWidget(self.timing_group)


        
        # Connect signals
        self.name_field.textChanged.connect(self.update_name)
        self.event_combo.currentTextChanged.connect(self.update_event)
        self.min_time_field.valueChanged.connect(self.update_timing)
        self.max_time_field.valueChanged.connect(self.update_timing)
        
        # Add to layout
        self.transition_properties_section.setLayout(self.transition_properties_layout)
        self.layout.addWidget(self.transition_properties_section)
        self.transition_properties_section.hide()
        
        # Current transition reference
        self.current_transition = None
        self.current_graphic = None
    
    def on_change(self, subject, event_type, data):
        """Handle changes in the transition model."""
        if event_type == "name_changed":
            if data["new"] != self.name_field.text():
                self.name_field.setText(data["new"])
        elif event_type == "event_changed":
            if data["new"] and data["new"].name != self.event_combo.currentText():
                self.event_combo.setCurrentText(data["new"].name)
        elif event_type == "timing_changed":
            if data[0] != self.min_time_field.value():
                self.min_time_field.setValue(data[0])
            if data[1] != self.max_time_field.value():
                self.max_time_field.setValue(data[1])
    
    def update_name(self, new_name):
        """Update the transition name."""
        if self.current_transition and new_name != self.current_transition.name:
            if self.validate_name(new_name):
                self.current_transition.change_name(new_name)
            else:
                self.name_field.setText(self.current_transition.name)
    
    def update_event(self, event_name):
        """Update the transition's associated event."""
        print("start update event")
        if self.current_transition and event_name:
            eventObject = self.current_transition.TOSPN.get_event_by_name(event_name)
            if eventObject:
                # If transition has a current event, remove it first
                if self.current_transition.event:
                    self.current_transition.event.remove_from_transition(self.current_transition)
                # Add new event
                eventObject.add_to_transition(self.current_transition)
                self.current_transition.set_event(eventObject)

            print(f"Debug: event of current transition {self.current_transition.event}")
    
    def update_timing(self):
        """Update the transition's timing."""
        if not self.current_transition:
            return
            
        min_time = self.min_time_field.value()
        max_time = self.max_time_field.value()
        
        if min_time <= max_time:
            self.current_transition.set_timing(min_time, max_time)
        else:
            # Revert to current values
            self.min_time_field.setValue(self.current_transition.timing_interval[0])
            self.max_time_field.setValue(self.current_transition.timing_interval[1])
    
    def validate_name(self, name):
        """Validate a transition name."""
        if not name:
            return False
        
        # Check for reserved words and characters
        invalid_terms = ["OR", "AND", "(", ")", "FM", "FD"]
        if any(term in name for term in invalid_terms) or " " in name:
            return False
        
        # Check uniqueness (excluding current transition)
        for transition in self.current_transition.TOSPN.transitions.values():
            if transition != self.current_transition and transition.name == name:
                return False
        
        return True
    
    def update_properties(self, graphic_transition):
        """Update the editor with a new transition."""
        # Remove listener from old transition
        if self.current_transition:
            self.current_transition.remove_listener(self)
        
        # Update references
        self.current_graphic = graphic_transition
        self.current_transition = graphic_transition.transition
        
        # Add as listener to new transition
        self.current_transition.add_listener(self)
        
        # Show properties section
        self.transition_properties_section.show()
        
        # Update fields
        self.id_field.setText(f"Transition ID: T.{self.current_transition.id}")
        self.name_field.setText(self.current_transition.name)
        
        # Update event combo box
        self.event_combo.clear()
        self.event_combo.addItem(self.current_transition.event.name)
        print(f"Debug: events {self.current_transition.TOSPN.events}")
        for event in self.current_transition.TOSPN.events.values():
            if event.name != self.current_transition.event.name:
                self.event_combo.addItem(event.name)

        # Set current event (should always have at least lambda event)
        if self.current_transition.event:
            self.event_combo.setCurrentText(self.current_transition.event.name)
        else:
            # If no event is set, default to lambda
            lambda_event = self.current_transition.TOSPN.get_event_by_name("λ")
            if lambda_event:
                lambda_event.add_transition(self.current_transition)
                self.event_combo.setCurrentText("λ")
        
        # Update timing fields
        self.min_time_field.setValue(self.current_transition.timing_interval[0])
        self.max_time_field.setValue(self.current_transition.timing_interval[1])