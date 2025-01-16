
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsTextItem,QGraphicsLineItem
from PySide2.QtGui import QBrush, QColor, QPen,  QPainterPath, QTransform, QPolygonF, QPainterPathStroker
from PySide2.QtCore import Qt, QRectF, QPointF

from gui.widgets.widgets import DraggableItem, DraggableTextItem

import math
import json

from tools.TOSPN import TOSPN, Output, Place, Event, Transition, Arc
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
    def __init__(self,scene,TOSPN):
        self.scene=scene
        self.TOSPN=TOSPN

        self.place_counter=0
        self.transition_counter=0
        self.arc_counter=0

        self.arcToGraphArcDic={}
        self.transitionToGraphTransitionDic = {}
        self.placeToGraphPlaceDic = {}

    def add_place(self, place, x, y):
        # Add a graphical item for the place
        place_graph_item = GraphPlaceItem(place, x, y)
        place.graphic_place = place_graph_item
        # Increment the place ID for the next place
        self.place_counter += 1
        self.scene.addItem(place_graph_item)

        self.placeToGraphPlaceDic[place]=place_graph_item
        place_graph_item.setFlag(QGraphicsItem.ItemIsMovable)


    def add_transition(self, transition, x, y, orientation=0):

        # Add a graphical item for the edge
        self.transition_counter += 1
        transition_graph_item = GraphTransitionItem(transition, x, y,orientation)
        self.scene.addItem(transition_graph_item)
        transition.graphic_transition = transition_graph_item
        transition_graph_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.transitionToGraphTransitionDic[transition] = transition_graph_item

    def add_arc(self, arc, object_1, object_2):

        # Add a graphical item for the edge
        self.arc_counter += 1
        arc_graph_item = GraphArcItem(arc, object_1, object_2)
        arc.graphic_arc = arc_graph_item
        self.scene.addItem(arc_graph_item)
        arc_graph_item.setZValue(-100)
        self.arcToGraphArcDic[arc] = arc_graph_item

    # transition_graph_item.setFlag(QGraphicsItem.ItemIsMovable)

    def remove_arc(self, arc):

        arc_graph_item = self.arcToGraphArcDic[arc]
        self.scene.removeItem(arc_graph_item)

        self.arc_counter -= 1

        del self.scene.arc_history[arc_graph_item.node1][arc_graph_item.node2]
        del self.arcToGraphArcDic[arc]

        arc.remove()

    def remove_place(self, place):


        for arc in place.next_arc_list.copy():
            self.remove_arc(arc)
        for arc in place.previous_arc_list.copy():
            self.remove_arc(arc)

        place_graph_item=self.placeToGraphPlaceDic[place]
        self.scene.removeItem(place_graph_item)

        self.place_counter -= 1

        del self.placeToGraphPlaceDic[place]
        place.remove()

    def remove_transition(self, transition):
        for arc in transition.next_arc_list.copy():
            self.remove_arc(arc)
        for arc in transition.previous_arc_list.copy():
            self.remove_arc(arc)

        transition_graph_item=self.transitionToGraphTransitionDic[transition]
        self.scene.removeItem(transition_graph_item)
        self.transition_counter -= 1

        del self.transitionToGraphTransitionDic[transition]
        transition.remove()


    def empty_self(self):
        for output_id in list(self.TOSPN.outputDic.keys()).copy():
            self.TOSPN.outputDic[output_id].remove()
        for event_id in list(self.TOSPN.eventDic.keys()).copy():
            self.TOSPN.eventDic[event_id].remove()
        for transition_id in list(self.TOSPN.transitionDic.keys()).copy():
            self.remove_transition(self.TOSPN.transitionDic[transition_id])
        for place_id in list(self.TOSPN.placeDic.keys()).copy():
            self.remove_place(self.TOSPN.placeDic[place_id])

        self.scene.parent.event_property_editor.reset_self()
        self.scene.parent.output_property_editor.reset_self()

        Place.place_id=0
        Transition.transition_id=0
        Event.event_id=0
        Arc.arc_id=0
        Output.output_id=0

        self.TOSPN.add_Event("λ")


    def save(self,file_path):
        save_dic={
            "general_info":{},
            "transition":{},
            "place":{},
            "arc":{},
            "output":{},
            "event":{}
        }

        for arc_id in self.TOSPN.arcDic.keys():
            arc_dic={}
            arc=self.TOSPN.arcDic[arc_id]
            arc_dic["elem1_type"]=arc.previous_element.type
            arc_dic["elem1_id"] =arc.previous_element.id
            arc_dic["elem2_type"] = arc.next_element.type
            arc_dic["elem2_id"] = arc.next_element.id
            arc_dic["weight"]=arc.weight
            arc_dic["id"] = arc.id

            save_dic["arc"][arc_id]=arc_dic

        for transition_id in self.TOSPN.transitionDic.keys():
            transition_dic={}
            transition=self.TOSPN.transitionDic[transition_id]
            transition_dic["name"]=transition.name
            transition_dic["time1"] =transition.timing_interval[0]
            transition_dic["time2"] = transition.timing_interval[1]
            transition_dic["event_id"] = transition.event.id
            transition_dic["pos_x"] = self.transitionToGraphTransitionDic[transition].pos().x()
            transition_dic["pos_y"] = self.transitionToGraphTransitionDic[transition].pos().y()
            transition_dic["orientation"] = self.transitionToGraphTransitionDic[transition].orientation
            transition_dic["id"] = transition.id

            save_dic["transition"][transition_id]=transition_dic


        for place_id in self.TOSPN.placeDic.keys():
            place_dic={}
            place=self.TOSPN.placeDic[place_id]
            place_dic["name"] = place.name
            place_dic["token"] = place.token_number
            place_dic["pos_x"] = self.placeToGraphPlaceDic[place].pos().x()
            place_dic["pos_y"] = self.placeToGraphPlaceDic[place].pos().y()
            place_dic["id"] = place.id

            save_dic["place"][place_id]=place_dic

        for output_id in self.TOSPN.outputDic.keys():
            output_dic={}
            output=self.TOSPN.outputDic[output_id]
            output_dic["name"]=output.name
            output_dic["math_expression"]=output.math_marking_expression
            output_dic["txt_expression"]=output.txt_marking_expression
            output_dic["id"] = output.id

            save_dic["output"][output_id] = output_dic

        for event_id in self.TOSPN.eventDic.keys():
            event_dic={}
            event=self.TOSPN.eventDic[event_id]
            event_dic["name"]=event.name
            event_dic["id"] = event.id

            save_dic["event"][event_id] = event_dic

        save_dic["general_info"]["place_id_num"]=Place.place_id
        save_dic["general_info"]["transition_id_num"] = Transition.transition_id
        save_dic["general_info"]["arc_id_num"] = Arc.arc_id
        save_dic["general_info"]["event_id_num"] = Event.event_id
        save_dic["general_info"]["output_id_num"] = Output.output_id


        with open(file_path, 'w') as json_file:
            json.dump(save_dic, json_file, indent=4)

    def load(self, file_path):

        self.empty_self()
        with open(file_path, 'r') as json_file:
            save_dic = json.load(json_file)

            Place.place_id = save_dic["general_info"]["place_id_num"]
            Transition.transition_id = save_dic["general_info"]["transition_id_num"]
            Event.event_id = save_dic["general_info"]["event_id_num"]
            Arc.arc_id = save_dic["general_info"]["arc_id_num"]
            Output.output_id = save_dic["general_info"]["output_id_num"]

            for event_id in save_dic["event"].keys():
                if event_id != "0":
                    self.scene.parent.event_property_editor.load_item(save_dic["event"][event_id])

            for place_id in save_dic["place"].keys():
                place=self.TOSPN.add_Place(save_dic["place"][place_id])
                self.add_place(place,save_dic["place"][place_id]["pos_x"],save_dic["place"][place_id]["pos_y"])

            for transition_id in save_dic["transition"].keys():
                transition=self.TOSPN.add_Transition(save_dic["transition"][transition_id])
                self.add_transition(transition,save_dic["transition"][transition_id]["pos_x"],save_dic["transition"][transition_id]["pos_y"])

            for arc_id in save_dic["arc"].keys():

                if save_dic["arc"][arc_id]["elem1_type"]=="place":
                    element1_id=save_dic["arc"][arc_id]["elem1_id"]
                    element2_id = save_dic["arc"][arc_id]["elem2_id"]
                    elem1=self.TOSPN.placeDic[element1_id]
                    elem2=self.TOSPN.transitionDic[element2_id]
                    arc=self.TOSPN.add_Arc(elem1,elem2)

                    obj1=self.placeToGraphPlaceDic[elem1]
                    obj2=self.transitionToGraphTransitionDic[elem2]
                    self.add_arc(arc,obj1,obj2)
                else:
                    element1_id = save_dic["arc"][arc_id]["elem1_id"]
                    element2_id = save_dic["arc"][arc_id]["elem2_id"]
                    elem1 = self.TOSPN.transitionDic[element1_id]
                    elem2 = self.TOSPN.placeDic[element2_id]
                    arc = self.TOSPN.add_Arc(elem1, elem2)

                    obj1 = self.transitionToGraphTransitionDic[elem1]
                    obj2 = self.placeToGraphPlaceDic[elem2]
                    self.add_arc(arc, obj1, obj2)

            for output_id in save_dic["output"].keys():
                self.scene.parent.output_property_editor.load_item(save_dic["output"][output_id])



