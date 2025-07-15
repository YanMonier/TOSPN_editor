import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, \
	QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QGroupBox, QFileDialog
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
import math
import os
import json

class AttackDetectionPropertyEditorTLSPN(QWidget):
	def __init__(self,MainWindow):
		"""Initialize the output property editor."""
		super().__init__()

		self.MainWindow=MainWindow
		self.setFixedWidth(300)
		self.widget_list = []

		self.timed_label_sequence = [] # Contiendra les événements
		self.event_sequence=[]
		self.current_step = -1  # Index courant de l’événement

		self.timewidget = TimeControlWidget(self)
		self.logViewer = LogViewer()


		# Layout
		self.layout = QVBoxLayout(self)
		self.layout.setAlignment(Qt.AlignTop)

		# Création du QSpinBox
		self.step_spinbox = QSpinBox()
		self.step_spinbox.setMinimum(1)  # Ne peut pas aller en dessous de 1
		self.step_spinbox.setMaximum(999999)  # Optionnel : borne max
		self.step_spinbox.setValue(1000)  # Valeur par défaut
		self.step_spinbox.setPrefix("Step: ")  # Optionnel : texte devant
		self.step_spinbox.setFixedWidth(120)  # Pour éviter que ce soit trop large

		# Bouton associé
		self.load_sequence_button = QPushButton("Load timed_event sequence")
		self.load_sequence_button.clicked.connect(self.load_event_sequence)

		# Layout horizontal pour placer les deux côte à côte
		hbox = QHBoxLayout()
		hbox.addWidget(self.load_sequence_button)
		hbox.addWidget(self.step_spinbox)



		self.layout.addLayout(hbox)

		#self.layout.addWidget(self.timewidget)
		self.layout.addWidget(self.logViewer)
		self.check_by_step_button = QPushButton("Next step")
		self.check_tot_button = QPushButton("Check tot")
		self.layout.addWidget(self.check_by_step_button)
		self.layout.addWidget(self.check_tot_button)

		self.check_by_step_button.clicked.connect(self.check_next_event)



		# output list label




		# Current TLSPN reference
		self.TLSPN = None
		self.SCIA_observer=None

	def set_TLSPN(self, TLSPN):
		"""Set the TLSPN model reference."""
		self.TLSPN = TLSPN
		#self.reset_attack_detection()


		"""# Add existing outputs
		for output in self.TLSPN.outputs.values():
			if output.name != ".":  # Don't show lambda output in the list
				self.add_to_list(output.name, output)"""

	def reset_self(self):
		"""Reset the entire editor."""
		self.TLSPN = None

	def reset_attack_detection(self):
		self.SCIA_observer=self.MainWindow.construct_SCIA_observer()
		self.logViewer.clear_layout()
		self.current_step = -1

	def on_change(self, subject, event_type, data):
		a=1

	def ms_to_str(self, ms):
		hours = (ms // (3600 * 1000)) % 24  # keep within 24h if you want
		minutes = (ms // (60 * 1000)) % 60
		seconds = (ms // 1000) % 60
		milliseconds = ms % 1000
		return QTime(hours, minutes, seconds, milliseconds).toString("HH:mm:ss.zzz")

	def str_to_ms(self, time_str):
		time = QTime.fromString(time_str, "HH:mm:ss.zzz")
		if not time.isValid():
			raise ValueError(f"Invalid time format: {time_str}")

		total_ms = (
				time.hour() * 3600 * 1000 +
				time.minute() * 60 * 1000 +
				time.second() * 1000 +
				time.msec()
		)
		return total_ms

	def convert_timed_event_sequence_into_event_sequence(self, timed_event_sequence, dt):
		non_observable_event=self.TLSPN.get_unobservable_event()
		converted_sequence=[]
		last_time=float(timed_event_sequence[-1][1])
		last_discrete_time_id=math.ceil(last_time/dt)
		k=0
		for i in range(last_discrete_time_id+1):
			if k < len(timed_event_sequence):
				next_time= math.ceil(float(timed_event_sequence[k][1])/dt)
				while next_time == i:

					new_event_name=timed_event_sequence[k][0]
					if new_event_name not in non_observable_event:
						converted_sequence.append(timed_event_sequence[k][0])
					k+=1
					if k<len(timed_event_sequence):
						next_time = math.ceil(float(timed_event_sequence[k][1]) / dt)
					else:
						break
			converted_sequence.append("r-e")
		return(converted_sequence)


	def load_event_sequence(self):
		directory = "saved_timed_label_sequences"
		if not os.path.exists(directory):
			os.makedirs(directory)
		file_path, _ = QFileDialog.getOpenFileName(
			self,
			"Load Event Sequence",
			directory,
			"JSON Files (*.json);;All Files (*)"
		)
		if file_path:
			with open(file_path, 'r') as f:
				self.SCIA_observer.reset_detection()
				self.timed_label_sequence = json.load(f)
				self.current_step = -1
				self.logViewer.clear_layout()

				self.sequence=self.convert_timed_event_sequence_into_event_sequence(self.timed_label_sequence,self.step_spinbox.value())

				# Ajouter tous les événements dans le log viewer
				for event in self.sequence:
					self.logViewer.add_event_line(event)


	def check_next_event(self):
		if not self.sequence or self.current_step + 1 >= len(self.sequence):
			QMessageBox.information(self, "Info", "No more events to check.")
			return

		# Avancer
		self.current_step += 1
		event = self.sequence[self.current_step]
		print("event checked:",event)
		# Tester avec ton automate ici
		success = self.SCIA_observer.give_next_detected_state(event)  # À adapter selon ton code

		# Appliquer la surbrillance
		self.logViewer.highlight_line(self.current_step, success)
		print("has highlighted:", self.current_step, success)

		# Retirer la surbrillance précédente
		if self.current_step > 0:
			self.logViewer.reset_line_style(self.current_step - 1)


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
	def __init__(self, log_type, id, name, time):
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
		self.event_lines=[]

	def clear_layout(self):
		while self.scroll_layout.count():
			item = self.scroll_layout.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.setParent(None)  # Removes the widget from the layout
		self.event_lines = []

	def add_event_line(self, event_text):
		entry = QLabel(event_text)
		entry.setStyleSheet("padding: 2px;")
		self.scroll_layout.addWidget(entry)

		# Stocker les entrées si besoin
		if not hasattr(self, "event_lines"):
			self.event_lines = []
		self.event_lines.append(entry)

	def highlight_line(self, index, success=True):
		if not hasattr(self, "event_lines") or index >= len(self.event_lines):
			print("here bug")
			return

		print("here launched")
		color = "#cce5ff" if success else "#f8d7da"  # Bleu ou rouge clair
		border_color = "#007bff" if success else "#dc3545"

		style = f"""
			background-color: {color};
			border: 2px solid {border_color};
			padding: 2px;
		"""
		self.event_lines[index].setStyleSheet(style)
		self.event_lines[index].repaint()
		QApplication.processEvents()

	def reset_line_style(self, index):
		if not hasattr(self, "event_lines") or index >= len(self.event_lines):
			return
		self.event_lines[index].setStyleSheet("padding: 2px;")