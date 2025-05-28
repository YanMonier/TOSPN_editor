from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem
from PySide2.QtGui import QBrush, QColor, QPen,  QPainterPath, QPolygonF
from PySide2.QtCore import Qt, QRectF, QPointF

from gui.widgets.widgets import DraggableItem, DraggableTextItem

import math
import json

from core.model.TOSPN.tospn import TOSPN

#from tools.TOSPN import TOSPN, Output, Place, Event, Transition, Arc        Old code

"""
class Node(QGraphicsItem):
    def __init__(self, x, y,parent=None):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.setPos(x, y)
        self.radius = 4  # Small circle (node)
        self.fill_color=QColor(0,0,0)
        self.pen_color=QColor(0,0,0)

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter, option, widget=None):
        if self.isVisible():
            painter.setBrush(self.fill_color)  # Black node
            pen=QPen(self.pen_color)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawEllipse(self.boundingRect())  # Draw the circle
"""


class GraphManager():
    def __init__(self, scene, tospn):
        """Initialize the GraphManager with a scene and TOSPN model."""
        self.scene = scene
        self.TOSPN = tospn
        
        # Dictionaries to map model objects to their graphical representations
        self.arc_to_graph_arc = {}
        self.transition_to_graph_transition = {}
        self.place_to_graph_place = {}
        self.arc_history = {}
    
    def add_place(self, place, x, y):
        """Add a graphical representation of a place."""
        place_graph_item = GraphPlaceItem(place, x, y)
        self.scene.addItem(place_graph_item)
        self.place_to_graph_place[place] = place_graph_item
        place_graph_item.setFlag(QGraphicsItem.ItemIsMovable)
        return place_graph_item
    
    def add_transition(self, transition, x, y, orientation=0):
        """Add a graphical representation of a transition."""
        transition_graph_item = GraphTransitionItem(transition, x, y, orientation)
        self.scene.addItem(transition_graph_item)
        self.transition_to_graph_transition[transition] = transition_graph_item
        transition_graph_item.setFlag(QGraphicsItem.ItemIsMovable)
        return transition_graph_item
    
    def add_arc(self, arc, source_item, target_item):

        can_create=False
        if source_item not in self.arc_history:
            self.arc_history[source_item] = {}
            can_create=True
        if target_item not in self.arc_history[source_item]:
            
            can_create=True
        if can_create:
            """Add a graphical representation of an arc."""
            arc_graph_item = GraphArcItem(arc, source_item, target_item)
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
            self.TOSPN.remove_place(place)
    
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
            self.TOSPN.remove_transition(transition)
    
    def empty_self(self):
        """Clear all graphical elements and reset the TOSPN model."""
        # Remove all outputs and events
        for output in list(self.TOSPN.outputs.values()):
            self.TOSPN.remove_output(output)
        
        for event in list(self.TOSPN.events.values()):
            if event.name != "λ":  # Keep the lambda event
                self.TOSPN.remove_event(event)
        
        # Remove all transitions and places
        for transition in list(self.TOSPN.transitions.values()):
            self.remove_transition(transition)
        
        for place in list(self.TOSPN.places.values()):
            self.remove_place(place)
        
        # Create a new TOSPN instance
        self.TOSPN = TOSPN()
        self.scene.set_TOSPN(self.TOSPN)
        
        # Reconnect property editors
        self.scene.parent.event_property_editor.set_TOSPN(self.TOSPN)
        self.scene.parent.output_property_editor.set_TOSPN(self.TOSPN)
    
    def save(self, file_path):
        """Save the TOSPN model to a file."""
        save_dic = self.TOSPN.to_dict()
        
        # Add graphical information
        for place_id, place in self.TOSPN.places.items():
            if place in self.place_to_graph_place:
                graph_place = self.place_to_graph_place[place]
                save_dic["places"][place_id]["pos_x"] = graph_place.pos().x()
                save_dic["places"][place_id]["pos_y"] = graph_place.pos().y()
        
        for transition_id, transition in self.TOSPN.transitions.items():
            if transition in self.transition_to_graph_transition:
                graph_transition = self.transition_to_graph_transition[transition]
                save_dic["transitions"][transition_id]["pos_x"] = graph_transition.pos().x()
                save_dic["transitions"][transition_id]["pos_y"] = graph_transition.pos().y()
                save_dic["transitions"][transition_id]["orientation"] = graph_transition.orientation
        
        with open(file_path, 'w') as json_file:
            json.dump(save_dic, json_file, indent=4)
    
    def load(self, file_path):
        """Load a TOSPN model from a file."""
        self.empty_self()
        
        with open(file_path, 'r') as json_file:
            save_dic = json.load(json_file)
            
            # Load the model
            loaded_tospn = TOSPN.from_dict(save_dic)
            
            # Update our TOSPN reference
            self.scene.set_TOSPN(loaded_tospn)
            self.TOSPN = loaded_tospn
            
            # Reconnect property editors
            self.scene.parent.event_property_editor.set_TOSPN(loaded_tospn)
            self.scene.parent.output_property_editor.set_TOSPN(loaded_tospn)
            
            # Create graphical representations
            for place in self.TOSPN.places.values():
                place_data = next(p for p in save_dic["places"] if p["id"] == place.id)
                self.add_place(place, place_data.get("pos_x", 0), place_data.get("pos_y", 0))
            
            for transition in self.TOSPN.transitions.values():
                transition_data = next(t for t in save_dic["transitions"] if t["id"] == transition.id)
                self.add_transition(
                    transition,
                    transition_data.get("pos_x", 0),
                    transition_data.get("pos_y", 0),
                    transition_data.get("orientation", 0)
                )
            
            # Create arcs after all places and transitions exist
            for arc in self.TOSPN.arcs.values():
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



