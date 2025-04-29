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


class OutputPropertyEditor(QWidget):
    def __init__(self):
        """Initialize the output property editor."""
        super().__init__()
        self.setFixedWidth(300)
        self.widget_list = []
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        
        # Output list label
        self.output_label = QLabel("Output list:")
        self.layout.addWidget(self.output_label)
        
        # Add button
        self.add_button = QPushButton("+ Add Output")
        self.layout.addWidget(self.add_button)
        
        # List widget
        self.output_list = QListWidget()
        self.layout.addWidget(self.output_list)
        
        # Connect signals
        self.add_button.clicked.connect(self.add_item)
        
        # Current TOSPN reference
        self.TOSPN = None
        self.output_parser = None
    
    def set_TOSPN(self, TOSPN):
        """Set the TOSPN model and initialize parser."""
        self.TOSPN = TOSPN
        from utils.other_utils import OutputParser
        self.output_parser = OutputParser(self.TOSPN)
        self.reset_list()
    
    def reset_list(self):
        """Clear and repopulate the list."""
        self.output_list.clear()
        if self.TOSPN:
            for output in self.TOSPN.outputs.values():
                self.add_to_list(
                    output.name,
                    output.retrieve_marking_name_expression(self.TOSPN.places),
                    output
                )
    


    def update_expressions(self):
        """Update all output expressions."""
        if self.output_parser:
            self.output_parser.update_parsing_element()
            for widget in self.widget_list:
                widget.expression_label.setText(widget.output.retrieve_marking_name_expression())


    def add_item(self):
        """Open dialog to add a new output."""
        if not self.TOSPN:
            return
            
        dialog = AddOutputDialog(self.TOSPN, self)
        if dialog.exec_() == QDialog.Accepted:
            name, txt_expression, txt_id_expression, math_expression = dialog.get_value()
            if name and txt_expression:
                output = self.TOSPN.add_output(name, math_expression, txt_id_expression)
                self.add_to_list(name, txt_expression, output)
    
    def add_to_list(self, name, expression, output):
        """Add an output to the list widget."""
        # Create list item and widget
        item = QListWidgetItem(self.output_list)
        
        # Create container widget
        container = QWidget()
        item_layout = QVBoxLayout(container)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        
        # Create output widget
        widget = OutputListItemWidget(name, expression, output, self.TOSPN, container)
        widget.remove_requested.connect(lambda: self.remove_item(item, widget))
        widget.edit_requested.connect(lambda: self.edit_item(item, widget))
        item_layout.addWidget(widget)
        
        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        item_layout.addWidget(line)
        
        # Set up container
        container.setLayout(item_layout)
        item.setSizeHint(container.sizeHint())
        self.output_list.setItemWidget(item, container)
        self.widget_list.append(widget)
    
        item.setSizeHint(widget.sizeHint())
        self.output_list.addItem(item)
        self.output_list.setItemWidget(item, widget)
        return item, widget
    
    def remove_item(self, item, widget):
        """Remove an output from the list and TOSPN model."""
        # Remove listeners from places
        for place in self.TOSPN.places.values():
            place.remove_listener(widget)
        
        # Remove listener from output
        widget.output.remove_listener(widget)
        
        # Remove output from TOSPN
        self.TOSPN.remove_output(widget.output)
        
        # Remove widget and item
        row = self.output_list.row(item)
        self.output_list.takeItem(row)
        widget.deleteLater()

    def edit_item(self, item, widget):
        """Open dialog to edit an output."""
        dialog = AddOutputDialog(self.TOSPN, self, widget)
        if dialog.exec_() == QDialog.Accepted:
            name, txt_expression, txt_id_expression, math_expression = dialog.get_value()
            widget.set_value(name, txt_expression, txt_id_expression, math_expression)
            #item.setSizeHint(widget.container.sizeHint())

