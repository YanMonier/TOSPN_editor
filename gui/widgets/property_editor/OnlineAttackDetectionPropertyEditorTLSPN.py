import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, \
	QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QGroupBox, QFileDialog,  QDialog, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QApplication, QAbstractItemView, QMenu, QAction, QHeaderView, QLineEdit, QMessageBox, QFormLayout
from PySide2.QtCore import QRectF, Qt, QPointF, QPoint, QMimeData, Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint
from PySide2.QtGui import QIcon
from PySide2.QtGui import QBrush, QColor, QPen, QDrag, QCursor
from PySide2.QtCore import QSize

from PySide2.QtWidgets import (QSizePolicy, QComboBox, QFrame, QListWidgetItem, QVBoxLayout, QWidget, QLineEdit,
							   QSpinBox, QPushButton, QColorDialog, QSplitter, QLabel, QHBoxLayout, QDoubleSpinBox,
							   QDialog, QListWidget, QDialogButtonBox, QSpacerItem, QScrollArea, QMessageBox, QTableWidget,QAbstractItemView,QTableWidgetItem, QMenu,QInputDialog)
from PySide2.QtCore import Qt, Signal, QTime, QTimer
from gui.graphics.graphics_TLSPN import GraphPlaceItemTLSPN, GraphTransitionItemTLSPN, GraphArcItemTLSPN, \
	TempGraphLineTLSPN

from utils.other_utils import OutputParser
from core.model.SIGNAL_AND_EVENT.event_abstraction import EventAbstraction_manager,EventAbstraction
from core.model.SIGNAL_AND_EVENT.signal import Signal,Signal_manager
from core.model.SIGNAL_AND_EVENT.dialog_windows import SignalInputDialog,SignalEditorDialog,RuleEditorDialog

import math
import os
import json
from functools import partial

def display_error(event,time):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Erreur")
    msg.setText(f"Attack detected at time {time} with event {event}")
    msg.exec_()



class SCIASpinBoxDialog(QDialog):
	def __init__(self, TLSPN):
		super().__init__()

		self.pgcd, self.divs = TLSPN.give_common_denominator()
		self.setWindowTitle("SCIA parameters")
		self.is_step_set=False

		self.label = QLabel("Step value for SCIA (ms):")

		self.spin_box = QSpinBox()
		self.spin_box.setMinimum(0)
		self.spin_box.setMaximum(99999)
		self.spin_box.setSingleStep(1)  # pas de 5
		self.spin_box.setValue(self.pgcd)

		# Label pour message d'erreur
		self.error_label = QLabel("")
		self.error_label.setStyleSheet("color: red;")
		self.error_label.setVisible(False)  # caché par défaut

		self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		layout = QVBoxLayout()
		layout.addWidget(self.label)
		layout.addWidget(self.spin_box)
		layout.addWidget(self.error_label)
		layout.addWidget(self.button_box)

		self.setLayout(layout)

		self.spin_box.valueChanged.connect(self.check_value)
		self.check_value(self.spin_box.value())

	def check_value(self, value):

		# Exemple de condition : le nombre doit être divisible par 10
		if value not in self.divs:
			self.error_label.setText(f"⚠️ Value must be among {self.divs}")
			self.error_label.setVisible(True)
			self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
		else:
			self.error_label.setVisible(False)
			self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)

	def get_value(self):
		return self.spin_box.value()


