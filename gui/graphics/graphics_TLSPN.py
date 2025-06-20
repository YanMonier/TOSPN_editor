from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsPathItem, QGraphicsEllipseItem
from PySide2.QtGui import QBrush, QColor, QPen, QPainterPath, QPolygonF, QPainterPathStroker
from PySide2.QtCore import Qt, QRectF, QPointF

from gui.widgets.widgets import DraggableItem, DraggableTextItem

import math
import json

from core.model.TLSPN.tlspn import TLSPN


# from tools.TLSPN import TLSPN, Output, Place, Event, Transition, Arc        Old code



class GraphManagerTLSPN():
	def __init__(self, scene, tlspn):
		"""Initialize the GraphManager with a scene and TLSPN model."""
		self.scene = scene
		self.TLSPN = tlspn

		# Dictionaries to map model objects to their graphical representations
		self.arc_to_graph_arc = {}
		self.transition_to_graph_transition = {}
		self.place_to_graph_place = {}
		self.arc_history = {}

	def add_place(self, place, x, y):
		"""Add a graphical representation of a place."""
		place_graph_item = GraphPlaceItemTLSPN(self, place, x, y)
		self.scene.addItem(place_graph_item)
		self.place_to_graph_place[place] = place_graph_item
		#place_graph_item.setFlag(QGraphicsItem.ItemIsMovable)
		return place_graph_item

	def add_transition(self, transition, x, y, orientation=0):
		"""Add a graphical representation of a transition."""
		transition_graph_item = GraphTransitionItemTLSPN(self, transition, x, y, orientation)
		self.scene.addItem(transition_graph_item)
		self.transition_to_graph_transition[transition] = transition_graph_item
		#transition_graph_item.setFlag(QGraphicsItem.ItemIsMovable)
		return transition_graph_item

	def add_arc(self, arc, source_item, target_item):

		can_create = False
		if source_item not in self.arc_history:
			self.arc_history[source_item] = {}
			can_create = True
		if target_item not in self.arc_history[source_item]:
			can_create = True
		if can_create:
			"""Add a graphical representation of an arc."""
			arc_graph_item = GraphArcItemTLSPN(self, arc, source_item, target_item)
			self.scene.addItem(arc_graph_item)
			arc_graph_item.setZValue(-100)
			self.arc_to_graph_arc[arc] = arc_graph_item

			# Add arc to source and target items' line lists
			source_item.line.append(arc_graph_item)
			target_item.line.append(arc_graph_item)

			# Track arc history for uniqueness checking
			self.arc_history[source_item][target_item] = 1
		else:
			arc_graph_item = None

		return arc_graph_item

	def remove_arc(self, arc):
		"""Remove a graphical representation of an arc."""
		if arc in self.arc_to_graph_arc:
			arc_graph_item = self.arc_to_graph_arc[arc]

			for cp in arc_graph_item.control_points.copy():
				arc_graph_item.removeControlPoint(cp)

			# Remove arc from source and target items' line lists
			if arc_graph_item.node1.line and arc_graph_item in arc_graph_item.node1.line:
				arc_graph_item.node1.line.remove(arc_graph_item)
			if arc_graph_item.node2.line and arc_graph_item in arc_graph_item.node2.line:
				arc_graph_item.node2.line.remove(arc_graph_item)

			self.scene.removeItem(arc_graph_item)

			# Clean up arc history
			if arc_graph_item.node1 in self.arc_history:
				if arc_graph_item.node2 in self.arc_history[arc_graph_item.node1]:
					del self.arc_history[arc_graph_item.node1][arc_graph_item.node2]

			del self.arc_to_graph_arc[arc]

	def remove_place(self, place):
		"""Remove a graphical representation of a place and its connected arcs."""
		if place in self.place_to_graph_place:
			# Remove connected arcs first
			for arc in list(place.input_arcs + place.output_arcs):
				self.remove_arc(arc)

			# Remove place graphics
			place_graph_item = self.place_to_graph_place[place]
			self.scene.removeItem(place_graph_item)
			del self.place_to_graph_place[place]

			# Remove from model
			self.TLSPN.remove_place(place)

	def remove_transition(self, transition):
		"""Remove a graphical representation of a transition and its connected arcs."""
		if transition in self.transition_to_graph_transition:
			# Remove connected arcs first
			for arc in list(transition.input_arcs + transition.output_arcs):
				self.remove_arc(arc)

			# Remove transition graphics
			transition_graph_item = self.transition_to_graph_transition[transition]
			self.scene.removeItem(transition_graph_item)
			del self.transition_to_graph_transition[transition]

			# Remove from model
			self.TLSPN.remove_transition(transition)

	def empty_self(self):
		"""Clear all graphical elements and reset the TLSPN model."""
		# Remove all outputs and events
		for output in list(self.TLSPN.outputs.values()):
			if output.name != ".":  # Keep the lambda event
				self.TLSPN.remove_output(output)

		for event in list(self.TLSPN.events.values()):
			if event.name != "λ":  # Keep the lambda event
				self.TLSPN.remove_event(event)

		# Remove all transitions and places
		for transition in list(self.TLSPN.transitions.values()):
			self.remove_transition(transition)

		for place in list(self.TLSPN.places.values()):
			self.remove_place(place)

		# Create a new TLSPN instance
		self.TLSPN = None

	def save(self, file_path):
		"""Save the TLSPN model to a file."""
		save_dic = self.TLSPN.to_dict()
		save_dic["file_type"]="TLSPN_edit_tab"

		# Add graphical information
		for place_id, place in self.TLSPN.places.items():
			if place in self.place_to_graph_place:
				graph_place = self.place_to_graph_place[place]
				save_dic["places"][place_id]["pos_x"] = graph_place.pos().x()
				save_dic["places"][place_id]["pos_y"] = graph_place.pos().y()

		for transition_id, transition in self.TLSPN.transitions.items():
			if transition in self.transition_to_graph_transition:
				graph_transition = self.transition_to_graph_transition[transition]
				save_dic["transitions"][transition_id]["pos_x"] = graph_transition.pos().x()
				save_dic["transitions"][transition_id]["pos_y"] = graph_transition.pos().y()
				save_dic["transitions"][transition_id]["orientation"] = graph_transition.orientation

		for arc_id, arc in self.TLSPN.arcs.items():
			if arc in self.arc_to_graph_arc:
				graph_arc = self.arc_to_graph_arc[arc]
				save_dic["arcs"][arc_id]["control_points"] = []
				for cp in graph_arc.control_points:
					save_dic["arcs"][arc_id]["control_points"].append([cp.pos().x(),cp.pos().y()])

		view_center = self.scene.views()[0].mapToScene(self.scene.views()[0].viewport().rect().center())
		save_dic["general_info"]["view_pos"]=[view_center.x(),view_center.y()]


		with open(file_path, 'w') as json_file:
			json.dump(save_dic, json_file, indent=4)

	def load(self, file_path):
		"""Load a TLSPN model from a file."""
		self.empty_self()

		with open(file_path, 'r') as json_file:
			save_dic = json.load(json_file)

			# Load the model
			loaded_tlspn = TLSPN.from_dict(save_dic)

			# Update our TLSPN reference
			self.scene.parent.set_model(loaded_tlspn)


			# Create graphical representations
			for place in self.TLSPN.places.values():
				place_data = next(p for p in save_dic["places"] if p["id"] == place.id)
				self.add_place(place, place_data.get("pos_x", 0), place_data.get("pos_y", 0))

			for transition in self.TLSPN.transitions.values():
				transition_data = next(t for t in save_dic["transitions"] if t["id"] == transition.id)
				self.add_transition(
					transition,
					transition_data.get("pos_x", 0),
					transition_data.get("pos_y", 0),
					transition_data.get("orientation", 0)
				)

			# Create arcs after all places and transitions exist
			for arc in self.TLSPN.arcs.values():
				source_item = (
						self.place_to_graph_place.get(arc.source) or
						self.transition_to_graph_transition.get(arc.source)
				)
				target_item = (
						self.place_to_graph_place.get(arc.target) or
						self.transition_to_graph_transition.get(arc.target)
				)
				if source_item and target_item:
					self.add_arc(arc, source_item, target_item)






