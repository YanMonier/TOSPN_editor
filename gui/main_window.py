import json


from PySide2.QtWidgets import QTabWidget, QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QSplitter, QHBoxLayout, QActionGroup, QDialogButtonBox
from PySide2.QtCore import QRectF, Qt, QPointF, QPoint
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
import sys
from gui.widgets.widgets import DraggableItem,DraggablePoint, LineBetweenPoints
from gui.dialogs import MessageDialog, CustomDialog

from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QInputDialog
from PySide2.QtCore import Qt

from gui.graphics.graphics_scene import GraphConstructionScene

from gui.widgets.property_editor.PlacePropertyEditor import PlacePropertyEditor
from gui.widgets.property_editor.TransitionPropertyEditor import TransitionPropertyEditor
from gui.widgets.property_editor.EventPropertyEditor import EventPropertyEditor
from gui.widgets.property_editor.OutputPropertyEditor import OutputPropertyEditor
from gui.widgets.property_editor.OutputPropertyEditorTLSPN import OutputPropertyEditorTLSPN

from gui.tabs.edit_TLSPN_tab import edit_model_tab
from core.model.SCG.scg import SCG
from core.model.SCIA.scia import SCIA
from core.model.SCIA.scia_observer import SCIA_observer

import os


class NewFileDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New File")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Choose what to create:"))

        # Create buttons for different file types
        self.buttons = {
            "TOSPN": QPushButton("New TOSPN"),
            "TLSPN": QPushButton("New TLSPN"),
        }

        for btn in self.buttons.values():
            layout.addWidget(btn)

        # Add Cancel button
        cancel_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        cancel_box.rejected.connect(self.reject)
        layout.addWidget(cancel_box)

        # Variable to store choice
        self.choice = None

        # Connect each button to select and accept
        for name, btn in self.buttons.items():
            btn.clicked.connect(lambda *_ , n=name: self.select_option(n))

    def select_option(self, name):
        self.choice = name
        self.accept()  # Close the dialog and return success