class OnlineAttackDetectionPropertyEditorTLSPN(QWidget):
	def __init__(self, MainWindow):
		"""Initialize the output property editor."""
		super().__init__()

		self.MainWindow=MainWindow
		self.setFixedWidth(300)
		self.widget_list = []

		self.signal_manager=Signal_manager()
		self.event_abstraction_manager=EventAbstraction_manager(self.signal_manager)
		self.rules={}
		self.signals=[]

		self.timed_label_sequence = [] # Contiendra les événements
		self.event_sequence=[]
		self.current_step = -1  # Index courant de l’événement

		self.timewidget = TimeControlWidget(self)
		self.logViewer = LogViewer()


		# Layout
		self.layout = QVBoxLayout(self)
		self.layout.setAlignment(Qt.AlignTop)

		# Création du QSpinBox

		self.change_step_button=QPushButton("Change step")
		self.change_step_button.clicked.connect(self.set_SCIA_observer)

		self.step_label=QLabel("")


		self.edit_signals_button = QPushButton("Edit signals")
		self.edit_events_button = QPushButton("Edit events")

		self.edit_signals_button.clicked.connect(self.edit_signals)
		self.edit_events_button.clicked.connect(self.edit_events)

		# Bouton associé
		self.load_sequence_button = QPushButton("Load timed_event sequence")
		self.load_sequence_button.clicked.connect(self.load_event_sequence)

		self.save_mapping_button = QPushButton("Save signal configuration")
		self.save_mapping_button.clicked.connect(self.save_mapping)

		self.load_mapping_button = QPushButton("Load signal configuration")
		self.load_mapping_button.clicked.connect(self.load_mapping)
		# Layout horizontal pour placer les deux côte à côte

		hbox1=QHBoxLayout()
		hbox1.addWidget(self.save_mapping_button)
		hbox1.addWidget(self.load_mapping_button)
		self.layout.addLayout(hbox1)

		hbox2 = QHBoxLayout()
		hbox2.addWidget(self.edit_signals_button)
		hbox2.addWidget(self.edit_events_button)
		self.layout.addLayout(hbox2)


		hbox = QHBoxLayout()
		hbox.addWidget(self.load_sequence_button)
		hbox.addWidget(self.change_step_button)
		hbox.addWidget(self.step_label)




		self.layout.addLayout(hbox)

		#self.layout.addWidget(self.timewidget)
		self.layout.addWidget(self.logViewer)
		self.check_by_step_button = QPushButton("Next step")
		self.check_tot_button = QPushButton("Check tot")
		self.layout.addWidget(self.check_by_step_button)
		self.layout.addWidget(self.check_tot_button)

		self.check_by_step_button.clicked.connect(self.check_next_event)
		self.check_tot_button.clicked.connect(self.check_tot)



		# output list label




		# Current TLSPN reference
		self.TLSPN = None
		self.SCIA_observer=None
		self.set_button_state(False)

	def save_mapping(self):
		save_dic={}
		signal_mapping_dic=self.signal_manager.save_signals()
		event_mapping_dic=self.event_abstraction_manager.save_event()

		save_dic["signal_mapping"]=signal_mapping_dic
		save_dic["event_mapping"]=event_mapping_dic
		# Open a file dialog to select save location

		directory = "mapping_saves"
		if not os.path.exists(directory):
			os.makedirs(directory)
		file_path, _ = QFileDialog.getSaveFileName(
			self,
			"Save File",  # Dialog title
			directory,  # Initial directory ("" for current directory)
			"JSON Files (*.json);;All Files (*)"  # File type filters
		)
		if file_path:  # Check if the user selected a file
			with open(file_path, 'w') as json_file:
				json.dump(save_dic, json_file, indent=4)
			print(f"File saved to: {file_path}")
			QMessageBox.information(self, "Save File", "Save the current file!")
			return ("saved")

		return ("canceled")

	def load_mapping(self):

		# Open a file dialog to select save location
		directory = "mapping_saves"
		if not os.path.exists(directory):
			os.makedirs(directory)

		file_path, _ = QFileDialog.getOpenFileName(
			self,
			"Open File",  # Dialog title
			directory,  # Initial directory ("" for current directory)
			"JSON Files (*.json);;All Files (*)"  # File type filters
		)
		if file_path:  # Check if the user selected a file
			file_type = None
			with open(file_path, 'r') as json_file:
				save_dic = json.load(json_file)
				#file_type = save_dic["file_type"]
				signal_mapping_dic = save_dic["signal_mapping"]
				event_mapping_dic = save_dic["event_mapping"]
				self.event_abstraction_manager.load_event(event_mapping_dic)
				self.signal_manager.load_signals(signal_mapping_dic)
				print(f"File loaded from: {file_path}")
				QMessageBox.information(self, "Load File", "The file has been successfully loaded !")

			print("debug: try open")

	def edit_signals(self):
		dlg = SignalEditorDialog(self.signal_manager)
		if dlg.exec_() == QDialog.Accepted:
			self.signals = dlg.get_data()

	def init_rules(self):
		for event_id in self.TLSPN.events.keys():
			if event_id not in self.rules.keys() and self.TLSPN.events[event_id].name != "λ":
				self.rules[event_id]={"event_id":event_id,"condition":"","rule_id":0}

	def edit_events(self):
		dlg = RuleEditorDialog(self.event_abstraction_manager,self.signal_manager)
		if dlg.exec_() == QDialog.Accepted:
			self.rules = dlg.get_data()

	def set_SCIA_observer(self):
		dialog = SCIASpinBoxDialog(self.TLSPN)
		if dialog.exec_() == QDialog.Accepted:
			step_value = dialog.get_value()
			self.step_value=step_value
			self.step_label.setText(str(step_value))
			self.reset_attack_detection()
			self.is_step_set = True
			self.set_button_state(True)

	def set_button_state(self,value):
		if value==True:
			self.load_sequence_button.setEnabled(True)
			self.check_by_step_button.setEnabled(True)
			self.check_tot_button.setEnabled(True)
		else:
			self.load_sequence_button.setEnabled(False)
			self.check_by_step_button.setEnabled(False)
			self.check_tot_button.setEnabled(False)

	def set_TLSPN(self, TLSPN):
		"""Set the TLSPN model reference."""
		self.TLSPN = TLSPN
		self.event_abstraction_manager.reset_TLSPN(self.TLSPN)
		try:
			self.pgcd, self.divs = self.TLSPN.give_common_denominator()
			self.step_value=self.pgcd
		except:
			self.step_value = 1
		#self.reset_attack_detection()


		"""# Add existing outputs
		for output in self.TLSPN.outputs.values():
			if output.name != ".":  # Don't show lambda output in the list
				self.add_to_list(output.name, output)"""

	def reset_self(self):
		"""Reset the entire editor."""
		self.TLSPN = None
		self.event_abstraction_manager.reset_TLSPN(self.TLSPN)
		self.is_step_set=False
		self.set_button_state(False)

	def reset_attack_detection(self):
		self.SCIA_observer=self.MainWindow.construct_SCIA_observer(self.step_value)
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
						converted_sequence.append((timed_event_sequence[k][0],timed_event_sequence[k][1]))
					k+=1
					if k<len(timed_event_sequence):
						next_time = math.ceil(float(timed_event_sequence[k][1]) / dt)
					else:
						break
			converted_sequence.append(("r-e",int(i*dt)))
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
				print(self.step_value)
				self.sequence=self.convert_timed_event_sequence_into_event_sequence(self.timed_label_sequence,self.step_value)
				print("converted time sequence")
				# Ajouter tous les événements dans le log viewer
				k=0
				for event in self.sequence:
					self.logViewer.add_event_line(event[0],event[1])
					print(k)
					k+=1


	def check_next_event(self):
		if not self.sequence or self.current_step + 1 >= len(self.sequence):
			QMessageBox.information(self, "Info", "No attack detected, no more events to check.")
			return

		# Avancer
		self.current_step += 1
		event = self.sequence[self.current_step][0]
		print("event checked:",event)
		# Tester avec ton automate ici
		success = self.SCIA_observer.give_next_detected_state(event)  # À adapter selon ton code

		# Appliquer la surbrillance
		self.logViewer.highlight_line(self.current_step, success)
		print("has highlighted:", self.current_step, success)

		"""# Retirer la surbrillance précédente
		if self.current_step > 0:
			self.logViewer.reset_line_style(self.current_step - 1)
		"""
		if success==False:
			display_error(event, self.sequence[self.current_step][1])
			return(False)
		return(True)

	def check_tot(self):
		previous=True
		while previous==True:
			previous=self.check_next_event()


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


class Timed_event(QFrame):
	def __init__(self,event_text,time_text):
		super().__init__()
		self.event_name=event_text
		self.setFrameStyle(QFrame.NoFrame)
		self.main_layout = QHBoxLayout(self)
		self.event_name_label = QLabel(event_text)
		self.time_label= QLabel(time_text)
		self.event_name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		self.main_layout.addWidget(self.event_name_label)
		self.main_layout.addWidget(self.time_label)
		self.setLayout(self.main_layout)

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

	def add_event_line(self, event_text, time_text="None"):
		entry = Timed_event(event_text,str(time_text))
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
		self.event_lines[index].setObjectName("parent_only")
		style = f"""
			background-color: {color};
			border: 2px solid {border_color};
		"""
		self.event_lines[index].setStyleSheet(style)
		for child in self.event_lines[index].findChildren(QLabel):
			child.setStyleSheet("background-color: transparent; border: none;")
		self.event_lines[index].repaint()
		QApplication.processEvents()

	def reset_line_style(self, index):
		if not hasattr(self, "event_lines") or index >= len(self.event_lines):
			return
		self.event_lines[index].setStyleSheet("padding: 2px;")