class GraphPlaceItemTLSPN(DraggableItem):
	def __init__(self, graphTLSPN, place, x, y):
		"""Initialize a graphical place item."""
		self.place_radius = 15
		super().__init__(x, y)
		self.place = place
		self.graphTLSPN=graphTLSPN

		self.boundingRectValue = QRectF(-self.place_radius - 10, -self.place_radius - 10, 2 * self.place_radius + 20,
										2 * self.place_radius + 20)

		self.drag_text = DraggableTextItem("", self)  # Note: The text item is a child of CustomItem
		self.drag_text.updateText(self.place.name)

		self.color = QColor(0, 0, 0)
		self.token_color = QColor(0, 0, 0)
		self.pend_width = 1
		self.line = []
		self.is_selected = False
		self.defaultZvalue = 1

		# Set flags
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
		self.setAcceptHoverEvents(True)

		# Add as listener to the place
		self.place.add_listener(self)

	def boundingRect(self):
		return self.boundingRectValue

	def paint(self, painter, option, widget=None):
		painter.setBrush(QBrush(QColor(255, 255, 255)))  # White fill
		pen = QPen(self.color)
		pen.setWidth(self.pend_width)
		painter.setPen(pen)
		painter.drawEllipse(-self.place_radius, -self.place_radius, 2 * self.place_radius,
							2 * self.place_radius)  # Draw the node as a circle

		# Draw token number
		painter.setPen(QPen(self.token_color))
		painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.place.token_number))
		for line in self.line:
			line.updateLine()

	def on_change(self, subject, event_type, data):
		"""Handle changes in the place model."""
		if event_type == "name_changed":
			self.drag_text.updateText(data["new"])
		elif event_type == "token_changed":
			self.update()  # Redraw to show new token count

	def set_color(self, r, g, b):
		"""Method to change the color dynamically."""
		self.color = QColor(r, g, b)  # Update the color
		self.drag_text.set_color(r, g, b)
		self.update()  # Request a repaint to apply the new color

	def selected(self):
		self.is_selected = True
		self.set_color(0, 0, 255)
		self.pend_width = 4
		self.update()

	def unselected(self):
		self.is_selected = False
		self.set_color(0, 0, 0)
		self.pend_width = 1
		self.update()

	def select(self):
		if self.is_selected == False:
			self.set_color(255, 0, 0)
			self.pend_width = 4
		self.update()

	def unselect(self):
		if self.is_selected == False:
			self.set_color(0, 0, 0)
			self.pend_width = 1
			self.update()

	def mouseMoveEvent(self, event):
		# Update all connected arcs
		for line in self.line:
			line.updateLine()
		super().mouseMoveEvent(event)
		# Ensure scene updates
		if self.scene():
			self.scene().update()

	def resetZvalue(self):
		self.setZValue(self.defaultZvalue)