class MyTabs(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def add_new_tab(self, name):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"This is {name}"))
        tab.setLayout(layout)
        self.addTab(tab, name)

    def close_tab(self, index):
        # Ask if user wants to save
        response = QMessageBox.question(
            self,
            "Save changes?",
            "Do you want to save changes before closing this tab?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        if response == QMessageBox.Yes:
            print("Saving...")  # Your save logic here
            if self.currentWidget().tab_type=="TLSPN_edit_tab":
                result = self.currentWidget().save_file()
            if result == "saved":
                self.removeTab(index)
            else:
                pass
        elif response == QMessageBox.No:
            self.removeTab(index)
        else:
            # Cancelled — do nothing
            pass

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene,parent)
        self.mainw=parent
        self.setMouseTracking(True)
        self._is_panning = False
        self._pan_start = QPoint()
        #self.setRenderHint(QPainter.Antialiasing)
        self.zoom_level = 0  # Track zoom level
        self.zoom_step = 0.1  # Scaling factor per wheel step
        self.min_zoom = -10  # Minimum zoom level (zoom out)
        self.max_zoom = 10  # Maximum zoom level (zoom in)


    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:  # Pan with middle mouse button
            self._is_panning = True
            self._pan_start = event.pos()  # Save the starting position
            self.setCursor(Qt.ClosedHandCursor)  # Change cursor to indicate panning
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            # Calculate the difference between current and starting positions
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            # Adjust the scrollbars to pan the view
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:  # Stop panning
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)  # Restore the default cursor
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # Determine the zoom direction
        if event.angleDelta().y() > 0:  # Zoom in
            if self.zoom_level < self.max_zoom:
                self.zoom_level += 1
                self.scale(1 + self.zoom_step, 1 + self.zoom_step)
        else:  # Zoom out
            if self.zoom_level > self.min_zoom:
                self.zoom_level -= 1
                self.scale(1 - self.zoom_step, 1 - self.zoom_step)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabs=QTabWidget()

        self.state = "none"
        self.current_scene_type = "edit"  # Track which scene is active

        # Set up the main window
        self.setWindowTitle("TOSPN Editor")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        self.central_widget = MyTabs()
        self.setCentralWidget(self.central_widget)
        self.tabs=[]
        #self.page1 = QWidget()
        #self.page2 = QWidget()
        #self.page3 = QWidget()
        self.tabs.append(edit_model_tab(self))
        #self.central_widget.addTab(self.page1, "Edit Mode")
        #self.central_widget.addTab(self.page2, "Class graph Mode")
        #self.central_widget.addTab(self.page3, "Simulation Mode")
        self.central_widget.addTab( self.tabs[-1], "Edit test")

        # Create scenes
        self.edit_scene = GraphConstructionScene(self)
        self.edit_scene.state = "none"
        self.edit_scene.setSceneRect(-10000, -10000, 20000, 20000)

        self.simulation_scene = QGraphicsScene(self)  # Empty scene for now
        self.simulation_scene.setSceneRect(-10000, -10000, 20000, 20000)

        self.simulation_graphics_view = GraphicsView(self.simulation_scene, self)
        self.simulation_graphics_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.simulation_graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.simulation_graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create a QGraphicsView
        self.graphics_view = GraphicsView(self.edit_scene, self)  # Start with edit scene
        self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create the property editor
        self.splitter = QSplitter(Qt.Horizontal)
        self.current_property_editor = None
        self.place_property_editor = PlacePropertyEditor()
        self.transition_property_editor = TransitionPropertyEditor()
        self.event_property_editor = EventPropertyEditor()
        self.output_property_editor = OutputPropertyEditor()

        # Connect property editors to TOSPN model
        self.event_property_editor.set_TOSPN(self.edit_scene.TOSPN)
        self.output_property_editor.set_TOSPN(self.edit_scene.TOSPN)

        # Create simulation mode widgets
        self.simulation_left_panel = QWidget()
        self.simulation_left_panel.setMinimumWidth(200)  # Set minimum width
        self.simulation_left_panel.setMaximumWidth(300)  # Set maximum width
        self.simulation_left_panel.setStyleSheet("background-color: lightgray;")  # Temporary visible style
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Simulation Controls"))
        self.simulation_left_panel.setLayout(left_layout)

        self.simulation_bottom_panel = QWidget()
        self.simulation_bottom_panel.setMinimumHeight(100)  # Set minimum height
        self.simulation_bottom_panel.setMaximumHeight(150)  # Set maximum height
        self.simulation_bottom_panel.setStyleSheet("background-color: lightblue;")  # Temporary visible style
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("Simulation Status"))
        self.simulation_bottom_panel.setLayout(bottom_layout)

        # Create persistent layouts
        # Edit mode layout
        self.edit_layout = QHBoxLayout()
        self.edit_layout.addWidget(self.graphics_view)
        self.edit_layout.addWidget(self.splitter)

        # Simulation mode layout
        self.simulation_layout = QVBoxLayout()
        
        # Create horizontal layout for top section
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.simulation_left_panel, 1)  # 1 part for left panel
        top_layout.addWidget(self.simulation_graphics_view, 4)  # 4 parts for graphics view
        
        # Create a widget to hold the top layout
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        
        # Add widgets to main simulation layout with stretch
        self.simulation_layout.addWidget(top_widget, 5)  # Top section takes 5 parts
        self.simulation_layout.addWidget(self.simulation_bottom_panel, 2)  # Bottom panel takes 2 parts

        # Create container widget for simulation layout
        self.simulation_widget = QWidget()
        self.simulation_widget.setLayout(self.simulation_layout)

        # Create container widget for edit layout
        self.edit_widget = QWidget()
        self.edit_widget.setLayout(self.edit_layout)

        # Create main layout for central widget
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.edit_widget)  # Start with edit widget
        #self.page1.setLayout(self.main_layout)

        # Set up menus and toolbars
        self.statusBar().showMessage("Ready")
        self.setup_menus()
        #self.setup_toolbar()

    def setup_edit_layout(self):
        """Switch to edit mode layout."""
        self.simulation_widget.hide()
        self.edit_widget.show()
        self.main_layout.removeWidget(self.simulation_widget)
        self.main_layout.addWidget(self.edit_widget)

    def setup_simulation_layout(self):
        """Switch to simulation mode layout."""
        self.edit_widget.hide()
        self.simulation_widget.show()
        self.main_layout.removeWidget(self.edit_widget)
        self.main_layout.addWidget(self.simulation_widget)

    def switch_to_edit_scene(self):
        """Switch to the edit scene."""
        if self.current_scene_type != "edit":
            self.current_scene_type = "edit"
            self.toolbar.show()
            self.move_action.setEnabled(True)
            self.add_place_action.setEnabled(True)
            self.add_transition_action.setEnabled(True)
            self.add_arc_action.setEnabled(True)
            self.add_event_action.setEnabled(True)
            self.add_output_action.setEnabled(True)
            self.setup_edit_layout()
            self.statusBar().showMessage("Edit Mode")

    def switch_to_simulation_scene(self):
        """Switch to the simulation scene."""
        if self.current_scene_type != "simulation":
            self.current_scene_type = "simulation"
            self.toolbar.hide()
            self.move_action.setEnabled(False)
            self.add_place_action.setEnabled(False)
            self.add_transition_action.setEnabled(False)
            self.add_arc_action.setEnabled(False)
            self.add_event_action.setEnabled(False)
            self.add_output_action.setEnabled(False)
            self.setup_simulation_layout()
            self.statusBar().showMessage("Simulation Mode")

    def setup_toolbar(self):
        # Create a toolbar
        self.toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(self.toolbar)

        # Create editing actions
        self.move_action = QAction(QIcon(), "move", self)
        self.move_action.setShortcut("Ctrl+m")
        self.move_action.setCheckable(True)
        self.move_action.triggered.connect(self.update_state)

        self.add_place_action = QAction(QIcon(), "add place", self)
        self.add_place_action.setShortcut("Ctrl+p")
        self.add_place_action.setCheckable(True)
        self.add_place_action.triggered.connect(self.update_state)

        self.add_transition_action = QAction(QIcon(), "add transition", self)
        self.add_transition_action.setShortcut("Ctrl+t")
        self.add_transition_action.setCheckable(True)
        self.add_transition_action.triggered.connect(self.update_state)

        self.add_arc_action = QAction(QIcon(), "add arc", self)
        self.add_arc_action.setShortcut("Ctrl+a")
        self.add_arc_action.setCheckable(True)
        self.add_arc_action.triggered.connect(self.update_state)

        self.add_event_action = QAction(QIcon(), "add event", self)
        self.add_event_action.setShortcut("Ctrl+e")
        self.add_event_action.setCheckable(True)
        self.add_event_action.triggered.connect(self.update_state)

        self.add_output_action = QAction(QIcon(), "add output", self)
        self.add_output_action.setShortcut("Ctrl+o")
        self.add_output_action.setCheckable(True)
        self.add_output_action.triggered.connect(self.update_state)

        # Add editing actions to toolbar
        self.toolbar.addAction(self.move_action)
        self.toolbar.addAction(self.add_place_action)
        self.toolbar.addAction(self.add_transition_action)
        self.toolbar.addAction(self.add_arc_action)
        self.toolbar.addAction(self.add_event_action)
        self.toolbar.addAction(self.add_output_action)

        # Customize the toolbar
        self.toolbar.setMovable(True)
        self.toolbar.setFloatable(True)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.toggle_action_list = [
            self.add_arc_action,
            self.add_transition_action,
            self.add_place_action,
            self.move_action,
            self.add_event_action,
            self.add_output_action
        ]

    def update_state(self, checked):
        """Update the label based on the toggle button's state."""
        sender=self.sender()
        #print(sender)
        if checked:
            if self.edit_scene.state=="add_event":
                index = self.splitter.indexOf(self.event_property_editor)
                self.splitter.replaceWidget(index, None)
                self.event_property_editor.setParent(None)

            for action in self.toggle_action_list:
                if action != sender:
                    action.setChecked(0)
            if sender == self.move_action:
                self.edit_scene.state="move"
                self.edit_scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_place_action:
                self.edit_scene.state="add_place"
                self.edit_scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_transition_action:
                self.edit_scene.state="add_transition"
                self.edit_scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_arc_action:
                self.edit_scene.state="add_arc"
                self.edit_scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_event_action:
                self.edit_scene.state = "add_event"
                self.edit_scene.empty_selected()
                self.set_property_editor("event")

            elif sender == self.add_output_action:
                self.edit_scene.state = "add_output"
                self.edit_scene.empty_selected()
                self.set_property_editor("output")
        else:
            self.edit_scene.state="None"

    def set_property_editor(self, value):
        # First remove the current editor if it exists
        if self.current_property_editor is not None:
            #self.splitter.widget(self.splitter.indexOf(self.current_property_editor)).hide()
            self.current_property_editor.setParent(None)
            self.current_property_editor = None

        # Then add the new editor based on value
        if value == "transition":
            self.splitter.addWidget(self.transition_property_editor)
            self.current_property_editor = self.transition_property_editor
        elif value == "place":
            self.splitter.addWidget(self.place_property_editor)
            self.current_property_editor = self.place_property_editor
        elif value == "event":
            self.splitter.addWidget(self.event_property_editor)
            self.current_property_editor = self.event_property_editor
        elif value == "output":
            self.splitter.addWidget(self.output_property_editor)
            self.current_property_editor = self.output_property_editor
            #self.output_property_editor.update_txt()

        # Show the new editor if one was added
        if self.current_property_editor is not None:
            self.current_property_editor.show()

    def resizeEvent(self, event):
        # Adjust the scene rectangle to match the size of the QGraphicsView
        view_width = self.graphics_view.width()
        view_height = self.graphics_view.height()
        # Update the scene rect to match the size of the view
        #self.scene.setSceneRect(0, 0, view_width, view_height)
        # Call the base class resizeEvent to ensure proper handling
        super().resizeEvent(event)
        # Optional: Add menu and toolbar here if needed (future extensions)


    # Placeholder for creating menus
    def setup_menus(self):
        # Get the menu bar
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        # Create actions for the File menu
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        # Add actions to the File menu
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        """# Mode Menu
        mode_menu = menubar.addMenu("Mode")
        # Create mode switching actions
        self.edit_mode_action = QAction("Edit Mode", self)
        self.edit_mode_action.setCheckable(True)
        self.edit_mode_action.setChecked(True)  # Start in edit mode
        self.edit_mode_action.triggered.connect(self.switch_to_edit_scene)

        self.simulation_mode_action = QAction("Simulation Mode", self)
        self.simulation_mode_action.setCheckable(True)
        self.simulation_mode_action.triggered.connect(self.switch_to_simulation_scene)



        # Create action group for mode switching
        mode_group = QActionGroup(self)
        mode_group.addAction(self.edit_mode_action)
        mode_group.addAction(self.simulation_mode_action)
        mode_group.setExclusive(True)

        # Add mode switching actions to Mode menu
        mode_menu.addAction(self.edit_mode_action)
        mode_menu.addAction(self.simulation_mode_action)"""

        # oppmenu
        opp_menu = menubar.addMenu("Opperation")
        # Create mode switching actions
        construct_graph = QAction("Construct Graph", self)
        construct_graph.triggered.connect(self.construct_classgraph)
        opp_menu.addAction(construct_graph)

        construct_scia = QAction("Construct SCIA", self)
        construct_scia.triggered.connect(self.construct_SCIA)
        opp_menu.addAction(construct_scia)

        construct_scia_observer = QAction("Construct SCIA_observer", self)
        construct_scia_observer.triggered.connect(self.construct_SCIA_observer)
        opp_menu.addAction(construct_scia_observer)


        # Help Menu
        help_menu = menubar.addMenu("Help")

        # Create an action for the Help menu
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)

        # Add the action to the Help menu
        help_menu.addAction(about_action)

    def construct_classgraph(self):
        current_tab = self.central_widget.currentWidget()
        if current_tab.tab_type == "TLSPN_edit_tab":
            TLSPN=current_tab.TLSPN
            if TLSPN != None:
                scg=SCG(TLSPN)
                print(scg.edge_list,scg.state_hash_dic)
                print("edge number",len(scg.edge_list))
                print("state number",len(list(scg.state_hash_dic.keys())))
                scg.plot_graph()

    def construct_SCIA(self):
        current_tab = self.central_widget.currentWidget()
        if current_tab.tab_type == "TLSPN_edit_tab":
            TLSPN=current_tab.TLSPN
            if TLSPN != None:
                scg=SCG(TLSPN)
                scia=SCIA(scg,1)
                scia.plot_graph()

    def construct_SCIA_observer(self):
        current_tab = self.central_widget.currentWidget()

        if current_tab != None:
            if current_tab.tab_type == "TLSPN_edit_tab":
                TLSPN=current_tab.TLSPN
                if TLSPN != None:
                    scg=SCG(TLSPN)
                    scia=SCIA(scg,1)
                    scia_observer=SCIA_observer(scia)
                    scia_observer.plot_graph()
            return(scia_observer)
        else:
            return(None)

    # Action Handlers
    def new_file(self):

        dialog = NewFileDialog()
        if dialog.exec_() == QDialog.Accepted:
            file_type = dialog.choice

            if dialog.choice == "TLSPN":
                self.tabs.append(edit_model_tab(self))
                self.central_widget.addTab(self.tabs[-1], "Edit TLSPN")
                self.central_widget.setCurrentWidget(self.tabs[-1])

        #self.edit_scene.graphManager.empty_self()
        #QMessageBox.information(self, "New File", "Create a new file!")

    def open_file(self):
        # Open a file dialog to select save location

        directory = "saves"
        if not os.path.exists(directory):
            os.makedirs(directory)


        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",  # Dialog title
             directory ,  # Initial directory ("" for current directory)
            "JSON Files (*.json);;All Files (*)"  # File type filters
        )
        if file_path:  # Check if the user selected a file
            file_type=None
            with open(file_path, 'r') as json_file:
                save_dic = json.load(json_file)
                file_type=save_dic["file_type"]

                if file_type == "TLSPN_edit_tab":
                    self.tabs.append(edit_model_tab(self))
                    self.central_widget.addTab(self.tabs[-1], "Edit TLSPN")
                    self.central_widget.setCurrentWidget(self.tabs[-1])
                    self.tabs[-1].load(file_path)

                    print(f"File loaded from: {file_path}")
                    QMessageBox.information(self, "Load File", "The file has been successfully loaded !")

            print("debug: try open")

    def save_file(self):
        # Open a file dialog to select save location

        current_tab = self.central_widget.currentWidget()
        if current_tab.tab_type=="TLSPN_edit_tab":
            current_tab.save_file()

    def show_about(self):
        QMessageBox.about(self, "About", "This editor was developed with funding from the ANR project MENACE. \nRef: ANR-22-CE10-0002\n\nAuthor: Yan Monier")