class GraphPlaceItem(DraggableItem):
    def __init__(self, place, x, y):
        super().__init__()
        self.place=place
        self.setPos(x, y)



        self.drag_text =DraggableTextItem(self)  # Note: The text item is a child of CustomItem
        self.drag_text.updateText(self.place.name)

        self.place_radius=15
        self.num_nodes = 8  # Number of nodes to draw around the place


        self.boundingRectValue=QRectF(-self.place_radius - 10, -self.place_radius - 10, 2 * self.place_radius + 20, 2 * self.place_radius + 20)
        self.color=QColor(0,0,0)
        self.token_color=QColor(0,0,0)
        self.pend_width=1
        self.line=[]
        self.is_selected=False
        self.defaultZvalue = 1

    def shape(self):
        """Define the hover-sensitive area as a smaller ellipse."""
        path = QPainterPath()
        path.addEllipse(-self.place_radius -4, -self.place_radius-4, 2 * self.place_radius + 8 , 2 * self.place_radius +8)
        return path

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(255,255,255)))
        self.pen=QPen(self.color)
        self.pen.setWidth(self.pend_width)
        painter.setPen(QPen(self.pen))
        painter.drawEllipse(-self.place_radius, -self.place_radius, 2*self.place_radius, 2*self.place_radius)  # Draw the node as a circle

        painter.setPen(QPen(self.token_color))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.place.token_number))  # Draw the node id


    def set_color(self, r,g,b):
        """Method to change the color dynamically."""
        self.color = QColor(r,g,b)  # Update the color
        self.drag_text.set_color(r,g,b)
        self.update()  # Request a repaint to apply the new color

    def updatetext(self):
        painter.drawEllipse(self.boundingRect())  # Draw the node as a circle
        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.place_id))  # Draw the node id


    def selected(self):
        self.is_selected=True
        self.set_color(0,0, 255)
        self.pend_width = 4
        self.update()

    def unselected(self):
        self.is_selected = False
        self.set_color(0, 0, 0)
        self.pend_width = 1
        self.update()


    def select(self):
        if self.is_selected==False:
            self.set_color(255,0,0)
            self.pend_width=4
        self.update()


    def unselect(self):
        if self.is_selected==False:
            self.set_color(0, 0, 0)
            self.pend_width=1
            self.update()


    def mouseMoveEvent(self, event):
        #print(f"Mouse moved to {self.place.id}")
        for line in self.line:
            line.updateLine()
        super().mouseMoveEvent(event)  # Always call the base class method

    def change_name(self,new_name):
        self.place.change_name(new_name)
        self.drag_text.updateText(self.place.name)

    def resetZvalue(self):
        self.setZValue(self.defaultZvalue)
    '''
    def remove(self):
        self.place.remove()
    '''



