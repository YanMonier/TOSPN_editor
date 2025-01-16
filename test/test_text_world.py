from PySide2.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QPushButton
from PySide2.QtCore import Qt

app = QApplication([])

# Create a main window
window = QWidget()
window.setWindowTitle("QLabel Word Wrap in Layout Example")



# Create a layout and add the label to it
layout = QHBoxLayout(window)


# Editable value field (read-only)
value_label = QLabel("teste steste st stest estes testestes tes test see")
value_label.setWordWrap(True)  # Ensure text wraps
value_label.setMaximumWidth(50)  # You can adjust the width here as needed

layout.addWidget(value_label)
layout.setAlignment(value_label, Qt.AlignLeft)
layout.setContentsMargins(0, 0, 0, 0)  # Left, Top, Right, Bottom margins
layout.setSpacing(0)

# Remove button
remove_button = QPushButton("-")
remove_button.setFixedSize(50, 20)
layout.addWidget(remove_button)


# Show the window

window.resize(300, 100)
window.show()

app.exec_()