class GraphTransitionItemTLSPN(DraggableItem):
	def __init__(self, graphTLSPN, transition, x, y, orientation=0):
		super().__init__(x, y)
		self.transition = transition
		self.graphTLSPN = graphTLSPN
		if orientation == 0:
			self.L = 30
			self.l = 7.5
		else:
			self.L = 7.5
			self.l = 30
		self.orientation = orientation

		self.boundingRectValue = QRectF(-(self.L / 2) - 5, -(self.l / 2) - 5, (self.L) + 10, (self.l) + 10)
		#self.setPos(x, y)

		self.drag_text = DraggableTextItem("", self)  # Note: The text item is a child of CustomItem
		self.drag_text.updateText("{}\n{} {} {}".format(self.transition.name,
													  self.transition.event.name if self.transition.event else "",
													  str(self.transition.timing_interval),
													  self.transition.output.name if self.transition.output else ""))
		self.pend_width = 1
		self.set_color(0, 0, 0)
		self.set_in_color(0,0,0)
		self.line = []
		self.is_selected = False
		self.defaultZvalue = 1

		#self.setFlag(QGraphicsItem.ItemIsSelectable)
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
		self.setAcceptHoverEvents(True)

		# Add as listener to the transition
		self.transition.add_listener(self)


	def paint(self, painter, option, widget=None):
		painter.setBrush(QBrush(self.in_color))
		self.pen = QPen(self.color)
		self.pen.setWidth(self.pend_width)
		painter.setPen(QPen(self.pen))
		painter.drawRect(QRectF(-self.L / 2, -self.l / 2, self.L, self.l))
		for line in self.line:
			line.updateLine()

	def simulation_clicked(self):
		print(f"simulation clicked {self.transition.id}")
		if self.transition.simulation_state=="enabled":
			event_name=self.transition.event.name
			self.graphTLSPN.TLSPN.activate_event(event_name)
		elif self.transition.simulation_state == "firable":
			self.graphTLSPN.TLSPN.fire_transition(self.transition)



	def on_change(self, subject, event_type, data):
		"""Handle changes in the transition model."""
		if event_type == "name_changed":
			self.drag_text.updateText("{}\n{} {} {}".format(
				self.transition.name,
				self.transition.event.name if self.transition.event else "",
				str(self.transition.timing_interval),
				self.transition.output.name))
		elif event_type == "event_changed":
			self.drag_text.updateText("{}\n{} {} {}".format(
				self.transition.name,
				data["new"].name if data["new"] else "",
				str(self.transition.timing_interval),
				self.transition.output.name))
		elif event_type == "output_changed":
			self.drag_text.updateText("{}\n{} {} {}".format(
				self.transition.name,
				self.transition.event.name if self.transition.event else "",
				str(self.transition.timing_interval),
				data["new"].name if data["new"] else ""))
		elif event_type == "timing_changed":
			self.drag_text.updateText("{}\n{} {} {}".format(
				self.transition.name,
				self.transition.event.name if self.transition.event else "",
				str(self.transition.timing_interval),
				self.transition.output.name))
		elif event_type == "event_name_changed":
			self.drag_text.updateText("{}\n{} {} {}".format(
				self.transition.name,
				data["new"] if data["new"] else "",
				str(self.transition.timing_interval),
				self.transition.output.name))

		elif event_type == "simulation_enabled":
			self.set_in_color(173, 216, 230)
			self.set_txt_color(173, 216, 230)

		elif event_type == "simulation_activated_cant_fire":
			self.set_in_color(255, 179, 102)
			self.set_txt_color(255, 179, 102)

		elif event_type == "simulation_activated_can_fire":
			self.set_in_color(144, 238, 144)
			self.set_txt_color(144, 238, 144)

		elif event_type == "simulation_not_enabled":
			self.set_in_color(0, 0, 0)
			self.set_txt_color(0, 0, 0)

	def set_color(self, r, g, b):
		"""Method to change the color dynamically."""
		self.color = QColor(r, g, b)  # Update the color
		self.update()  # Request a repaint to apply the new color

	def set_txt_color(self,r, g, b):
		self.drag_text.set_color(r, g, b)
		self.update()

	def set_in_color(self, r, g, b):
		"""Method to change the color dynamically."""
		self.in_color = QColor(r, g, b)  # Update the color
		self.update()


	def selected(self):
		self.is_selected = True
		self.set_color(0, 0, 255)
		self.set_txt_color(0, 0, 255)
		self.pend_width = 4
		self.update()

	def unselected(self):
		self.is_selected = False
		if self.graphTLSPN.scene.state == "simulation":
			self.set_color(0, 0, 0)
			self.set_txt_color(self.in_color.red(), self.in_color.green(), self.in_color.blue())
		else:
			self.set_color(0, 0, 0)
			self.set_txt_color(0, 0, 0)
			self.set_in_color(0, 0, 0)
		self.pend_width = 1
		self.update()

	def select(self):
		if self.is_selected == False:
			self.set_color(255, 0, 0)
			self.set_txt_color(255, 0, 0)
			self.pend_width = 4
		self.update()

	def unselect(self):
		if self.is_selected == False:
			if self.graphTLSPN.scene.state=="simulation":
				self.set_color(0, 0, 0)
				self.set_txt_color(self.in_color.red(), self.in_color.green(), self.in_color.blue())
			else:
				self.set_color(0, 0, 0)
				self.set_txt_color(0, 0, 0)
			self.pend_width = 1
			self.update()

	def mouseMoveEvent(self, event):
		# Update all connected arcs
		for line in self.line:
			line.updateLine()
		super().mouseMoveEvent(event)
		# Ensure scene updates
		if self.scene():
			self.scene().update()

	def resetZvalue(self):
		self.setZValue(self.defaultZvalue)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_R:
			if self.is_selected == True:
				# Update orientation
				if self.orientation == 0:
					self.orientation = 1
				else:
					self.orientation = 0

				# Swap dimensions
				old_L = self.L
				self.L = self.l
				self.l = old_L

				# Update bounding rectangle
				self.boundingRectValue = QRectF(-((self.L + self.l) / 2) - 5, -((self.l + self.L) / 2) - 5,
												(self.L + self.l) + 10, (self.l + self.L) + 10)

				# Update all connected arcs
				for line in self.line:
					line.updateLine()

				# Update scene
				if self.scene():
					self.scene().update()
				self.update()
		else:
			super().keyPressEvent(event)

	def change_name(self, new_name):
		self.transition.name = new_name
		self.drag_text.updateText(
			"{}\n{}\n{}".format(self.transition.name, self.transition.event.name, str(self.transition.timing_interval)))

	def change_event(self, new_event):
		self.transition.change_event(new_event)
		self.drag_text.updateText(
			"{}\n{}\n{}".format(self.transition.name, self.transition.event.name, str(self.transition.timing_interval)))

	def change_clock_1(self, clock_1):
		self.transition.timing_interval[0] = clock_1
		self.drag_text.updateText(
			"{}\n{}\n{}".format(self.transition.name, self.transition.event.name, str(self.transition.timing_interval)))

	def change_clock_2(self, clock_2):
		self.transition.timing_interval[1] = clock_2
		self.drag_text.updateText(
			"{}\n{}\n{}".format(self.transition.name, self.transition.event.name, str(self.transition.timing_interval)))