class GraphPlaceItem(DraggableItem):
    def __init__(self, place, x, y):
        """Initialize a graphical place item."""
        self.place_radius = 15
        super().__init__(x, y)
        self.place = place
        
        self.boundingRectValue = QRectF(-self.place_radius - 10, -self.place_radius - 10, 2 * self.place_radius + 20, 2 * self.place_radius + 20)
        
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
        painter.drawEllipse(-self.place_radius, -self.place_radius, 2*self.place_radius, 2*self.place_radius)  # Draw the node as a circle
        
        # Draw token number
        painter.setPen(QPen(self.token_color))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.place.token_number))
    
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



class GraphTransitionItem(DraggableItem):
    def __init__(self, transition, x, y, orientation=0):
        super().__init__(x, y)
        self.transition = transition
        if orientation == 0:
            self.L = 30
            self.l = 7.5
        else:
            self.L = 7.5
            self.l = 30
        self.orientation = orientation

        self.boundingRectValue = QRectF(-(self.L/2) -5, -(self.l/2) - 5, (self.L)+ 10, (self.l) + 10)
        self.setPos(x, y)

        self.drag_text = DraggableTextItem("",self)  # Note: The text item is a child of CustomItem
        self.drag_text.updateText("{}\n{}\n{}".format(self.transition.name,
                                                     self.transition.event.name if self.transition.event else "",
                                                     str(self.transition.timing_interval)))
        self.pend_width = 1
        self.set_color(0, 0, 0)
        self.line = []
        self.is_selected = False
        self.defaultZvalue = 1
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        
        # Add as listener to the transition
        self.transition.add_listener(self)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(0,0,0)))
        self.pen = QPen(self.color)
        self.pen.setWidth(self.pend_width)
        painter.setPen(QPen(self.pen))
        painter.drawRect(QRectF(-self.L/2, -self.l/2, self.L, self.l))

    def on_change(self, subject, event_type, data):
        """Handle changes in the transition model."""
        if event_type == "name_changed":
            self.drag_text.updateText("{}\n{}\n{}".format(
                self.transition.name,
                self.transition.event.name if self.transition.event else "",
                str(self.transition.timing_interval)))
        elif event_type == "event_changed":
            self.drag_text.updateText("{}\n{}\n{}".format(
                self.transition.name,
                data["new"].name if data["new"] else "",
                str(self.transition.timing_interval)))
        elif event_type == "timing_changed":
            self.drag_text.updateText("{}\n{}\n{}".format(
                self.transition.name,
                self.transition.event.name if self.transition.event else "",
                str(self.transition.timing_interval)))
        elif event_type == "event_name_changed":
            self.drag_text.updateText("{}\n{}\n{}".format(
                self.transition.name,
                data["new"] if data["new"] else "",
                str(self.transition.timing_interval)))

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
                self.boundingRectValue = QRectF(-((self.L+self.l) / 2) - 5, -((self.l+self.L) / 2) - 5, (self.L+self.l) + 10, (self.l+self.L) + 10)
                
                # Update all connected arcs
                for line in self.line:
                    line.updateLine()
                
                # Update scene
                if self.scene():
                    self.scene().update()
                self.update()

    def change_name(self,new_name):
        self.transition.name = new_name
        self.drag_text.updateText("{}\n{}\n{}".format(self.transition.name,self.transition.event.name,str(self.transition.timing_interval)))

    def change_event(self,new_event):
        self.transition.change_event(new_event)
        self.drag_text.updateText("{}\n{}\n{}".format(self.transition.name,self.transition.event.name,str(self.transition.timing_interval)))

    def change_clock_1(self,clock_1):
        self.transition.timing_interval[0] = clock_1
        self.drag_text.updateText("{}\n{}\n{}".format(self.transition.name,self.transition.event.name,str(self.transition.timing_interval)))
    def change_clock_2(self, clock_2):
        self.transition.timing_interval[1]=clock_2
        self.drag_text.updateText("{}\n{}\n{}".format(self.transition.name,self.transition.event.name,str(self.transition.timing_interval)))



