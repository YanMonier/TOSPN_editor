import sys
from PySide2.QtWidgets import QGraphicsTextItem, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen, QPainterPath, QFont, QFontMetrics

from PySide2.QtWidgets import (QVBoxLayout, QWidget, QLineEdit, QSpinBox, QPushButton, QColorDialog, QSplitter, QLabel)
from PySide2.QtCore import Qt


class DraggableItem(QGraphicsItem):
    def __init__(self,x,y,parent=None):
        super().__init__(parent)
        self.dragging=False
        #self.setFlag(QGraphicsItem.ItemIsMovable)  # Allow moving the item
        #self.setFlag(QGraphicsItem.ItemIsSelectable)  # Allow selecting the item
        #self.setFlag(QGraphicsItem.ItemIsFocusable)  # Allow focusing the item
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)  # Cache the item for better performance
        self.setAcceptHoverEvents(True)
        self.boundingRectValue= QRectF(0,0,0,0)
        self.setPos(x,y)

    def boundingRect(self):
        return self.boundingRectValue


    def mousePressEvent(self, event):
        # Optional: Handle press events (e.g., change color or do something on press)
        if event.button() == Qt.LeftButton and (self.scene().state=="move" or self.scene().state=="add_transition" or self.scene().state=="add_place" or self.scene().state=="add_event"):
            self.setFlag(QGraphicsItem.ItemIsMovable)
            self.setFlag(QGraphicsItem.ItemIsSelectable)
            self.setFlag(QGraphicsItem.ItemIsFocusable)
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        #self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        #print("cant move")
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Notify parent edge to update path on move
            if self.scene().isGridOn == True:
                #print(self.scene())
                # value is the new position (QPointF)
                GRID_SIZE = self.scene().grid_size
                new_pos = value
                # Snap to grid
                x = round(new_pos.x() / GRID_SIZE) * GRID_SIZE
                y = round(new_pos.y() / GRID_SIZE) * GRID_SIZE
                return QPointF(x, y)
            else:
                new_pos = value
                x = new_pos.x()
                y = new_pos.y()
                return QPointF(x, y)
        elif change == QGraphicsItem.ItemPositionHasChanged:
            self.update()

        return super().itemChange(change, value)


class DraggableTextItem(DraggableItem):
    def __init__(self, text, parent=None):
        super().__init__(0,0,parent)

        self.setPos(15,20)
        self.text=text
        self.font = QFont("Arial", 10)
        self.text_color = Qt.black

        self.boundingRectValue = QRectF()

        self.updateText(self.text)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.setAcceptHoverEvents(False)
        self.parent=parent
        self.updateText(self.text)



    def boundingRect(self):
        return self.boundingRectValue

    def paint(self, painter, option, widget=None):
        """
        Custom paint function to draw the text on multiple lines.
        """
        # Set brush and pen
        painter.setBrush(QBrush(Qt.transparent))  # No background fill
        painter.setPen(QPen(self.text_color))

        # Set font
        painter.setFont(self.font)

        # Draw the text line by line
        line_height = QFontMetrics(self.font).height()
        lines = self.text.split("\n")
        for i, line in enumerate(lines):
            painter.drawText(0, (i+1) * line_height, line)

    def updateText(self, new_text):
        """
        Update the text and recalculate the bounding rect dynamically.
        """
        self.text = new_text  # Update the stored text

        # Calculate the bounding rect based on the font and text
        line_height = QFontMetrics(self.font).height()
        lines = new_text.split("\n")

        metrics = QFontMetrics(self.font)
        text_width = max(metrics.horizontalAdvance(line) for line in lines)
        #text_width = max(QFontMetrics(self.font).width(line) for line in lines)
        text_height = line_height * len(lines)

        # Update the bounding rect to fit the full text
        self.prepareGeometryChange()  # Notify the scene of the change

        padding = 4  # ou 2 ou plus selon le rendu
        self.boundingRectValue = QRectF(0, 0, text_width + padding * 2, text_height + padding * 2)
        #self.boundingRectValue = QRectF(0, 0, text_width, text_height)

        # Trigger a repaint
        self.update()

    def set_color(self, r,g,b):
        """Method to change the color dynamically."""
        self.text_color = QColor(r,g,b)  # Update the color
        #print(self.boundingRectValue)
        self.update()  # Request a repaint to apply the new color


class DraggablePoint(QGraphicsEllipseItem):
    def __init__(self, x, y):
        super().__init__(-5, -5, 10, 10)  # Create a small circle with width and height of 10px
        self.setBrush(QBrush(QColor("red")))  # Set color of the point
        self.setPos(x, y)  # Set the initial position
        self.setFlag(QGraphicsItem.ItemIsMovable)  # Make the point draggable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.line=[]

    def boundingRect(self):
        return self.rect()  # Just return the bounding box of the ellipse

    def mouseMoveEvent(self, event):
        # Override mouseMoveEvent to update the line during the movement
        super().mouseMoveEvent(event)
        for line in self.line:
            line.updateLine()  # Update the line when the point moves


class LineBetweenPoints(QGraphicsLineItem):
    def __init__(self, point1, point2):
        super().__init__()
        self.point1 = point1
        self.point2 = point2
        point1.line.append(self)
        point2.line.append(self)
        pen = QPen(QColor("black"))
        self.setPen(pen)
        # Update the line whenever the points move
        self.updateLine()

    def updateLine(self):
        # Set the line to connect the two points
        line = QPointF(self.point1.x(), self.point1.y()), QPointF(self.point2.x(), self.point2.y())
        self.setLine(line[0].x(), line[0].y(), line[1].x(), line[1].y())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Recalculate the line whenever either point moves
            self.updateLine()

        return super().itemChange(change, value)