class GraphTransitionItem(DraggableItem):
    def __init__(self, transition, x, y, orientation=0):
        super().__init__()
        self.transition=transition
        if orientation == 0:
            self.L=30
            self.l=7.5
        else:
            self.L = 7.5
            self.l = 30
        self.orientation=orientation

        self.boundingRectValue = QRectF(-(self.L/2) -5, -(self.l/2) - 5, (self.L)+ 10, (self.l) + 10)
        self.setPos(x, y)

        self.drag_text = DraggableTextItem(self)  # Note: The text item is a child of CustomItem
        self.drag_text.updateText("{}\n{}\n{}".format(self.transition.name,self.transition.event.name,str(self.transition.timing_interval)))
        self.pend_width=1
        self.set_color(0,0,0)
        self.line = []
        self.is_selected=False
        self.defaultZvalue = 1
        self.setFlag(QGraphicsItem.ItemIsFocusable)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(0,0,0)))
        self.pen = QPen(self.color)
        self.pen.setWidth(self.pend_width)
        painter.setPen(QPen(self.pen))

        painter.drawRect(QRectF(-self.L/2, -self.l/2, self.L, self.l))
        #painter.drawText(QRectF(-2.5, -2.5, 20, 5), Qt.AlignCenter, str(self.transition.id))  # Draw the node id


    def set_color(self, r,g,b):
        """Method to change the color dynamically."""
        self.color = QColor(r,g,b)  # Update the color
        self.drag_text.set_color(r,g,b)
        self.update()  # Request a repaint to apply the new color

    def updatetext(self):
        painter.drawEllipse(self.boundingRect())  # Draw the node as a circle
        #painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.node_id))  # Draw the node id

    def updatePosition(self, new_position):
        # Update the position of the parent (rectangle), and the child (text) moves automatically
        self.setPos(new_position)

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
        #print(f"Mouse moved to {self.place.id}")
        for line in self.line:
            line.updateLine()
        super().mouseMoveEvent(event)  # Always call the base class method

    def resetZvalue(self):
        self.setZValue(self.defaultZvalue)
    '''
    def remove(self):
        self.transition.remove()
    '''

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

    def keyPressEvent(self, event):
        print("key")
        if event.key() == Qt.Key_R:
            if self.is_selected==True:
                if self.orientation==0:
                    self.orientation = 1
                else:
                    self.orientation = 0
                old_L=self.L
                self.L = self.l
                self.l = old_L
                self.boundingRectValue = QRectF(-((self.L+self.l) / 2) - 5, -((self.l+self.L) / 2) - 5, (self.L+self.l) + 10, (self.l+self.L) + 10)
                self.update()



