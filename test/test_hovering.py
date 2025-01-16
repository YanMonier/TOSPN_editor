import sys
from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QColor, QPainter
from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem


class HoverGraphicsItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.normal_color = QColor("blue")
        self.hover_color = QColor("red")
        self.setBrush(self.normal_color)


class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_item = None  # Keep track of the last item that was hovered over

    def mouseMoveEvent(self, event):
        print("move")
        # Get the item under the mouse cursor
        super().mouseMoveEvent(event)


class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        scene = CustomGraphicsScene(self)
        self.setScene(scene)

        # Enable mouse tracking so mouseMoveEvent is always triggered
        self.setMouseTracking(True)  # Enable mouse tracking

        # Create a graphics item




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
