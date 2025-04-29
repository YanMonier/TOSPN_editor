import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, QGraphicsScene, QGraphicsRectItem,QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
import sys
import os
import logging


from gui.main_window import MainWindow


if __name__ == "__main__":
    # Force stdout to be unbuffered
    sys.stdout.reconfigure(line_buffering=True)
    
    # Set up logging with immediate flush
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log', mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Replace print with logging.debug
    def print(*args, **kwargs):
        message = ' '.join(map(str, args))
        logging.debug(message)
        sys.stdout.flush()  # Force flush after each print
    
    app = QApplication(sys.argv)
    # Create and display the main window
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())