class GraphArcItem(QGraphicsLineItem):
    def __init__(self, arc, node1, node2):
        super().__init__()

        self.arc=arc
        self.head_size = 15


        self.node1 = node1
        self.node2 = node2
        node1.line.append(self)
        node2.line.append(self)
        pen = QPen(QColor("black"))
        self.setPen(pen)
        # Update the line whenever the points move
        self.updateLine()
        self.color=QColor(0,0,0)
        self.is_selected=False
        self.margin=10
        self.defaultZvalue=0
        self.mid_point = QPointF(0, 0)

    def updateLine(self):
        # Set the line to connect the two points
        line = QPointF(self.node1.x(), self.node1.y()), QPointF(self.node2.x(), self.node2.y())
        self.setLine(line[0].x(), line[0].y(), line[1].x(), line[1].y())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Recalculate the line whenever either point moves
            self.updateLine()

        return super().itemChange(change, value)

    def set_color(self, r, g, b):
        """Method to change the color dynamically."""
        self.color = QColor(r, g, b)  # Update the color
        self.update()  # Request a repaint to apply the new color

    def paint(self, painter, option, widget):
        # Draw the main line using the base class paint method
        pen = QPen(self.color)
        pen.setWidth(2)
        painter.setPen(pen)
        super().paint(painter, option, widget)

        # Calculate the mid-point of the line
        line = self.line()
        start = line.p1()
        end = line.p2()

        line_length = math.sqrt((end.x() - start.x()) ** 2 + (end.y() - start.y()) ** 2)
        dx = (end.x() - start.x()) / line_length
        dy = (end.y() - start.y()) / line_length

        mid_x = (start.x() + end.x()) / 2 - dx*self.head_size/4
        mid_y = (start.y() + end.y()) / 2 - dy*self.head_size/4
        self.mid_point = QPointF(mid_x, mid_y)

        line_length = math.sqrt((end.x() - start.x()) ** 2 + (end.y() - start.y()) ** 2)
        dx = (end.x() - start.x()) / line_length
        dy = (end.y() - start.y()) / line_length

        # Calculate the angle of the line
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())

        # Calculate the two points of the arrowhead at the mid-point
        arrow_point1 = QPointF(
            self.mid_point.x() - self.head_size * math.cos(angle - math.pi / 6),
            self.mid_point.y() - self.head_size * math.sin(angle - math.pi / 6)
        )
        arrow_point2 = QPointF(
            self.mid_point.x() - self.head_size * math.cos(angle + math.pi / 6),
            self.mid_point.y() - self.head_size * math.sin(angle + math.pi / 6)
        )

        # Draw the arrowhead at the mid-point as a filled triangle
        arrow_head = QPolygonF([self.mid_point, arrow_point1, arrow_point2])
        painter.setBrush(QBrush(self.color))
        painter.drawPolygon(arrow_head)

    def boundingRect(self):
        # Get the line's bounding rectangle
        line = self.line()
        base_rect = super().boundingRect()
        # Extend the bounding rect to include the arrowhead
        extra = self.head_size
        return base_rect.adjusted(-extra, -extra, extra, extra)

    def shape(self):

        """
        # Create a QPainterPath for the line's selection area
        path = QPainterPath()

        # Get the line's coordinates
        line = self.line()

        # Add the line to the QPainterPath
        path.moveTo(line.p1())
        path.lineTo(line.p2())

        # Now expand the path to create a wider selection area along the line
        stroker = QPainterPathStroker()
        stroker.setWidth(self.pen().width() + self.margin * 2)  # Increase the stroke width

        # Apply the stroker to the path, effectively creating a wider selection area
        expanded_path = stroker.createStroke(path)
        return expanded_path

        """
        line = self.line()
        path = QPainterPath()
        path.moveTo(line.p1())
        path.lineTo(line.p2())

        start = line.p1()
        end = line.p2()
        line_length = math.sqrt((end.x() - start.x()) ** 2 + (end.y() - start.y()) ** 2)
        dx = (end.x() - start.x()) / line_length
        dy = (end.y() - start.y()) / line_length
        mid_x = (start.x() + end.x()) / 2 - dx * self.head_size / 4 - dx * self.head_size/2
        mid_y = (start.y() + end.y()) / 2 - dy * self.head_size / 4 - dy * self.head_size/2
        mid_point_2=QPointF(mid_x, mid_y)

        # Draw a circle (or another shape) around the arrowhead to represent the selection area
        path.addEllipse(mid_point_2, self.head_size , self.head_size)

        return path

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

    def resetZvalue(self):
        self.setZValue(self.defaultZvalue)
    '''
    def remove(self):
        self.arc.remove()
    '''



class TempGraphLine(QGraphicsLineItem):
    def __init__(self, pos1, pos2):
        super().__init__()
        self.pos1 = pos1
        self.pos2 = pos2
        pen = QPen(QColor("black"))
        self.setPen(pen)
        # Update the line whenever the points move
        self.updateLine()

    def updateLine(self):
        # Set the line to connect the two points
        line = QPointF(self.pos1.x(), self.pos1.y()), QPointF(self.pos2.x(), self.pos2.y())
        self.setLine(line[0].x(), line[0].y(), line[1].x(), line[1].y())

    def update_pos(self,pos1,pos2):
        self.pos1 = pos1
        self.pos2 = pos2
        self.updateLine()