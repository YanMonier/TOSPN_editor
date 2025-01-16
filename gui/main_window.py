from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow
from PySide2.QtCore import QRectF, Qt, QPointF, QPoint
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
import sys
from gui.widgets.widgets import DraggableItem,DraggablePoint, LineBetweenPoints
from gui.dialogs import MessageDialog, CustomDialog

from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QInputDialog,QSplitter, QHBoxLayout
from PySide2.QtCore import Qt

from gui.graphics.graphics_scene import GraphConstructionScene
from gui.widgets.property_editor import PlacePropertyEditor, TransitionPropertyEditor, EventPropertyEditor, OutputPropertyEditor




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
        self.state="none"

        # Set up the main window
        self.setWindowTitle("PySide2 Application")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set a basic layout for the central widget
        self.layoutV = QVBoxLayout()
        self.layoutH1 = QHBoxLayout()

        self.H1=QWidget()
        self.H1.setLayout(self.layoutH1)

        self.central_widget.setLayout(self.layoutV)
        self.layoutV.addWidget(self.H1)


        # Create a QGraphicsView and QGraphicsScene
        self.scene = GraphConstructionScene(self)
        self.scene.state="none"
        self.scene.setSceneRect(-10000, -10000, 20000, 20000)  # Set scene boundaries


        # Create a QGraphicsView
        self.graphics_view = GraphicsView(self.scene, self)

        # Align the scene's (0, 0) to the top-left of the view
        self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Optional: Disable scrollbars
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add the QGraphicsView to the layout
        self.layoutH1.addWidget(self.graphics_view)


        # Add a label as a placeholder
        #label = QLabel("Welcome to PySide2 Application!", self)
        #label.setStyleSheet("font-size: 18px;")
        #self.layoutV.addWidget(label)


        # Create two draggable points
        #point1 = DraggablePoint(100, 100)
        #point2 = DraggablePoint(400, 300)

        # Create a line between the two points
        #line = LineBetweenPoints(point1, point2)

        # Add the points and the line to the scene
        #self.scene.addItem(point1)
        #self.scene.addItem(point2)
        #self.scene.addItem(line)


        # Optional: Set up a status bar
        self.statusBar().showMessage("Ready")
        self.setup_menus()
        self.setup_toolbar()

        # Create the property editor


        self.splitter = QSplitter(Qt.Horizontal)
        self.current_property_editor=None
        self.place_property_editor = PlacePropertyEditor()
        self.transition_property_editor=TransitionPropertyEditor(self.scene.TOSPN)

        self.event_property_editor=EventPropertyEditor(self.scene.TOSPN)
        self.output_property_editor=OutputPropertyEditor(self.scene.TOSPN)


        #self.splitter.addWidget(self.place_property_editor)
        self.layoutH1.addWidget(self.splitter)






        ################TEST
        """
        # Initialize dialogs
        self.message_dialog = MessageDialog(self)
        self.custom_dialog = CustomDialog()

        # Button to show message box
        self.button = QPushButton("Show Info Dialog", self)
        self.button.clicked.connect(self.message_dialog.show_message_dialog)
        self.button.setGeometry(100, 50, 200, 50)
        self.layoutV.addWidget(self.button)

        # Button to open file dialog
        self.button_open_file = QPushButton("Open File", self)
        self.button_open_file.clicked.connect(self.message_dialog.open_file_dialog)
        self.button_open_file.setGeometry(100, 150, 200, 50)
        self.layoutV.addWidget(self.button_open_file)

        # Button to show input dialog
        self.button_input = QPushButton("Enter Your Name", self)
        self.button_input.clicked.connect(self.message_dialog.show_input_dialog)
        self.button_input.setGeometry(100, 250, 200, 50)
        self.layoutV.addWidget(self.button_input)

        # Button to show custom dialog
        self.button_custom_dialog = QPushButton("Custom Dialog", self)
        self.button_custom_dialog.clicked.connect(self.custom_dialog.exec_)
        self.button_custom_dialog.setGeometry(100, 350, 200, 50)
        self.layoutV.addWidget(self.button_custom_dialog)
        """
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
        file_menu.addSeparator()  # Add a separator
        file_menu.addAction(exit_action)

        '''
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")

        # Create actions for the Edit menu
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)

        # Add actions to the Edit menu
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        '''
        # Help Menu
        help_menu = menubar.addMenu("Help")

        # Create an action for the Help menu
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)

        # Add the action to the Help menu
        help_menu.addAction(about_action)

    # Action Handlers
    def new_file(self):
        self.scene.graphManager.empty_self()
        QMessageBox.information(self, "New File", "Create a new file!")

    def open_file(self):
        # Open a file dialog to select save location
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",  # Dialog title
            "",  # Initial directory ("" for current directory)
            "JSON Files (*.json);;All Files (*)"  # File type filters
        )
        if file_path:  # Check if the user selected a file
            self.scene.graphManager.load(file_path)
            print(f"File loaded from: {file_path}")
            QMessageBox.information(self, "Save File", "Save the current file!")


    def save_file(self):
        # Open a file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",  # Dialog title
            "",  # Initial directory ("" for current directory)
            "JSON Files (*.json);;All Files (*)"  # File type filters
        )
        if file_path:  # Check if the user selected a file
            self.scene.graphManager.save(file_path)
            print(f"File saved to: {file_path}")
            QMessageBox.information(self, "Save File", "Save the current file!")

    def show_about(self):
        QMessageBox.about(self, "About", "This editor was developed with funding from the ANR project MENACE.")

    # Placeholder for creating a toolbar
    def setup_toolbar(self):
        # Create a toolbar
        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)  # Add the toolbar to the main window

        # Create actions for the toolbar
        self.move_action = QAction(QIcon(), "move", self)  # Replace QIcon() with a valid icon file
        self.move_action.setShortcut("Ctrl+m")
        self.move_action.setCheckable(True)
        self.move_action.triggered.connect(self.update_state)

        self.add_place_action = QAction(QIcon(), "add place", self)  # Replace QIcon() with a valid icon file
        self.add_place_action.setShortcut("Ctrl+p")
        self.add_place_action.setCheckable(True)
        self.add_place_action.triggered.connect(self.update_state)

        self.add_transition_action = QAction(QIcon(), "add transition", self)  # Replace QIcon() with a valid icon file
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

        # Add actions to the toolbar
        toolbar.addAction(self.move_action)
        toolbar.addAction(self.add_place_action)
        toolbar.addAction(self.add_transition_action)

        #toolbar.addSeparator()  # Add a separator
        toolbar.addAction(self.add_arc_action)
        toolbar.addAction(self.add_event_action)
        toolbar.addAction(self.add_output_action)



        # Customize the toolbar
        toolbar.setMovable(True)  # Allow the toolbar to be moved
        toolbar.setFloatable(True)  # Allow the toolbar to float
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # Show text under icons
        self.toggle_action_list=[self.add_arc_action,self.add_transition_action,self.add_place_action,self.move_action,self.add_event_action,self.add_output_action]


    def toggle_action(self, checked):
        if checked:
            print("Action is ON")
        else:
            print("Action is OFF")

    def update_state(self, checked):
        """Update the label based on the toggle button's state."""
        sender=self.sender()
        #print(sender)
        if checked:
            if self.scene.state=="add_event":
                index = self.splitter.indexOf(self.event_property_editor)
                self.splitter.replaceWidget(index, None)
                self.event_property_editor.setParent(None)

            for action in self.toggle_action_list:
                if action != sender:
                    action.setChecked(0)
            if sender == self.move_action:
                self.scene.state="move"
                self.scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_place_action:
                self.scene.state="add_place"
                self.scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_transition_action:
                self.scene.state="add_transition"
                self.scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_arc_action:
                self.scene.state="add_arc"
                self.scene.empty_selected()
                self.set_property_editor(None)
            elif sender == self.add_event_action:
                self.scene.state = "add_event"
                self.scene.empty_selected()
                self.set_property_editor("event")

            elif sender == self.add_output_action:
                self.scene.state = "add_output"
                self.scene.empty_selected()
                self.set_property_editor("output")
        else:
            self.scene.state="None"

    def set_property_editor(self,value):

        if self.current_property_editor != None:
            index = self.splitter.indexOf(self.current_property_editor)
            self.splitter.replaceWidget(index, None)
            self.current_property_editor.setParent(None)


        if value=="transition":
            self.splitter.addWidget(self.transition_property_editor)
            self.current_property_editor=self.transition_property_editor
        elif value=="place":
            self.splitter.addWidget(self.place_property_editor)
            self.current_property_editor = self.place_property_editor
        elif value=="event":
            self.splitter.addWidget(self.event_property_editor)
            self.current_property_editor = self.event_property_editor
        elif value=="output":
            self.splitter.addWidget(self.output_property_editor)
            self.current_property_editor = self.output_property_editor
            self.output_property_editor.update_txt()
        else:
            self.current_property_editor = None

