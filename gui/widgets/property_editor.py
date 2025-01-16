
import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen

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



class PlacePropertyEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)


        # Properties section (hidden by default)
        self.place_properties_section = QWidget()
        self.place_properties_layout = QVBoxLayout(self.place_properties_section)

        # Example fields (dynamic in a real app)

        self.id_field = QLabel("Place Object ID: ")
        self.place_properties_layout.addWidget(self.id_field)

        self.name_layout = QHBoxLayout()

        self.name_label = QLabel("Place name: ")
        # self.name_field.setPlaceholderText("Place name:")
        self.change_name_button = QPushButton("Change name")
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.change_name_button)
        self.change_name_button.clicked.connect(self.change_name)
        self.place_properties_layout.addLayout(self.name_layout)




        self.token_layout = QHBoxLayout()
        self.token_field = QSpinBox()
        self.token_field.setRange(0, 1000000)
        self.token_label = QLabel("Number of tokens:")
        # self.name_field.setPlaceholderText("Place name:")
        self.token_layout.addWidget(self.token_label)
        self.token_layout.addWidget(self.token_field)
        self.place_properties_layout.addLayout(self.token_layout)

        self.token_field.valueChanged.connect(self.update_token)

        #self.color_button = QPushButton("Select Color")
        #self.color_button.clicked.connect(self.choose_color)
        #self.place_properties_layout.addWidget(self.color_button)

        self.place_properties_section.setLayout(self.place_properties_layout)
        self.layout.addWidget(self.place_properties_section)
        self.place_properties_section.hide()  # Hidden by default

    def update_token(self, token):

        self.place.change_token_number(token)
        self.graphic_place.update()



    def update_properties(self, graphic_place):
        self.graphic_place=graphic_place
        self.place=graphic_place.place
        id = self.place.id
        name = self.place.name
        token = self.place.token_number
        """Update the panel to show properties of the selected object."""
        self.place_properties_section.show()

        # Example: Populate fields dynamically
        self.name_label.setText("Place name: {}".format(name))
        self.id_field.setText("Place ID: P.{}".format(id))
        self.token_field.setValue(token)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(f"Selected color: {color.name()}")  # Update your object's color here

    def change_name(self,name):
        """Open the dialog to edit an existing item."""

        dialog = ChangePlaceNameDialog(self.place.TOSPN,self.place)
        if dialog.exec_() == QDialog.Accepted:
            new_value = dialog.get_value()

            self.graphic_place.change_name(new_value)
            self.graphic_place.update()



class ChangePlaceNameDialog(QDialog):
    """Dialog for adding or editing an item."""
    def __init__(self, TOSPN, placeItem=None):
        super().__init__()
        self.TOSPN=TOSPN
        if placeItem==None:
            initial_value=""
        else:
            initial_value=placeItem.name
        self.setWindowTitle("Change Place name")
        self.setModal(True)
        self.initial_value=initial_value

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
        """Validation logic: Ensure the input is a positive number."""
        if (value not in self.TOSPN.placeNameDic.keys() or value==self.initial_value) and "OR" not in value and "AND" not in value and "(" not in value and ")" not in value and "FM" not in value and "FD" not in value and " "not in value and "and" not in value and "or" not in value:
            return True
        else:
            return False

    def get_value(self):
        """Return the input value."""
        return self.line_edit.text()