class GraphArcItemTLSPN(QGraphicsPathItem):
	def __init__(self,graphTLSPN, arc, node1, node2):
		super().__init__()
		self.graphTLSPN = graphTLSPN
		self.arc = arc
		self.head_size = 15
		self.node1 = node1
		self.node2 = node2
		node1.line.append(self)
		node2.line.append(self)

		self.control_points = []


		self.color = QColor("black")
		self.is_selected = False
		self.defaultZvalue = 0

		# Create draggable text item for weight
		self.weight_text = DraggableTextItem(str(self.arc.weight), self)
		self.weight_text.updateText(str(self.arc.weight))

		# Track text offset from middle
		self.text_offset_x = 0
		self.text_offset_y = 0
		self.weight_text.mousePressEvent = self.startTextDrag
		self.weight_text.mouseReleaseEvent = self.endTextDrag

		# Add as listener to the arc
		self.arc.add_listener(self)
		self.adjusted_p1=node1.pos()
		self.adjusted_p2 = node2.pos()
		self.updateLine()

	def addControlPoint(self,pos):
		cp = self.createControlPoint(pos)
		self.control_points.append(cp)
		self.updateLine()
		return

	def insertControlPoint(self, pos):
		# Edge case: no control points, just insert at start
		if not self.control_points:
			# create new control point item at pos
			cp = self.createControlPoint(pos)
			self.control_points.append(cp)
			self.updateLine()
			return

		# Find where to insert based on closest segment
		min_dist = float('inf')
		insert_index = 0  # default to front

		# Prepare a list of points: start, all control points, end
		points = [self.node1.scenePos()]
		points.extend([cp.pos() for cp in self.control_points])
		points.append(self.node2.scenePos())

		# Iterate over segments
		for i in range(len(points) - 1):
			p_start = points[i]
			p_end = points[i + 1]

			# Calculate distance from pos to segment p_start-p_end
			dist = self.pointToSegmentDistance(pos, p_start, p_end)
			if dist < min_dist:
				min_dist = dist
				insert_index = i

		# Create new control point
		cp = self.createControlPoint(pos)

		# Insert control point at found index (after segment start)
		self.control_points.insert(insert_index, cp)

		# Update path
		self.updateLine()

	def createControlPoint(self, pos):
		cp = ControlPoint(pos, parent_edge=self)
		self.scene().addItem(cp)
		return cp

	def pointToSegmentDistance(self, p, a, b):
		"""Calculate shortest distance from point p to line segment ab"""
		# Vector ab
		ab = b - a
		# Vector ap
		ap = p - a
		t = QPointF.dotProduct(ap, ab) / QPointF.dotProduct(ab, ab) if QPointF.dotProduct(ab, ab) != 0 else 0
		t = max(0, min(1, t))
		closest = a + ab * t
		return (p - closest).manhattanLength()  # or use euclidean length if preferred

	def removeControlPoint(self, cp):
		if cp in self.control_points:
			self.control_points.remove(cp)
			scene = self.scene()
			if scene:
				scene.removeItem(cp)
			cp.setParentItem(None)
			self.updateLine()

	def startTextDrag(self, event):
		"""Called when text dragging starts to calculate initial offset."""
		mid = self.pathMidpoint(self.path())
		self.text_offset_x = self.weight_text.pos().x() - mid.x()
		self.text_offset_y = self.weight_text.pos().y() - mid.y()
		super(DraggableTextItem, self.weight_text).mousePressEvent(event)

	def endTextDrag(self, event):
		"""Called when text dragging ends to update final offset."""
		mid = self.pathMidpoint(self.path())
		self.text_offset_x = self.weight_text.pos().x() - mid.x()
		self.text_offset_y = self.weight_text.pos().y() - mid.y()
		super(DraggableTextItem, self.weight_text).mouseReleaseEvent(event)

	def pathMidpoint(self,path):
		"""Computes midpoint along the path (linear approximation)."""
		total_len = 0
		points = []

		for i in range(1, path.elementCount()):
			p1 = path.elementAt(i - 1)
			p2 = path.elementAt(i)
			pt1 = QPointF(p1.x, p1.y)
			pt2 = QPointF(p2.x, p2.y)
			segment_len = (pt2 - pt1).manhattanLength()
			total_len += segment_len
			points.append((total_len, pt1, pt2))

		if total_len == 0:
			return self.start  # fallback

		half_len = total_len / 2
		for seg_len, pt1, pt2 in points:
			if seg_len >= half_len:
				return (pt1 + pt2) / 2

		return self.end  # fallback



	def updateLine(self):
		# Get positions of nodes

		path=self.path()

		p1 = self.node1.scenePos()
		p2 = self.node2.scenePos()

		if self.control_points != []:
			e0 = self.control_points[0]
			e_last = self.control_points[-1]
		else:
			e0 = self.node2.scenePos()
			e_last = self.node1.scenePos()



		# Calculate vector
		dx1 = e0.x() - p1.x()
		dy1 = e0.y() - p1.y()
		length = math.hypot(dx1, dy1)

		dx2 = p2.x() - e_last.x()
		dy2 = p2.y() - e_last.y()
		length2 = math.hypot(dx2, dy2)

		if length == 0:
			dx1=0
			dy1=0
		else:
			# Normalize
			dx1 /= length
			dy1 /= length
		if length2 == 0:
			dx2 = 0
			dy2 = 0
		else:
			# Normalize
			dx2 /= length2
			dy2 /= length2



		# Adjust p1 (start point) based on node1 shape
		if isinstance(self.node1, GraphPlaceItemTLSPN):
			p1 = QPointF(p1.x() + dx1 * self.node1.place_radius, p1.y() + dy1 * self.node1.place_radius)
		else:
			p1 = self._adjustToRectEdge(self.node1, p1, dx1, dy1)

		# Adjust p2 (end point) based on node2 shape
		if isinstance(self.node2, GraphPlaceItemTLSPN):
			p2 = QPointF(p2.x() - dx2 * self.node2.place_radius, p2.y() - dy2 * self.node2.place_radius)
		else:
			p2 = self._adjustToRectEdge(self.node2, p2, -dx2, -dy2)

		self.adjusted_p1=p1
		self.adjusted_p2=p2

		# Build path with control points
		path = QPainterPath(p1)
		for ctrl in self.control_points:
			path.lineTo(ctrl.pos())
		path.lineTo(p2)

		self.setPath(path)

		# --- Update the text label position ---
		# Get midpoint from path
		mid = self.pathMidpoint(path)
		text_x = mid.x() + self.text_offset_x
		text_y = mid.y() + self.text_offset_y

		self.weight_text.setPos(
			text_x - self.weight_text.boundingRect().width() / 2,
			text_y - self.weight_text.boundingRect().height() / 2
		)



	def _adjustToRectEdge(self, node, point, dx, dy):
		angle = math.atan2(dy, dx)
		if abs(math.cos(angle)) * node.L > abs(math.sin(angle)) * node.l:
			# Vertical edge
			tx = math.copysign(node.L / 2, dx)
			ty = (dy / dx) * tx if dx != 0 else math.copysign(node.l / 2, dy)
			if abs(ty) > node.l / 2:
				ty = math.copysign(node.l / 2, ty)
				tx = (dx / dy) * ty if dy != 0 else math.copysign(node.L / 2, dx)
		else:
			# Horizontal edge
			ty = math.copysign(node.l / 2, dy)
			tx = (dx / dy) * ty if dy != 0 else math.copysign(node.L / 2, dx)
			if abs(tx) > node.L / 2:
				tx = math.copysign(node.L / 2, tx)
				ty = (dy / dx) * tx if dx != 0 else math.copysign(node.l / 2, dy)

		return QPointF(point.x() + tx, point.y() + ty)

	def paint(self, painter, option, widget):
		# Draw the path with custom pen
		pen = QPen(self.color)
		pen.setWidth(2)
		painter.setPen(pen)
		painter.setBrush(Qt.NoBrush)
		painter.drawPath(self.path())

		# Draw arrow head
		path = self.path()



		if self.control_points!=[]:
			last = self.adjusted_p2
			prev = self.control_points[-1]
		else:
			last = self.adjusted_p2
			prev = self.adjusted_p1

		dx = last.x() - prev.x()
		dy = last.y() - prev.y()
		angle = math.atan2(dy, dx)

		arrow_p1 = QPointF(last.x(), last.y())
		arrow_p2 = QPointF(
			arrow_p1.x() - self.head_size * math.cos(angle - math.pi / 6),
			arrow_p1.y() - self.head_size * math.sin(angle - math.pi / 6)
		)
		arrow_p3 = QPointF(
			arrow_p1.x() - self.head_size * math.cos(angle + math.pi / 6),
			arrow_p1.y() - self.head_size * math.sin(angle + math.pi / 6)
		)

		arrow_head = QPolygonF([arrow_p1, arrow_p2, arrow_p3])
		painter.setBrush(QBrush(self.color))
		painter.drawPolygon(arrow_head)

	def shape(self):
		path = QPainterPath()
		base_path = self.path()

		# Use a stroker to widen the shape for easier clicking
		stroker = QPainterPathStroker()
		stroker.setWidth(10)
		shape_path = stroker.createStroke(base_path)

		# Add arrow head to shape
		if self.control_points!=[]:
			last_point = self.adjusted_p2
			prev_point = self.control_points[-1]
		else:
			last_point = self.adjusted_p2
			prev_point = self.adjusted_p1
		dx = last_point.x() - prev_point.x()
		dy = last_point.y() - prev_point.y()
		angle = math.atan2(dy, dx)

		arrow_p1 = QPointF(last_point.x(), last_point.y())
		arrow_p2 = QPointF(
			arrow_p1.x() - self.head_size * math.cos(angle - math.pi / 6),
			arrow_p1.y() - self.head_size * math.sin(angle - math.pi / 6)
		)
		arrow_p3 = QPointF(
			arrow_p1.x() - self.head_size * math.cos(angle + math.pi / 6),
			arrow_p1.y() - self.head_size * math.sin(angle + math.pi / 6)
		)

		arrow_path = QPainterPath()
		arrow_path.moveTo(arrow_p1)
		arrow_path.lineTo(arrow_p2)
		arrow_path.lineTo(arrow_p3)
		arrow_path.closeSubpath()

		shape_path.addPath(arrow_path)

		return shape_path


	def on_change(self, subject, event_type, data):
		"""Handle changes in the arc model."""
		if event_type == "weight_changed":
			self.weight_text.updateText(str(data))
			#self.weight_text.setDefaultTextColor(self.color)
			self.updateLine()  # Update to reposition weight text

	def set_color(self, r, g, b):
		self.color = QColor(r, g, b)
		self.weight_text.set_color(r, g, b)
		self.update()

	def selected(self):
		self.is_selected = True
		self.set_color(0, 0, 255)
		self.update()

	def unselected(self):
		self.is_selected = False
		self.set_color(0, 0, 0)
		self.update()

	def select(self):
		if not self.is_selected:
			self.set_color(255, 0, 0)
		self.update()

	def unselect(self):
		if not self.is_selected:
			self.set_color(0, 0, 0)
		self.update()

	def resetZvalue(self):
		self.setZValue(self.defaultZvalue)

	def mousePressEvent(self, event):
		if event.button() == Qt.RightButton:
			pos = event.pos()
			# Add control point at click position (in edge local coordinates)
			self.insertControlPoint(pos)
		super().mousePressEvent(event)

