import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
import sys


from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Create and display the main window
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())