class TransitionPropertyEditor(QWidget):
    def __init__(self,TOSPN):
        super().__init__()
        self.TOSPN=TOSPN
        self.setFixedWidth(300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)


        # Properties section (hidden by default)
        self.transition_properties_section = QWidget()
        self.transition_properties_layout = QVBoxLayout(self.transition_properties_section)

        # Example fields (dynamic in a real app)

        self.id_field = QLabel("transition Object ID: ")
        self.transition_properties_layout.addWidget(self.id_field)

        self.name_layout = QHBoxLayout()
        self.name_field = QLineEdit()
        self.name_label = QLabel("transition name: ")
        # self.name_field.settransitionholderText("transition name:")
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_field)
        self.transition_properties_layout.addLayout(self.name_layout)

        self.name_field.textChanged.connect(self.update_name)

        self.event_layout = QHBoxLayout()


        self.event_combo_box = QComboBox()
        self.event_combo_box.addItem("{}".format(self.TOSPN.eventDic[0].name))
        self.event_combo_box.setItemData(0,self.TOSPN.eventDic[0])
        self.event_combo_box.currentIndexChanged.connect(self.update_event)


        # self.name_field.settransitionholderText("transition name:")
        self.event_label=QLabel("Event: ")
        self.event_layout.addWidget(self.event_label)
        self.event_layout.addWidget(self.event_combo_box)


        self.transition_properties_layout.addLayout(self.event_layout)



        self.clock_layout = QHBoxLayout()
        self.clock_field_1 = QDoubleSpinBox()
        self.clock_field_1.setMinimum(0.0)
        self.clock_field_1.setSingleStep(0.1)
        self.clock_field_1.setMaximum(10000000.0)
        self.clock_field_1.setDecimals(3)

        self.clock_field_2 = QDoubleSpinBox()
        self.clock_field_2.setMinimum(0.0)
        self.clock_field_2.setSingleStep(0.1)
        self.clock_field_2.setMaximum(10000000.0)
        self.clock_field_2.setDecimals(3)

        self.clock_label = QLabel("Number of clocks:")
        # self.name_field.settransitionholderText("transition name:")
        self.clock_layout.addWidget(self.clock_label)
        self.clock_layout.addWidget(self.clock_field_1)
        self.clock_layout.addWidget(self.clock_field_2)
        self.transition_properties_layout.addLayout(self.clock_layout)

        self.clock_field_1.valueChanged.connect(self.update_clock_1)
        self.clock_field_2.valueChanged.connect(self.update_clock_2)

        #self.color_button = QPushButton("Select Color")
        #self.color_button.clicked.connect(self.choose_color)
        #self.transition_properties_layout.addWidget(self.color_button)

        self.transition_properties_section.setLayout(self.transition_properties_layout)
        self.layout.addWidget(self.transition_properties_section)
        self.transition_properties_section.hide()  # Hidden by default


    def update_name(self,name):
        self.graphic_transition.change_name(name)
        self.graphic_transition.update()

    def update_event(self,index):
        event = self.event_combo_box.itemData(index)
        if event in self.TOSPN.eventDic.values():
            self.graphic_transition.change_event(event)
            self.graphic_transition.update()
            print("event_cahnged")

    def update_clock_1(self, clock_1):
        self.graphic_transition.change_clock_1(clock_1)
        self.graphic_transition.update()

    def update_clock_2(self, clock_2):
        self.graphic_transition.change_clock_2(clock_2)
        self.graphic_transition.update()



    def update_properties(self, graphic_transition):
        self.graphic_transition=graphic_transition
        self.transition=graphic_transition.transition
        id = self.transition.id
        name = self.transition.name
        event=self.transition.event
        clock_1 = self.transition.timing_interval[0]
        clock_2 = self.transition.timing_interval[1]
        """Update the panel to show properties of the selected object."""
        self.transition_properties_section.show()



        # Example: Populate fields dynamically
        self.name_field.setText(name)
        self.event_combo_box.clear()
        k=0
        found_event=False
        for event_id in self.TOSPN.eventDic.keys():
            self.event_combo_box.addItem("{}".format(self.TOSPN.eventDic[event_id].name))
            self.event_combo_box.setItemData(k, self.TOSPN.eventDic[event_id])
            if self.TOSPN.eventDic[event_id]==event:
                self.event_combo_box.setCurrentIndex(k)
                found_event = True
            k+=1
        if found_event==False:
            self.event_combo_box.setCurrentIndex(0)
            self.update_event(0)



        self.id_field.setText("transition ID: T.{}".format(id))
        self.clock_field_1.setValue(clock_1)
        self.clock_field_2.setValue(clock_2)


    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(f"Selected color: {color.name()}")  # Update your object's color here




