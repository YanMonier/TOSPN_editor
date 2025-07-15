import json
from PySide2.QtWidgets import QTabWidget, QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QSplitter, QHBoxLayout, QActionGroup
from PySide2.QtCore import QRectF, Qt, QPointF, QPoint
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
import sys

from gui.widgets.property_editor.ArcPropertyEditorTLSPN import ArcPropertyEditorTLSPN
from gui.widgets.widgets import DraggableItem,DraggablePoint, LineBetweenPoints
from gui.dialogs import MessageDialog, CustomDialog
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QInputDialog

from gui.graphics.graphics_scene_TLSPN import GraphConstructionScene
from gui.widgets.property_editor.PlacePropertyEditorTLSPN  import PlacePropertyEditorTLSPN
from gui.widgets.property_editor.TransitionPropertyEditorTLSPN import TransitionPropertyEditorTLSPN
from gui.widgets.property_editor.EventPropertyEditorTLSPN  import EventPropertyEditorTLSPN
from gui.widgets.property_editor.OutputPropertyEditorTLSPN  import OutputPropertyEditorTLSPN
from gui.widgets.property_editor.SimulationPropertyEditorTLSPN  import SimulationPropertyEditorTLSPN
from gui.widgets.property_editor.AttackDetectionPropertyEditorTLSPN import AttackDetectionPropertyEditorTLSPN

from gui.widgets.property_editor.ArcPropertyEditorTLSPN  import ArcPropertyEditorTLSPN

from core.model.TLSPN.tlspn import TLSPN
import os

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