class OutputListItemWidget(QWidget):
    """Widget for displaying and editing an output in the list."""
    remove_requested = Signal()
    edit_requested = Signal()

    def __init__(self, name, expression, output, TOSPN, container):
        super().__init__()
        self.output = output
        self.container = container
        self.TOSPN = TOSPN
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
        
        # Separator
        self.separator_label = QLabel(": ")
        self.separator_label.setWordWrap(True)
        self.separator_label.setMaximumWidth(15)
        self.layout.addWidget(self.separator_label)
        self.layout.setAlignment(self.separator_label, Qt.AlignLeft)
        
        # Expression label
        self.expression_label = QLabel(expression)
        self.expression_label.setWordWrap(True)
        self.expression_label.setMaximumWidth(1000)
        self.layout.addWidget(self.expression_label)
        self.layout.setAlignment(self.expression_label, Qt.AlignLeft)

        # Spacer
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addSpacerItem(self.spacer)

        # Remove button
        self.remove_button = QPushButton("-")
        self.remove_button.setFixedSize(50, 20)
        self.layout.addWidget(self.remove_button)

        # Connect signals
        self.name_label.mouseDoubleClickEvent = self.request_edit
        self.remove_button.clicked.connect(self.remove_requested.emit)
        
        # Add as listener to output

        # Add listeners
        self.output.add_listener(self)
        for place in self.TOSPN.places.values():
            place.add_listener(self)
    
    def on_change(self, subject, event_type, data):
        """Handle changes in the output or places."""
        if event_type == "name_changed":
            if hasattr(subject, 'type') and subject.type == "place":
                # A place name was changed, update the expression display
                expression = self.TOSPN.get_output_expression_with_names(self.output)
                self.expression_label.setText(expression)
                
            else:
                # The output name was changed
                self.name_label.setText(data["new"])
        elif event_type == "expression_changed":
            expression = self.TOSPN.get_output_expression_with_names(self.output)
            self.expression_label.setText(expression)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.request_edit(event)

    def request_edit(self, event):
        self.edit_requested.emit()

    def set_value(self, name, txt_expression, txt_id_expression, math_expression):
        """Update the widget with new values."""
        #self.name_label.setText(name)
        #self.expression_label.setText(txt_expression)
        self.output.update_expression(math_expression, txt_id_expression)

    def sizeHint(self):
        return QSize(200, 50)  # Adjust size as needed

class AddOutputDialog(QDialog):
    """Dialog for adding or editing an output."""
    def __init__(self, TOSPN, editor, widget=None):
        super().__init__()
        self.TOSPN = TOSPN
        self.editor = editor
        self.output_parser = editor.output_parser
        
        if widget:
            self.initial_name = widget.output.name
            self.initial_expression = widget.output.retrieve_marking_name_expression(self.TOSPN.places)
        else:
            self.initial_name = ""
            self.initial_expression = ""
        
        self.setWindowTitle("Edit Output" if widget else "Add New Output")
        self.setModal(True)
        
        # Layout
        self.layout = QVBoxLayout(self)
        
        # Name field
        self.name_label = QLabel("Enter output name:")
        self.name_edit = QLineEdit(self.initial_name)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)
        
        # Expression field
        self.exp_label = QLabel("Enter output expression:")
        self.expression_edit = QLineEdit(self.initial_expression)
        self.layout.addWidget(self.exp_label)
        self.layout.addWidget(self.expression_edit)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttons)
        
        # Set up OK button
        self.ok_button = self.buttons.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(bool(self.initial_name))
        
        # Connect signals
        self.name_edit.textChanged.connect(self.validate_input)
        self.expression_edit.textChanged.connect(self.validate_input)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
    
    def validate_input(self):
        """Validate the input fields."""
        print("try validating input")
        name = self.name_edit.text()
        expression = self.expression_edit.text()
        self.ok_button.setEnabled(
            self.validate_name(name) and 
            self.validate_expression(expression)
        )
        print(f"name: {name} {self.validate_name(name)}")
        print(f"expression: {expression} {self.validate_expression(expression)}")
    
    def validate_name(self, name):
        """Check if the name is valid."""
        if not name or "?" in name:
            return False
            
        # Check if name is unique (except for current output)
        if name != self.initial_name and name in self.TOSPN.output_names:
            return False
            
        return True
    
    def validate_expression(self, expression):
        """Check if the expression is valid."""
        self.output_parser.update_parsing_element()
        return self.output_parser.check_validity(expression)
    
    def get_value(self):
        """Return the output values."""
        result = self.output_parser.tryParsing(self.expression_edit.text())
        math_expression = self.output_parser.reformat_math_expression(result[1].asList())
        txt_expression = self.output_parser.reformat_txt(result[1].asList())
        txt_id_expression = self.output_parser.reformat_id_txt(result[1].asList())
        return self.name_edit.text(), txt_expression, txt_id_expression, math_expression