class EventPropertyEditor(QWidget):
    def __init__(self,TOSPN):
        super().__init__()
        self.TOSPN=TOSPN
        self.setFixedWidth(300)
        # Main widget and layout
        self.layout = QVBoxLayout(self)


        self.event_label=QLabel("Event list:")

        # List widget
        self.list_widget = QListWidget()

        # Add button
        self.add_button = QPushButton("+ Add Item")

        self.layout.addWidget(self.event_label)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.list_widget)

        # Connect signals
        self.add_button.clicked.connect(self.add_item)


    def reset_self(self):
        self.layout.removeWidget(self.list_widget)
        self.list_widget.deleteLater()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def load_item(self,init_dic):
        eventItem = self.TOSPN.add_Event(None,init_dic)
        self.add_to_list(init_dic["name"], eventItem)

    def add_item(self):
        """Open the dialog to add a new item."""
        dialog = AddEventDialog(self.TOSPN)
        if dialog.exec_() == QDialog.Accepted:
            value = dialog.get_value()
            eventItem=self.TOSPN.add_Event(value)
            self.add_to_list(value, eventItem)

    def add_to_list(self, value, eventItem):
        """Add a new custom widget to the list."""
        item = QListWidgetItem(self.list_widget)

        # Create the custom widget
        widget = EventListItemWidget(value, eventItem)
        widget.remove_requested.connect(lambda:self.remove_item(item, widget))
        widget.edit_requested.connect(lambda:self.edit_item(item, widget))

        # Add a horizontal line (QFrame) between items
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        # line.setFixedWidth(100)

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
        # container.setFixedSize(200, 10)
        item.setSizeHint(container.sizeHint())  # Ensure proper sizing based on the custom widget's size hint

        self.list_widget.setItemWidget(item, container)
        # self.list_widget.update()

    def is_event_used(self,event):
        print(event.transition_dic)
        if event.transition_dic=={}:
            return False
        else:
            return True
    def remove_item(self, item,widget):
        """Remove an item from the list."""
        if self.is_event_used(widget.eventItem)==False:
            eventItem = widget.eventItem
            eventItem.remove()
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

    def edit_item(self, item, widget):
        """Open the dialog to edit an existing item."""
        eventItem=widget.eventItem
        dialog = AddEventDialog(widget.TOSPN,eventItem)
        if dialog.exec_() == QDialog.Accepted:
            new_value = dialog.get_value()
            widget.set_value(new_value)

class AddEventDialog(QDialog):
    """Dialog for adding or editing an item."""
    def __init__(self, TOSPN, eventItem=None):
        super().__init__()
        self.TOSPN=TOSPN
        if eventItem==None:
            initial_value=""
        else:
            initial_value=eventItem.name
        self.setWindowTitle("Edit Item" if initial_value else "Add New Item")
        self.setModal(True)
        self.initial_value=initial_value

        # Layout and Widgets
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Enter event name:")
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
        if (value not in self.TOSPN.event_name_list or value==self.initial_value) and value!="":
            if "?" not in str(value):
                return True
            else:
                return False
        else:
            return False

    def get_value(self):
        """Return the input value."""
        return self.line_edit.text()

class EventListItemWidget(QWidget):
    """Custom widget for a list item, with remove and edit capabilities."""
    remove_requested = Signal()  # Signal emitted when the remove button is clicked
    edit_requested = Signal()  # Signal emitted when the value is clicked

    def __init__(self, value, eventItem):
        super().__init__()
        self.TOSPN=eventItem.TOSPN
        self.eventItem = eventItem
        self.layout = QHBoxLayout(self)
        # Editable value field (read-only)
        self.value_label = QLabel(value)
        self.value_label.setWordWrap(True)  # Ensure text wraps
        self.value_label.setMaximumWidth(150)  # You can adjust the width here as needed

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
        self.eventItem.update_name(value)

    def sizeHint(self):
        """Override sizeHint to return the correct size based on QLabel content."""
        # Return the size hint based on the width of the label and the height of the content
        return self.value_label.sizeHint()