class GraphArcItem(QGraphicsLineItem):
    def __init__(self, arc, node1, node2):
        super().__init__()

        self.arc = arc
        self.head_size = 15
        self.node1 = node1
        self.node2 = node2
        node1.line.append(self)
        node2.line.append(self)
        
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
        
        self.updateLine()

    def startTextDrag(self, event):
        """Called when text dragging starts to calculate initial offset."""
        mid_x = (self.line().p1().x() + self.line().p2().x()) / 2
        mid_y = (self.line().p1().y() + self.line().p2().y()) / 2
        self.text_offset_x = self.weight_text.pos().x() - mid_x
        self.text_offset_y = self.weight_text.pos().y() - mid_y
        # Call original mousePressEvent
        super(DraggableTextItem, self.weight_text).mousePressEvent(event)

    def endTextDrag(self, event):
        """Called when text dragging ends to update final offset."""
        mid_x = (self.line().p1().x() + self.line().p2().x()) / 2
        mid_y = (self.line().p1().y() + self.line().p2().y()) / 2
        self.text_offset_x = self.weight_text.pos().x() - mid_x
        self.text_offset_y = self.weight_text.pos().y() - mid_y
        # Call original mouseReleaseEvent
        super(DraggableTextItem, self.weight_text).mouseReleaseEvent(event)

    def updateLine(self):
        # Get positions of nodes
        p1 = self.node1.scenePos()
        p2 = self.node2.scenePos()
        
        # Calculate line vector
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = (dx*dx + dy*dy)**0.5
        
        if length == 0:
            return
            
        # Normalize vector
        dx /= length
        dy /= length
        
        # Adjust start and end points to node boundaries
        if isinstance(self.node1, GraphPlaceItem):
            p1 = QPointF(p1.x() + dx*self.node1.place_radius, p1.y() + dy*self.node1.place_radius)
        else:  # TransitionItem
            # Calculate intersection with rectangle
            angle = math.atan2(dy, dx)
            if abs(math.cos(angle)) * self.node1.L > abs(math.sin(angle)) * self.node1.l:
                # Intersects with vertical edge
                tx = math.copysign(self.node1.L/2, dx)
                ty = (dy/dx) * tx if dx != 0 else math.copysign(self.node1.l/2, dy)
                if abs(ty) > self.node1.l/2:
                    ty = math.copysign(self.node1.l/2, ty)
                    tx = (dx/dy) * ty if dy != 0 else math.copysign(self.node1.L/2, dx)
            else:
                # Intersects with horizontal edge
                ty = math.copysign(self.node1.l/2, dy)
                tx = (dx/dy) * ty if dy != 0 else math.copysign(self.node1.L/2, dx)
                if abs(tx) > self.node1.L/2:
                    tx = math.copysign(self.node1.L/2, tx)
                    ty = (dy/dx) * tx if dx != 0 else math.copysign(self.node1.l/2, dy)
            p1 = QPointF(p1.x() + tx, p1.y() + ty)
        
        if isinstance(self.node2, GraphPlaceItem):
            p2 = QPointF(p2.x() - dx*self.node2.place_radius, p2.y() - dy*self.node2.place_radius)
        else:  # TransitionItem
            # Calculate intersection with rectangle
            angle = math.atan2(dy, dx)
            if abs(math.cos(angle)) * self.node2.L > abs(math.sin(angle)) * self.node2.l:
                # Intersects with vertical edge
                tx = math.copysign(self.node2.L/2, dx)
                ty = (dy/dx) * tx if dx != 0 else math.copysign(self.node2.l/2, dy)
                if abs(ty) > self.node2.l/2:
                    ty = math.copysign(self.node2.l/2, ty)
                    tx = (dx/dy) * ty if dy != 0 else math.copysign(self.node2.L/2, dx)
            else:
                # Intersects with horizontal edge
                ty = math.copysign(self.node2.l/2, dy)
                tx = (dx/dy) * ty if dy != 0 else math.copysign(self.node2.L/2, dx)
                if abs(tx) > self.node2.L/2:
                    tx = math.copysign(self.node2.L/2, tx)
                    ty = (dy/dx) * tx if dx != 0 else math.copysign(self.node2.l/2, dy)
            p2 = QPointF(p2.x() - tx, p2.y() - ty)
        
        # Update line position
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        
        # Calculate middle point
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        
        # Update text position using stored offset
        text_x = mid_x + self.text_offset_x
        text_y = mid_y + self.text_offset_y
        self.weight_text.setPos(text_x - self.weight_text.boundingRect().width()/2,
                              text_y - self.weight_text.boundingRect().height()/2)

    def paint(self, painter, option, widget):
        # Draw the main line
        pen = QPen(self.color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.line())

        # Draw arrow head
        line = self.line()
        if line.length() == 0:
            return
        
        angle = math.atan2(line.dy(), line.dx())
        arrow_p1 = line.p2()
        
        # Calculate arrow points for larger head
        arrow_p2 = QPointF(
            arrow_p1.x() - self.head_size * math.cos(angle - math.pi/6),
            arrow_p1.y() - self.head_size * math.sin(angle - math.pi/6)
        )
        arrow_p3 = QPointF(
            arrow_p1.x() - self.head_size * math.cos(angle + math.pi/6),
            arrow_p1.y() - self.head_size * math.sin(angle + math.pi/6)
        )

        # Draw the filled arrow head
        arrow_head = QPolygonF([arrow_p1, arrow_p2, arrow_p3])
        painter.setBrush(QBrush(self.color))
        painter.drawPolygon(arrow_head)

    def shape(self):
        # Create a path that includes both the line and arrow head
        path = QPainterPath()
        line = self.line()
        
        # Calculate arrow head points
        angle = math.atan2(line.dy(), line.dx())
        arrow_p1 = line.p2()
        arrow_p2 = QPointF(
            arrow_p1.x() - self.head_size * math.cos(angle - math.pi/6),
            arrow_p1.y() - self.head_size * math.sin(angle - math.pi/6)
        )
        arrow_p3 = QPointF(
            arrow_p1.x() - self.head_size * math.cos(angle + math.pi/6),
            arrow_p1.y() - self.head_size * math.sin(angle + math.pi/6)
        )
        
        # Add a thin strip along the line for selection
        normal_x = -math.sin(angle) * 3  # 3 pixels padding
        normal_y = math.cos(angle) * 3
        
        # Add line path
        path.moveTo(line.p1().x() + normal_x, line.p1().y() + normal_y)
        path.lineTo(line.p2().x() + normal_x, line.p2().y() + normal_y)
        path.lineTo(line.p2().x() - normal_x, line.p2().y() - normal_y)
        path.lineTo(line.p1().x() - normal_x, line.p1().y() - normal_y)
        path.closeSubpath()
        
        # Add arrow head path
        path.moveTo(arrow_p1.x(), arrow_p1.y())
        path.lineTo(arrow_p2.x(), arrow_p2.y())
        path.lineTo(arrow_p3.x(), arrow_p3.y())
        path.closeSubpath()
        
        return path

    def on_change(self, subject, event_type, data):
        """Handle changes in the arc model."""
        if event_type == "weight_changed":
            self.weight_text.updateText(str(data))
            self.weight_text.setDefaultTextColor(self.color)
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



class TempGraphLine(QGraphicsLineItem):
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