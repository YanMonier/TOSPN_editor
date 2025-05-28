from gui.graphics.graphics_TLSPN import GraphPlaceItemTLSPN, GraphTransitionItemTLSPN, GraphArcItemTLSPN, TempGraphLineTLSPN, GraphManagerTLSPN
from gui.widgets.widgets import DraggableTextItem
from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from core.model.TLSPN.tlspn import TLSPN


class GraphConstructionScene(QGraphicsScene):
	def __init__(self, parent=None):
		"""Initialize the scene for TLSPN construction."""
		super().__init__(parent)
		self.parent = parent
		self.state = "none"
		self.TLSPN = TLSPN()
		self.graphManager = GraphManagerTLSPN(self, self.TLSPN)

		# Selection tracking
		self.items_under_cursor = []
		self.last_items_under_cursor = []
		self.selected_item_1 = None
		self.selected_item_2 = None
		self.is_clicked = None

		# Temporary arc for preview
		self.temp_arc = TempGraphLineTLSPN(QPoint(0, 0), QPoint(0, 0))
		self.addItem(self.temp_arc)
		self.temp_arc.setVisible(False)

		# Selection management
		self.selected_item_list = []
		self.top_mono_item = None
		self.last_top_mono_item = None
		self.mono_selected_item = None

		self.mouse_clicked = False

	def empty_selected(self):
		"""Clear all selections."""
		if self.mono_selected_item is not None:
			self.mono_selected_item.clearFocus()
			self.mono_selected_item.unselected()

		if self.last_top_mono_item is not None:
			self.last_top_mono_item.clearFocus()
			self.last_top_mono_item.unselect()
			self.last_top_mono_item.resetZvalue()

		for item in self.selected_item_list:
			item.clearFocus()
			item.unselected()

		self.selected_item_list = []
		self.selected_item_1 = None
		self.selected_item_2 = None
		self.mono_selected_item = None

	def mousePressEvent(self, event):
		"""Handle mouse press events."""
		self.mouse_clicked = True

		if event.button() == Qt.LeftButton:
			# Handle selection changes
			if self.top_mono_item != self.mono_selected_item or self.top_mono_item is None:
				if self.mono_selected_item is not None:
					self.empty_selected()
					self.unselect_item()

			if self.top_mono_item is not None:
				if self.top_mono_item != self.mono_selected_item:
					self.mono_selected_item = self.top_mono_item
					self.mono_selected_item.selected()
					self.mono_selected_item.setFocus()
					self.select_item(self.mono_selected_item)

			# Handle state-specific actions
			if self.state == "add_place":
				if self.top_mono_item is None:
					new_place = self.TLSPN.add_place()
					self.graphManager.add_place(new_place, event.scenePos().x(), event.scenePos().y())

			elif self.state == "add_transition":
				if self.top_mono_item is None:
					new_transition = self.TLSPN.add_transition()
					self.graphManager.add_transition(new_transition, event.scenePos().x(), event.scenePos().y())

			elif self.state == "add_arc":
				if self.selected_item_1 is None:
					self.items_under_cursor = self.items(event.scenePos())
					for item in self.items_under_cursor:
						if isinstance(item, (GraphPlaceItemTLSPN, GraphTransitionItemTLSPN)):
							self.selected_item_1 = item
							break

		super().mousePressEvent(event)

	def select_item(self, item_selected):
		"""Update property editor based on selected item."""
		if isinstance(item_selected, GraphPlaceItemTLSPN):
			self.parent.set_property_editor("place")
			self.parent.current_property_editor.update_properties(item_selected)
		elif isinstance(item_selected, GraphTransitionItemTLSPN):
			self.parent.set_property_editor("transition")
			self.parent.current_property_editor.update_properties(item_selected)

	def unselect_item(self):
		"""Clear property editor."""
		self.parent.set_property_editor(None)

	def mouseReleaseEvent(self, event):
		"""Handle mouse release events."""
		self.mouse_clicked = False

		if self.state == "add_arc":
			if self.selected_item_1 is not None:
				self.items_under_cursor = self.items(event.scenePos())
				for item in self.items_under_cursor:
					if isinstance(item, (GraphPlaceItemTLSPN , GraphTransitionItemTLSPN)):
						if item != self.selected_item_1:
							# Check valid connections (place->transition or transition->place)
							if (isinstance(item, GraphPlaceItemTLSPN ) and
									isinstance(self.selected_item_1, GraphTransitionItemTLSPN)):
								self.selected_item_2 = item
								break
							elif (isinstance(item, GraphTransitionItemTLSPN ) and
								  isinstance(self.selected_item_1, GraphPlaceItemTLSPN)):
								self.selected_item_2 = item
								break

				if self.selected_item_2 is not None:
					# Create arc if connection is valid and unique
					# Get model objects
					source = self.selected_item_1.place if isinstance(self.selected_item_1,
																	  GraphPlaceItemTLSPN) else self.selected_item_1.transition
					target = self.selected_item_2.place if isinstance(self.selected_item_2,
																	  GraphPlaceItemTLSPN) else self.selected_item_2.transition

					# Create arc
					new_arc = self.TLSPN.add_arc(source, target)

					if new_arc is not None:
						self.graphManager.add_arc(new_arc, self.selected_item_1, self.selected_item_2)

		self.selected_item_1 = None
		self.selected_item_2 = None
		self.temp_arc.setVisible(False)

		super().mouseReleaseEvent(event)

	def mouseMoveEvent(self, event):
		"""Handle mouse move events."""
		# Handle mono selection
		if self.state in ["move", "add_arc", "add_place", "add_transition"]:
			self.items_under_cursor = self.items(event.scenePos())
			self.top_mono_item = None

			# Find top-most selectable item
			for item in self.items_under_cursor:
				if isinstance(item, (GraphPlaceItemTLSPN, GraphTransitionItemTLSPN, GraphArcItemTLSPN, DraggableTextItem)):
					if isinstance(item, DraggableTextItem):
						self.top_mono_item = item.parent
					else:
						self.top_mono_item = item
					break

			# Update hover states
			if self.last_top_mono_item is not None:
				if self.last_top_mono_item != self.top_mono_item:
					self.last_top_mono_item.unselect()
					self.last_top_mono_item.resetZvalue()

			if self.top_mono_item is not None:
				self.top_mono_item.select()
				self.top_mono_item.setZValue(2)
				self.last_top_mono_item = self.top_mono_item

		# Update temporary arc preview
		if self.selected_item_1 is not None and self.state == "add_arc":
			self.temp_arc.update_pos(self.selected_item_1.scenePos(), event.scenePos())
			self.temp_arc.setVisible(True)

		super().mouseMoveEvent(event)

	def keyPressEvent(self, event):
		"""Handle key press events."""
		if event.key() == Qt.Key_Delete:
			if self.state in ["move", "add_transition", "add_place"]:
				if self.mono_selected_item is not None:
					if isinstance(self.mono_selected_item, GraphArcItemTLSPN):
						self.graphManager.remove_arc(self.mono_selected_item.arc)
					elif isinstance(self.mono_selected_item, GraphTransitionItemTLSPN):
						self.graphManager.remove_transition(self.mono_selected_item.transition)
					elif isinstance(self.mono_selected_item, GraphPlaceItemTLSPN):
						self.graphManager.remove_place(self.mono_selected_item.place)
						self.empty_selected()
						self.unselect_item()

		super().keyPressEvent(event)




	def set_model(self, TLSPN):
		self.TLSPN= TLSPN
		#self.graphManager.empty_self()
		self.graphManager = GraphManagerTLSPN(self, self.TLSPN)

