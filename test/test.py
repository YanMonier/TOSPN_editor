import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem


class MyGraphicsScene(QGraphicsScene):
    def mousePressEvent(self, event):
        # Get the QGraphicsView rendering this scene
        graphics_view = self.views()[0]

        # Convert mouse position from view to scene coordinates
        scene_pos = graphics_view.mapToScene(event.pos().toPoint())
        print(f"Mouse clicked at scene position: ({scene_pos.x()}, {scene_pos.y()})")

        # Add a marker (optional, to visualize the click)
        self.addEllipse(scene_pos.x() - 5, scene_pos.y() - 5, 10, 10)

        super().mousePressEvent(event)


def main():
    app = QApplication(sys.argv)

    # Create scene and view
    scene = MyGraphicsScene()
    scene.setSceneRect(0, 0, 800, 600)

    view = QGraphicsView(scene)
    view.setScene(scene)
    view.setGeometry(100, 100, 800, 600)

    # Show the view
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()