class TempGraphLineTLSPN(QGraphicsLineItem):
	def __init__(self, pos1, pos2):
		"""Initialize a temporary line for arc creation preview."""
		super().__init__()
		self.pos1 = pos1
		self.pos2 = pos2

		# Set up appearance
		pen = QPen(QColor(100, 100, 100))  # Gray color
		pen.setStyle(Qt.DashLine)  # Dashed line
		pen.setWidth(2)
		self.setPen(pen)

		# Initial update
		self.updateLine()

	def updateLine(self):
		"""Update the line position."""
		self.setLine(self.pos1.x(), self.pos1.y(), self.pos2.x(), self.pos2.y())

	def update_pos(self, pos1, pos2):
		"""Update the start and end positions."""
		self.pos1 = pos1
		self.pos2 = pos2
		self.updateLine()


class ControlPoint(QGraphicsEllipseItem):
	def __init__(self, pos, parent_edge, radius=3):
		self.parent_edge = parent_edge
		self.scene2 = self.parent_edge.graphTLSPN.scene
		super().__init__(-radius, -radius, 2 * radius, 2 * radius)

		self.setBrush(Qt.gray)
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
		self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # keep size constant on zoom
		self.setZValue(2)
		self.setPos(pos)
		self.grab_radius = 6  # larger grab radius


	def itemChange(self, change, value):
		if change == QGraphicsItem.ItemPositionChange:
			# Notify parent edge to update path on move

			if self.scene2.isGridOn==True:
				# value is the new position (QPointF)
				GRID_SIZE=self.scene2.grid_size
				new_pos = value
				# Snap to grid
				x = round(new_pos.x() / GRID_SIZE) * GRID_SIZE
				y = round(new_pos.y() / GRID_SIZE) * GRID_SIZE
				return QPointF(x, y)

		elif change == QGraphicsItem.ItemPositionHasChanged:
			self.parent_edge.updateLine()

		return super().itemChange(change, value)

	def mousePressEvent(self, event):
		if event.button() == Qt.RightButton:
			self.parent_edge.removeControlPoint(self)
		super().mousePressEvent(event)


	def shape(self):
		path = QPainterPath()
		# Larger grab radius for mouse interaction
		path.addEllipse(-self.grab_radius, -self.grab_radius, 2 * self.grab_radius, 2 * self.grab_radius)
		return path