class OutputPropertyEditor(QWidget):
    def __init__(self,TOSPN):
        super().__init__()
        self.TOSPN=TOSPN
        self.setFixedWidth(300)
        self.widget_list=[]
        # Main widget and layout
        self.layout = QVBoxLayout(self)
        self.outputParser=OutputParser(self.TOSPN)

        self.output_label=QLabel("Output list:")

        # List widget
        self.list_widget = QListWidget()

        # Add button
        self.add_button = QPushButton("+ Add Item")

        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.list_widget)

        # Connect signals
        self.add_button.clicked.connect(self.add_item)

    def update_txt(self):
        self.outputParser.update_parsing_element()
        for widget in self.widget_list:
            widget.expression_label.setText(widget.outputItem.retrieve_marking_name_expression())

    def reset_self(self):
        self.layout.removeWidget(self.list_widget)
        self.list_widget.deleteLater()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def load_item(self, init_dic):
        eventItem = self.TOSPN.add_Output(None,None,None,init_dic)
        self.add_to_list(init_dic["name"], init_dic["txt_expression"] ,eventItem)

    def add_item(self):
        """Open the dialog to add a new item."""
        dialog = AddOutputDialog(self.TOSPN,self)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_txt_expression, new_txt_id_expression ,new_math_expression = dialog.get_value()
            print(new_txt_expression)
            print(new_txt_id_expression)
            print(new_math_expression)
            outputItem=self.TOSPN.add_Output(new_name,new_math_expression,new_txt_id_expression)
            self.add_to_list( new_name, new_txt_expression, outputItem)


    def add_to_list(self, new_name,new_expression, outputItem):
        """Add a new custom widget to the list."""
        item = QListWidgetItem(self.list_widget)

        container = QWidget()
        # Create the custom widget
        widget = OutputListItemWidget(new_name,new_expression, outputItem, container)
        widget.remove_requested.connect(lambda:self.remove_item(item, widget))
        widget.edit_requested.connect(lambda:self.edit_item(item, widget))

        # Add a horizontal line (QFrame) between items
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        # line.setFixedWidth(100)

        # Create a layout for the item and the separator line

        item_layout = QVBoxLayout(container)
        item_layout.setContentsMargins(0, 0, 0, 0)  # Left, Top, Right, Bottom margins
        item_layout.setSpacing(0)  # Spacing between items
        item_layout.addWidget(widget)  # Add the item widget
        item_layout.addWidget(line)  # Add a separator line

        # Set the layout for the item
        container.setLayout(item_layout)

        # Set the widget for the list item and ensure it takes the correct size hint
        # container.setFixedSize(200, 10)
          # Ensure proper sizing based on the custom widget's size hint
        self.list_widget.setItemWidget(item, container)
        item.setSizeHint(container.sizeHint())
        # self.list_widget.update()
        self.widget_list.append(widget)

    def remove_item(self, item,widget):
        """Remove an item from the list."""

        outputItem = widget.outputItem
        outputItem.remove()
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        self.widget_list.remove(widget)

    def edit_item(self, item, widget):
        """Open the dialog to edit an existing item."""
        outputItem=widget.outputItem
        dialog = AddOutputDialog(widget.TOSPN,self,widget)
        if dialog.exec_() == QDialog.Accepted:
            new_name, txt_expression, txt_id_expression, math_expression = dialog.get_value()
            widget.set_value(new_name, txt_expression, txt_id_expression,  math_expression)
            item.setSizeHint(widget.container.sizeHint())

