
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from gui.graphics.graphics_TOSPN import GraphPlaceItem, GraphTransitionItem, GraphArcItem, TempGraphLine, GraphManager
from gui.widgets.widgets import DraggableTextItem
from PySide2.QtGui import QBrush, QColor, QPen
from PySide2.QtCore import Qt, QRectF, QPointF
from PySide2.QtWidgets import*
from PySide2.QtCore import*
from PySide2.QtGui import*
from tools.TOSPN import TOSPN




class GraphConstructionScene(QGraphicsScene):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.parent=parent
		self.state= "None"
		self.TOSPN = TOSPN()
		self.graphManager=GraphManager(self,self.TOSPN)


		#self.place_counter = 1  # Counter to give unique place IDs
		#self.transition_counter = 1
		#self.arc_counter = 1
		self.items_under_cursor=[]
		self.last_items_under_cursor=[]
		self.selected_item_1=None
		self.selected_item_2=None
		self.is_clicked=None
		self.temp_arc=None
		self.temp_arc = TempGraphLine(QPoint(0,0), QPoint(0,0))
		self.addItem(self.temp_arc)
		self.temp_arc.setVisible(False)


		self.arc_history={}
		self.selected_item_list=[]

		self.top_mono_item = None
		self.last_top_mono_item=None
		self.mono_selected_item=None

		self.mouse_clicked = False


	def empty_selected(self):

		if self.mono_selected_item != None:
			self.mono_selected_item.clearFocus()
			self.mono_selected_item.unselected()


		if self.last_top_mono_item != None:
			self.last_top_mono_item.clearFocus()
			self.last_top_mono_item.unselect()
			self.last_top_mono_item.resetZvalue()

		for item in self.selected_item_list:
			item.clearFocus()
			item.unselected()

		self.selected_item_list = []
		self.selected_item_1 = None
		self.selected_item_2 = None
		self.mono_selected_item=None

	def mousePressEvent(self, event : QGraphicsSceneMouseEvent):
		self.mouse_clicked=True
		if event.button() == Qt.LeftButton:
			if self.state=="add_place":

				newPlace=self.TOSPN.add_Place()
				self.graphManager.add_place(newPlace, event.scenePos().x(), event.scenePos().y())# Create a new place at the mouse position
			elif self.state=="add_transition":
				newTransition = self.TOSPN.add_Transition()
				self.graphManager.add_transition(newTransition, event.scenePos().x(),event.scenePos().y())  # Create a new place at the mouse position
			elif self.state=="add_arc":
				if self.selected_item_1==None:
					self.items_under_cursor = self.items(event.scenePos())
					for item in self.items_under_cursor:
						if isinstance(item, GraphPlaceItem) or isinstance(item, GraphTransitionItem):
							self.selected_item_1 = item
							break
			elif self.state=="move":

				print("self.mono_selected_item",self.mono_selected_item)
				print('top ',self.top_mono_item)

				if self.top_mono_item != self.mono_selected_item or self.top_mono_item==None:
					if self.mono_selected_item != None:
						self.empty_selected()
						self.unselect_item()


				if self.top_mono_item != None:
					if self.top_mono_item != self.mono_selected_item:
						self.mono_selected_item=self.top_mono_item
						self.mono_selected_item.selected()
						self.mono_selected_item.setFocus()
						self.select_item(self.mono_selected_item)
						

		super().mousePressEvent(event)

	def select_item(self, item_selected):
		if isinstance(item_selected, GraphPlaceItem):
			self.parent.set_property_editor("place")
			self.parent.current_property_editor.update_properties(item_selected)

		elif isinstance(item_selected, GraphTransitionItem):
			self.parent.set_property_editor("transition")
			self.parent.current_property_editor.update_properties(item_selected)


	def unselect_item(self):
		self.parent.set_property_editor(None)

	def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
		self.mouse_clicked = False
		if self.state == "add_arc":
			if self.selected_item_1 != None:
				self.items_under_cursor = self.items(event.scenePos())
				for item in self.items_under_cursor:
					if isinstance(item, GraphPlaceItem) or isinstance(item, GraphTransitionItem):
						if item != self.selected_item_1:
							if isinstance(item, GraphPlaceItem) and isinstance(self.selected_item_1, GraphTransitionItem):
								self.selected_item_2=item
								break
							elif isinstance(item, GraphTransitionItem) and isinstance(self.selected_item_1, GraphPlaceItem):
								self.selected_item_2 = item
								break

				if self.selected_item_2!=None:
					if self.selected_item_1 not in self.arc_history.keys():
						self.arc_history[self.selected_item_1]={}
					if self.selected_item_2 not in self.arc_history[self.selected_item_1].keys():
						self.arc_history[self.selected_item_1][self.selected_item_2]=1

						if isinstance(self.selected_item_1, GraphPlaceItem):
							object1=self.selected_item_1.place
						else:
							object1 = self.selected_item_1.transition
						if isinstance(self.selected_item_2, GraphPlaceItem):
							object2=self.selected_item_2.place
						else:
							object2 = self.selected_item_2.transition

						newArc = self.TOSPN.add_Arc(object1,object2)
						self.graphManager.add_arc(newArc,self.selected_item_1, self.selected_item_2)

		self.selected_item_1=None
		self.selected_item_2=None
		self.temp_arc.setVisible(False)

		super().mouseReleaseEvent(event)



	def mouseMoveEvent(self, event):

		#########Mono selection#################
		if self.state == "move" or self.state=="add_arc":
			self.items_under_cursor = self.items(event.scenePos())
			self.top_mono_item=None
			top_item=None
			for item in self.items_under_cursor:
				if isinstance(item, GraphPlaceItem) or isinstance(item, GraphTransitionItem) or (isinstance(item, GraphArcItem) and self.state == "move") or (isinstance(item, DraggableTextItem) and self.state == "move"):
					top_item=item
					break
			if top_item!=None:
				if isinstance(top_item, DraggableTextItem):
					self.top_mono_item=top_item.parent
				else:
					self.top_mono_item=top_item


			if self.last_top_mono_item!=None:
				if self.last_top_mono_item!=self.top_mono_item:
					self.last_top_mono_item.unselect()
					self.last_top_mono_item.resetZvalue()

			if self.top_mono_item!=None:
				self.top_mono_item.select()
				self.top_mono_item.setZValue(2)
				self.last_top_mono_item=self.top_mono_item
		############END MONO SELECTON#################



		##########TEMP ARC CREATION##########################################
		if self.selected_item_1!=None and self.state=="add_arc":
			self.temp_arc.update_pos(self.selected_item_1.scenePos(),event.scenePos())
			self.temp_arc.setVisible(True)

		super().mouseMoveEvent(event)  # Always call the base class method

	def keyPressEvent(self, event):
		# Check if the Delete (Suppr) key is pressed
		print("key2")
		if event.key() == Qt.Key_Delete:
			if self.state == "move":
				if self.mono_selected_item!=None:
					if isinstance(self.mono_selected_item,GraphArcItem):
						self.graphManager.remove_arc(self.mono_selected_item.arc)
						self.empty_selected()
						self.unselect_item()

					if isinstance(self.mono_selected_item,GraphTransitionItem):
						self.graphManager.remove_transition(self.mono_selected_item.transition)
						self.empty_selected()
						self.unselect_item()

					if isinstance(self.mono_selected_item,GraphPlaceItem):
						self.graphManager.remove_place(self.mono_selected_item.place)
						self.empty_selected()
						self.unselect_item()

		super().keyPressEvent(event)


