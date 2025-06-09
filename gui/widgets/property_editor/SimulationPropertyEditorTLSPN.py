import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, \
	QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QGroupBox
from PySide2.QtCore import QRectF, Qt, QPointF
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen
from PySide2.QtCore import QSize

from PySide2.QtWidgets import (QSizePolicy, QComboBox, QFrame, QListWidgetItem, QVBoxLayout, QWidget, QLineEdit,
							   QSpinBox, QPushButton, QColorDialog, QSplitter, QLabel, QHBoxLayout, QDoubleSpinBox,
							   QDialog, QListWidget, QDialogButtonBox, QSpacerItem, QScrollArea)
from PySide2.QtCore import Qt, Signal, QTime, QTimer
from gui.graphics.graphics_TLSPN import GraphPlaceItemTLSPN, GraphTransitionItemTLSPN, GraphArcItemTLSPN, \
	TempGraphLineTLSPN

from utils.other_utils import OutputParser


class SimulationPropertyEditorTLSPN(QWidget):
	def __init__(self):
		"""Initialize the output property editor."""
		super().__init__()
		self.setFixedWidth(300)
		self.widget_list = []

		self.timewidget = TimeControlWidget(self)
		self.logViewer = LogViewer()

		# Layout
		self.layout = QVBoxLayout(self)
		self.layout.setAlignment(Qt.AlignTop)

		self.layout.addWidget(self.timewidget)
		self.layout.addWidget(self.logViewer)
		# output list label

		# Current TLSPN reference
		self.TLSPN = None

	def set_TLSPN(self, TLSPN):
		"""Set the TLSPN model reference."""
		self.TLSPN = TLSPN
		self.TLSPN.add_listener(self)
		self.reset_simulation()

		# Add existing outputs
		for output in self.TLSPN.outputs.values():
			if output.name != ".":  # Don't show lambda output in the list
				self.add_to_list(output.name, output)

	def reset_self(self):
		"""Reset the entire editor."""
		self.TLSPN = None

	def reset_simulation(self):
		self.logViewer.clear_layout()
		self.TLSPN.reset_simulation()

	def on_change(self, subject, event_type, data):
		if event_type == "update_time":
			self.timewidget.set_time(data)

		elif event_type == "transition_enabled":
			log = ("ENABLE", str(data[0]), self.ms_to_str(data[1]))
			self.logViewer.add_log(log)

		elif event_type == "transition_disabled":
			log = ("DISABLE", str(data[0]), self.ms_to_str(data[1]))
			self.logViewer.add_log(log)

		elif event_type == "transition_activated":
			log = ("ACTIVATE", str(data[0]), self.ms_to_str(data[1]))
			self.logViewer.add_log(log)

		elif event_type == "transition_firable":
			log = ("FIRABLE", str(data[0]), self.ms_to_str(data[1]))
			self.logViewer.add_log(log)

		elif event_type == "transition_fired":
			log = ("FIRE", str(data[0]), self.ms_to_str(data[1]))
			self.logViewer.add_log(log)

	def ms_to_str(self, ms):
		hours = (ms // (3600 * 1000)) % 24  # keep within 24h if you want
		minutes = (ms // (60 * 1000)) % 60
		seconds = (ms // 1000) % 60
		milliseconds = ms % 1000
		return QTime(hours, minutes, seconds, milliseconds).toString("HH:mm:ss.zzz")


class TimeControlWidget(QWidget):
	def __init__(self, simulation_editor):
		super().__init__()

		self.simulation_editor = simulation_editor
		self.time = QTime(0, 0, 0, 0)  # Start time at 00:00

		# Buttons
		self.step_button = QPushButton("▶")
		self.jump_button = QPushButton("▶▶")

		button_size = 40  # pixels
		for button in [self.step_button, self.jump_button]:
			button.setFixedSize(button_size, button_size)
			button.setStyleSheet("""
		               QPushButton {
		                   font-size: 18px;
		                   font-weight: bold;
		               }
		           """)

		# Time display
		self.time_label = QLabel(self.time.toString("HH:mm:ss.zzz"))

		# Connect buttons
		self.step_button.clicked.connect(self.increment_time)
		self.jump_button.clicked.connect(self.jump_to_time)

		# Layout
		h_layout = QHBoxLayout()
		h_layout.addWidget(self.step_button)
		h_layout.addWidget(self.jump_button)
		h_layout.addWidget(self.time_label)

		self.setLayout(h_layout)

	def increment_time(self):
		self.simulation_editor.TLSPN.simulate_over_time(100)  # add 1 minute

	def jump_to_time(self):
		self.simulation_editor.TLSPN.simulate_over_time(1000)  # jump to 12:00 (for example)

	def update_label(self):
		self.time_label.setText(self.time.toString("HH:mm:ss.zzz"))

	def ms_to_qtime(self, ms: int) -> QTime:
		hours = (ms // (3600 * 1000)) % 24  # keep within 24h if you want
		minutes = (ms // (60 * 1000)) % 60
		seconds = (ms // 1000) % 60
		milliseconds = ms % 1000
		return QTime(hours, minutes, seconds, milliseconds)

	def set_time(self, ms):
		self.time = self.ms_to_qtime(ms)
		self.update_label()


class LogEntryWidget(QWidget):
	def __init__(self, log_type, name, time):
		super().__init__()

		layout = QHBoxLayout()

		# Type
		self.type_label = QLabel(log_type)

		if log_type == "ENABLE":
			self.type_label.setStyleSheet("color: blue; width: 60px;")
		elif log_type == "DISABLE":
			self.type_label.setStyleSheet("color: red; width: 60px;")
		elif log_type == "ACTIVATE":
			self.type_label.setStyleSheet("color: orange; width: 60px;")
		elif log_type == "FIRABLE":
			self.type_label.setStyleSheet("color: green; width: 60px;")
		elif log_type == "FIRE":
			self.type_label.setStyleSheet("color: purple; width: 60px;")

		else:
			self.type_label.setStyleSheet("color: blue; width: 60px;")

		self.type_label.setFixedWidth(60)

		# Name
		self.name_label = QLabel(name)
		self.name_label.setStyleSheet("font-weight: bold;")
		self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

		# Time
		self.time_label = QLabel(time)
		self.time_label.setFixedWidth(60)
		self.time_label.setStyleSheet("color: gray;")

		# Add to layout
		layout.addWidget(self.type_label)
		layout.addWidget(self.name_label)
		layout.addWidget(self.time_label)

		self.setLayout(layout)


class LogViewer(QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Log Viewer")

		# Main layout for the LogViewer
		self.main_layout = QVBoxLayout(self)

		# Scroll area
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)

		# Container inside scroll area
		self.scroll_content = QWidget()
		self.scroll_layout = QVBoxLayout(self.scroll_content)
		self.scroll_layout.setContentsMargins(0, 0, 0, 0)
		self.scroll_layout.setAlignment(Qt.AlignTop)

		self.scroll_area.setWidget(self.scroll_content)
		self.main_layout.addWidget(self.scroll_area)

		# Example log entries
		logs = [
			("INFO", "Startup complete fds fds fds fds fds fds fds fds", "10:00"),
			("ERROR", "Connection failed", "10:05"),
			("DEBUG", "Retrying login", "10:06"),
			("INFO", "User logged in", "10:08"),
			("WARNING", "Low battery", "10:10"),
			("INFO", "Process completed", "10:12"),
			("ERROR", "Timeout occurred", "10:15"),
			("DEBUG", "Cleanup started", "10:17"),
			("INFO", "Shutdown", "10:20"),
		]

		# Add each log as a widget
		for log in logs:
			entry_widget = LogEntryWidget(*log)
			self.scroll_layout.addWidget(entry_widget)

	def clear_layout(self):
		while self.scroll_layout.count():
			item = self.scroll_layout.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.setParent(None)  # Removes the widget from the layout

	def add_log(self, log):
		entry_widget = LogEntryWidget(*log)
		self.scroll_layout.addWidget(entry_widget)
		QApplication.processEvents()
		self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