class edit_model_tab(QWidget):
	def __init__(self,MainWindow):
		super().__init__()
		self.MainWindow=MainWindow
		self.tab_type="TLSPN_edit_tab"
		self.TLSPN=None

		self.edit_scene = GraphConstructionScene(self)
		self.edit_scene.state = "none"
		self.edit_scene.setSceneRect(-10000, -10000, 20000, 20000)

		# Create a QGraphicsView
		self.graphics_view = GraphicsView(self.edit_scene, self)  # Start with edit scene
		self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		# Create the property editor
		self.splitter = QSplitter(Qt.Horizontal)
		self.current_property_editor = None
		self.place_property_editor = PlacePropertyEditorTLSPN ()
		self.transition_property_editor = TransitionPropertyEditorTLSPN ()
		self.event_property_editor = EventPropertyEditorTLSPN ()
		self.output_property_editor = OutputPropertyEditorTLSPN ()
		self.simulation_property_editor = SimulationPropertyEditorTLSPN()
		self.attack_detection_property_editor = AttackDetectionPropertyEditorTLSPN(self.MainWindow)
		self.arc_property_editor= ArcPropertyEditorTLSPN()


		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		# Add toolbar
		self.toolbar = QToolBar("Main Toolbar", self)

		self.layout.addWidget(self.toolbar)

		self.edit_layout = QHBoxLayout()
		self.edit_layout.addWidget(self.graphics_view)
		self.edit_layout.addWidget(self.splitter)

		self.layout.addLayout(self.edit_layout)


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

		self.simulation_action = QAction(QIcon(), "simulation", self)
		self.simulation_action.setShortcut("Ctrl+w")
		self.simulation_action.setCheckable(True)
		self.simulation_action.triggered.connect(self.update_state)

		self.attack_detection_action = QAction(QIcon(), "attack detection", self)
		self.attack_detection_action.setShortcut("Ctrl+t")
		self.attack_detection_action.setCheckable(True)
		self.attack_detection_action.triggered.connect(self.update_state)

		# Add editing actions to toolbar
		self.toolbar.addAction(self.move_action)
		self.toolbar.addAction(self.add_place_action)
		self.toolbar.addAction(self.add_transition_action)
		self.toolbar.addAction(self.add_arc_action)
		self.toolbar.addAction(self.add_event_action)
		self.toolbar.addAction(self.add_output_action)
		self.toolbar.addAction(self.simulation_action)
		self.toolbar.addAction(self.attack_detection_action)

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
			self.add_output_action,
			self.simulation_action,
			self.attack_detection_action
		]

		self.set_model(TLSPN())

	def update_state(self, checked):
		"""Update the label based on the toggle button's state."""
		sender = self.sender()
		# print(sender)
		if checked:
			if self.TLSPN!=None:
				self.TLSPN.reset_simulation()
			if self.edit_scene.state == "add_event":
				index = self.splitter.indexOf(self.event_property_editor)
				self.splitter.replaceWidget(index, None)
				self.event_property_editor.setParent(None)

			for action in self.toggle_action_list:
				if action != sender:
					action.setChecked(0)
			if sender == self.move_action:
				self.edit_scene.state = "move"
				self.edit_scene.empty_selected()
				self.set_property_editor(None)
			elif sender == self.add_place_action:
				self.edit_scene.state = "add_place"
				self.edit_scene.empty_selected()
				self.set_property_editor(None)
			elif sender == self.add_transition_action:
				self.edit_scene.state = "add_transition"
				self.edit_scene.empty_selected()
				self.set_property_editor(None)
			elif sender == self.add_arc_action:
				self.edit_scene.state = "add_arc"
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

			elif sender == self.simulation_action:
				self.edit_scene.state = "simulation"
				self.edit_scene.empty_selected()
				self.set_property_editor("simulation")

			elif sender == self.attack_detection_action:
				self.edit_scene.state = "attack_detection"
				self.edit_scene.empty_selected()
				self.set_property_editor("attack_detection")

			if self.edit_scene.state != "simulation":
				for gtransition in self.edit_scene.graphManager.transition_to_graph_transition.values():
					gtransition.unselected()
		else:
			self.edit_scene.state = "None"

	def set_property_editor(self, value):
		# First remove the current editor if it exists
		if self.current_property_editor is not None:
			# self.splitter.widget(self.splitter.indexOf(self.current_property_editor)).hide()
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
		elif value == "simulation":
			self.splitter.addWidget(self.simulation_property_editor)
			self.current_property_editor = self.simulation_property_editor
			self.simulation_property_editor.reset_simulation()
		elif value == "attack_detection":
			self.splitter.addWidget(self.attack_detection_property_editor)
			self.current_property_editor = self.attack_detection_property_editor
			self.attack_detection_property_editor.reset_attack_detection()
		elif value == "arc":
			self.splitter.addWidget(self.arc_property_editor)
			self.current_property_editor = self.arc_property_editor
		# self.output_property_editor.update_txt()

		# Show the new editor if one was added
		if self.current_property_editor is not None:
			self.current_property_editor.show()

	def set_model(self,TLSPN):
		# Connect property editors to TOSPN model
		self.event_property_editor.set_TLSPN(TLSPN)
		self.output_property_editor.set_TLSPN(TLSPN)
		self.simulation_property_editor.set_TLSPN(TLSPN)
		self.attack_detection_property_editor.set_TLSPN(TLSPN)
		self.TLSPN=TLSPN
		self.edit_scene.set_model(TLSPN)

	def save_file(self):
		# Open a file dialog to select save location

		directory = "saves"
		if not os.path.exists(directory):
			os.makedirs(directory)
		file_path, _ = QFileDialog.getSaveFileName(
			self,
			"Save File",  # Dialog title
			directory,  # Initial directory ("" for current directory)
			"JSON Files (*.json);;All Files (*)"  # File type filters
		)
		if file_path:  # Check if the user selected a file
			self.edit_scene.graphManager.save(file_path)
			print(f"File saved to: {file_path}")
			QMessageBox.information(self, "Save File", "Save the current file!")
			return("saved")

		return ("canceled")




	def load(self, file_path):
		"""Load a TLSPN model from a file."""

		with open(file_path, 'r') as json_file:
			save_dic = json.load(json_file)

			# Load the model
			loaded_tlspn = TLSPN.from_dict(save_dic)

			self.set_model(loaded_tlspn)


			# Create graphical representations
			for place in self.TLSPN.places.values():
				place_data = save_dic["places"][str(place.id)]
				self.edit_scene.graphManager.add_place(place, place_data.get("pos_x", 0), place_data.get("pos_y", 0))

			for transition in self.TLSPN.transitions.values():
				transition_data = save_dic["transitions"][str(transition.id)]
				self.edit_scene.graphManager.add_transition(
					transition,
					transition_data.get("pos_x", 0),
					transition_data.get("pos_y", 0),
					transition_data.get("orientation", 0)
				)

			# Create arcs after all places and transitions exist
			for arc in self.TLSPN.arcs.values():
				source_item = (
						self.edit_scene.graphManager.place_to_graph_place.get(arc.source) or
						self.edit_scene.graphManager.transition_to_graph_transition.get(arc.source)
				)
				target_item = (
						self.edit_scene.graphManager.place_to_graph_place.get(arc.target) or
						self.edit_scene.graphManager.transition_to_graph_transition.get(arc.target)
				)
				if source_item and target_item:
					self.edit_scene.graphManager.add_arc(arc, source_item, target_item)
					print(save_dic["arcs"])
					for cp_pos in save_dic["arcs"][str(arc.id)]["control_points"]:
						graph_arc=self.edit_scene.graphManager.arc_to_graph_arc[arc]
						graph_arc.addControlPoint(QPointF(cp_pos[0],cp_pos[1]))


			self.edit_scene.views()[0].centerOn(QPointF(save_dic["general_info"]["view_pos"][0],save_dic["general_info"]["view_pos"][1]))