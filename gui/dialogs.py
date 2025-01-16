from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QInputDialog
from PySide2.QtCore import Qt

class MessageDialog:
    def __init__(self, parent):
        self.parent = parent

    def show_message_dialog(self):
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Information")
        msg_box.setText("This is an informational message.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            print(f"Selected file: {file_path}")

    def show_input_dialog(self):
        text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter your name:")
        if ok:
            print(f"User entered: {text}")


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Dialog")
        self.setGeometry(100, 100, 300, 150)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Enter your name:", self)
        self.layout.addWidget(self.label)

        self.name_input = QLineEdit(self)
        self.layout.addWidget(self.name_input)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

    def get_name(self):
        return self.name_input.text()