class AddOutputDialog(QDialog):
    """Dialog for adding or editing an item."""
    def __init__(self, TOSPN, editor , widget=None):
        super().__init__()
        self.TOSPN=TOSPN
        if widget==None:
            initial_name=""
            initial_expression=""
        else:
            initial_name= widget.outputItem.name
            initial_expression = widget.outputItem.retrieve_marking_name_expression()
        self.editor=editor
        self.outputParser=self.editor.outputParser
        self.setWindowTitle("Edit Item" if initial_name else "Add New Item")
        self.setModal(True)
        self.initial_name=initial_name

        # Layout and Widgets
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Enter output name:")
        self.name_edit = QLineEdit(initial_name)
        self.exp_label = QLabel("Enter output expression:")
        self.expression_edit = QLineEdit(initial_expression)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.exp_label)
        self.layout.addWidget(self.expression_edit)

        self.layout.addWidget(self.buttons)

        # Disable the OK button initially if no initial value
        self.ok_button = self.buttons.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(bool(initial_name))

        # Connect signals
        self.name_edit.textChanged.connect(self.validate_input)
        self.expression_edit.textChanged.connect(self.validate_input)

        self.buttons.accepted.connect(self.accept)  # OK button closes the dialog
        self.buttons.rejected.connect(self.reject)  # Cancel button closes the dialog

    def validate_input(self):
        """Enable OK button only if the input is valid."""
        if self.validate_name(self.name_edit.text()) and self.validate_expression(self.expression_edit.text()):
            self.ok_button.setEnabled(True)

        else:
            self.ok_button.setEnabled(False)

    def validate_name(self, name):
        if (name not in self.TOSPN.output_name_list or name==self.initial_name) and name!="":
            if "?" not in str(name):
                return True
            else:
                return False
        else:
            return False

    def validate_expression(self,expression):
        """Validation logic: Ensure the input is a positive number."""
        if self.outputParser.check_validity(expression):
            return True
        else:
            return False


    def get_value(self):
        """Return the input value."""
        result = self.outputParser.tryParsing(self.expression_edit.text())
        print(result[1])
        math_expression =  self.outputParser.reformat_math_expression(result[1].asList())
        txt_expression = self.outputParser.reformat_txt(result[1].asList())
        txt_id_expression = self.outputParser.reformat_id_txt(result[1].asList())

        print("getvalue")
        print(math_expression)
        print(txt_expression)
        print(txt_id_expression)

        return self.name_edit.text(), txt_expression,txt_id_expression ,math_expression

class OutputListItemWidget(QWidget):
    """Custom widget for a list item, with remove and edit capabilities."""
    remove_requested = Signal()  # Signal emitted when the remove button is clicked
    edit_requested = Signal()  # Signal emitted when the value is clicked

    def __init__(self, new_name,new_expression, outputItem,container):
        super().__init__()
        self.container=container
        self.TOSPN=outputItem.TOSPN
        self.outputItem = outputItem
        self.layout = QHBoxLayout(self)
        # Editable value field (read-only)
        self.name_label = QLabel(new_name)
        self.name_label.setWordWrap(True)  # Ensure text wraps
        self.name_label.setMaximumWidth(150)  # You can adjust the width here as needed

        self.separator_label= QLabel(": ")
        self.separator_label.setWordWrap(True)
        self.separator_label.setMaximumWidth(15)

        self.expression_label = QLabel(new_expression)
        self.expression_label.setWordWrap(True)  # Ensure text wraps
        self.expression_label.setMaximumWidth(1000)  # You can adjust the width here as needed

        self.layout.addWidget(self.name_label)
        self.layout.setAlignment(self.name_label, Qt.AlignLeft)
        self.layout.addWidget(self.separator_label)
        self.layout.setAlignment(self.separator_label, Qt.AlignLeft)
        self.layout.addWidget(self.expression_label)
        self.layout.setAlignment(self.expression_label, Qt.AlignLeft)

        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addSpacerItem(self.spacer)

        self.layout.setContentsMargins(0, 0, 0, 0)  # Left, Top, Right, Bottom margins
        self.layout.setSpacing(0)

        # Remove button
        self.remove_button = QPushButton("-")
        self.remove_button.setFixedSize(50, 20)
        self.layout.addWidget(self.remove_button)

        # Connect signals
        self.name_label.mouseDoubleClickEvent = self.request_edit  # Double-click to request edit
        self.remove_button.clicked.connect(self.remove_requested.emit)

    def mousePressEvent(self, event):
        """Emit a signal to request editing if clicked on the widget."""
        self.edit_requested.emit()

    def request_edit(self, event):
        """Emit a signal to request editing."""
        self.edit_requested.emit()

    def set_value(self, new_name, txt_expression, txt_id_expression, math_expression):
        """Set the displayed value."""
        self.name_label.setText(new_name)
        self.outputItem.update_name(new_name)
        self.expression_label.setText(txt_expression)
        self.outputItem.update_expression(math_expression,txt_id_expression)
        self.update()
        self.container.update()


    '''
    def sizeHint(self):
        """Override sizeHint to return the correct size based on QLabel content."""
        # Return the size hint based on the width of the label and the height of the content
        return self.expression_label.sizeHint()
    '''
