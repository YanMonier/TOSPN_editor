import sys
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAction, QMessageBox, QToolBar, QGraphicsView, \
	QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QMainWindow, QGroupBox, QFileDialog,  QDialog, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QApplication, QAbstractItemView, QMenu, QAction, QHeaderView, QLineEdit, QMessageBox, QFormLayout
from PySide2.QtCore import QRectF, Qt, QPointF, QPoint, QMimeData, Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint


from PySide2.QtWidgets import (QSizePolicy, QComboBox, QFrame, QListWidgetItem, QVBoxLayout, QWidget, QLineEdit,
							   QSpinBox, QPushButton, QColorDialog, QSplitter, QLabel, QHBoxLayout, QDoubleSpinBox,
							   QDialog, QListWidget, QDialogButtonBox, QSpacerItem, QScrollArea, QMessageBox, QTableWidget,QAbstractItemView,QTableWidgetItem, QMenu,QInputDialog, QPlainTextEdit)
from PySide2.QtCore import Qt, Signal, QTime, QTimer
from PySide2.QtGui import QColor
from functools import partial

from core.model.SIGNAL_AND_EVENT.event_abstraction import EventSignalParser

class SignalInputDialog(QDialog):
	def __init__(self, signal_manager, parent=None):
		super().__init__(parent)
		self.setWindowTitle("New Signal")
		self.setWindowFlags(
			Qt.Dialog |
			Qt.WindowTitleHint |
			Qt.WindowCloseButtonHint
		)
		self.setModal(True)
		self.resize(300, 200)

		self.signal_manager = signal_manager

		layout = QVBoxLayout(self)

		form = QFormLayout()
		self.id_edit = QLabel(str(self.signal_manager.signal_id))
		self.source_id_edit = QSpinBox()
		self.source_id_edit.setMinimum(0)
		self.source_id_edit.setValue(0)
		self.name_edit = QLineEdit()
		self.units_edit = QLineEdit()
		self.desc_edit = QLineEdit()

		form.addRow("ID:", self.id_edit)
		form.addRow("Name:", self.name_edit)
		form.addRow("Source Id:", self.source_id_edit)
		form.addRow("Units:", self.units_edit)
		form.addRow("Description:", self.desc_edit)
		layout.addLayout(form)

		self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.ok_button = self.buttons.button(QDialogButtonBox.Ok)
		self.ok_button.setEnabled(False)  # Disabled until valid

		layout.addWidget(self.buttons)

		# Connect signals
		self.buttons.accepted.connect(self.accept)
		self.buttons.rejected.connect(self.reject)

		for edit in (self.source_id_edit, self.name_edit, self.units_edit, self.desc_edit):
			edit.textChanged.connect(self.validate_input)


	def validate_input(self):
		signal_data = {
			"id":self.id_edit.text(),
			"name":self.name_edit.text(),
			"source_id":self.source_id_edit.text(),
			"units":self.units_edit.text(),
			"description":self.desc_edit.text()
		}


		btn_enabled=False
		print(self.signal_manager.signals)
		print(self.signal_manager.signal_name_to_id)
		if int(signal_data["id"]) in self.signal_manager.signals.keys():
			print("test ", self.name_edit.text(), "with", self.signal_manager.signals[int(signal_data["id"])].name)
			if (self.name_edit.text() not in list(self.signal_manager.signal_name_to_id.keys()) or self.name_edit.text()==self.signal_manager.signals[int(signal_data["id"])].name) and self.name_edit.text()!="" and "." not in self.name_edit.text():
				btn_enabled=True
		else:
			if (self.name_edit.text() not in list(self.signal_manager.signal_name_to_id.keys())) and self.name_edit.text()!="":
				btn_enabled=True


		self.ok_button.setEnabled(btn_enabled)

	def get_signal_data(self):
		return {
			"id":self.id_edit.text(),
			"name":self.name_edit.text(),
			"source_id":self.source_id_edit.text(),
			"units":self.units_edit.text(),
			"description":self.desc_edit.text()
		}

class SignalEditorDialog(QDialog):
	def __init__(self, signal_manager, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Signal Editor")
		self.setWindowFlags(
			Qt.Dialog |
			Qt.WindowTitleHint |
			Qt.WindowCloseButtonHint
		)
		self.signal_manager=signal_manager
		self.resize(600, 400)
		self.table = QTableWidget(0, 6, self)  # Columns: ID, Name, Units, Description, Remove Button
		self.table.setHorizontalHeaderLabels(["ID", "Name", "Source ID" , "Units", "Description", ""])
		self.table.verticalHeader().setVisible(False)
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setDragDropMode(QAbstractItemView.InternalMove)
		#self.table.setDragEnabled(True)
		#self.table.setAcceptDrops(True)
		#self.table.setDropIndicatorShown(True)
		self.table.setDefaultDropAction(Qt.MoveAction)

		# Prevent editing the "Remove" column text
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.cellDoubleClicked.connect(self.edit_signal_row)
		self.table.setColumnWidth(5, 50)  # narrow column for remove buttons

		#self.table.viewport().setAcceptDrops(True)
		#self.table.setDragDropOverwriteMode(False)

		self.table.installEventFilter(self)

		# Always add the + button row at the bottom
		self.add_button_widget = QPushButton("+ Add Signal")
		self.add_button_widget.clicked.connect(self.open_add_signal_dialog)

		self.layout = QVBoxLayout(self)
		self.layout.addWidget(self.table)
		self.layout.addWidget(self.add_button_widget, alignment=Qt.AlignCenter)

		self.table.setContextMenuPolicy(Qt.CustomContextMenu)

		self.table.customContextMenuRequested.connect(self.on_context_menu)

		# Track row order on drop
		self.table.dropEvent = self.drop_event_with_reorder

		# Start with empty list
		print(self.signal_manager.signals)
		self.load_signals(list(self.signal_manager.signals.values()))

	def open_add_signal_dialog(self):
		dlg = SignalInputDialog(self.signal_manager)
		if dlg.exec_() == QDialog.Accepted:
			data = dlg.get_signal_data()
			new_signal=self.signal_manager.add_signals(data["name"],data["source_id"],data["units"],data["description"])
			# Assuming you have a signal object or just use a dict
			self.add_signal_row(new_signal)

	def edit_signal_row(self, row, column):
		# Get current values from the row
		current_data = {
			"id":int(self.table.item(row, 0).text()),
			"name":self.table.item(row, 1).text(),
			"source_id":self.table.item(row, 2).text(),
			"units":self.table.item(row, 3).text(),
			"description":self.table.item(row, 4).text()
		}
		current_signal=self.signal_manager.signals[int(current_data["id"])]

		# Open the dialog with current values prefilled
		dlg = SignalInputDialog(self.signal_manager)
		dlg.id_edit.setText(str(current_signal.id))
		dlg.source_id_edit.setValue(int(current_signal.source_id))
		dlg.name_edit.setText(current_signal.name)
		dlg.units_edit.setText(current_signal.units)
		dlg.desc_edit.setText(current_signal.description)

		if dlg.exec_() == QDialog.Accepted:
			new_data = dlg.get_signal_data()

			self.signal_manager.change_signal_name(current_signal.id,new_data["name"])
			current_signal.source_id=int(new_data["source_id"])
			current_signal.units = new_data["units"]
			current_signal.description=new_data["description"]

			self.table.item(row, 0).setText(str(current_signal.id))
			self.table.item(row, 1).setText(str(current_signal.name))
			self.table.item(row, 2).setText(str(current_signal.source_id))
			self.table.item(row, 3).setText(str(current_signal.units))
			self.table.item(row, 4).setText(str(current_signal.description))

	def eventFilter(self, source, event):
		# Disable editing on the Remove button column cells (to avoid confusion)
		if event.type() == event.MouseButtonPress and source is self.table.viewport():
			idx = self.table.indexAt(event.pos())
			if idx.isValid() and idx.column() == 5:
				# Clicking remove button area - ignore editing
				return True
		return super().eventFilter(source, event)




	def add_signal_row(self, signal, insert_row=None):
		"""Add a new signal row at the bottom or at insert_row if specified."""
		if insert_row is None:
			insert_row = self.table.rowCount()

		self.table.insertRow(insert_row)
		row = insert_row

		# ID, Name, Units, Description
		for col in range(5):
			item = QTableWidgetItem("")
			item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			self.table.setItem(row, col, item)

		self.table.item(row, 0).setText(str(signal.id))
		self.table.item(row, 1).setText(str(signal.name))
		self.table.item(row, 2).setText(str(signal.source_id))
		self.table.item(row, 3).setText(str(signal.units))
		self.table.item(row, 4).setText(str(signal.description))

		# Remove button
		btn = QPushButton("–")
		btn.setFixedWidth(25)
		btn.clicked.connect(partial(self.remove_signal, row))
		self.table.setCellWidget(row, 5, btn)

		self.update_remove_buttons()

	def remove_signal(self, row):
		signal_id=int(self.table.item(row, 0).text())
		self.table.removeRow(row)
		self.signal_manager.remove_signals(signal_id)
		self.update_remove_buttons()

	def update_remove_buttons(self):
		# Reconnect remove buttons with correct row indices
		for row in range(self.table.rowCount()):
			cell_widget = self.table.cellWidget(row, 5)
			if isinstance(cell_widget, QPushButton):
				# Disconnect old connections safely
				try:
					cell_widget.clicked.disconnect()
				except Exception:
					pass
				cell_widget.clicked.connect(partial(self.remove_signal, row))

	def on_context_menu(self, point: QPoint):
		idx = self.table.indexAt(point)
		if not idx.isValid():
			return
		row = idx.row()

		menu = QMenu(self)
		insert_above_action = QAction("Insert Signal Above", self)
		insert_below_action = QAction("Insert Signal Below", self)

		insert_above_action.triggered.connect(lambda:self.insert_signal(row))
		insert_below_action.triggered.connect(lambda:self.insert_signal(row + 1))

		menu.addAction(insert_above_action)
		menu.addAction(insert_below_action)

		menu.exec_(self.table.viewport().mapToGlobal(point))

	def insert_signal(self, row):
		self.add_signal_row(insert_row=row)

	def drop_event_with_reorder(self, event):
		"""Custom drop event to reorder rows without overwriting."""
		source = event.source()
		if source != self.table:
			super(QTableWidget, self.table).dropEvent(event)
			return

		drop_position = self.table.indexAt(event.pos()).row()
		if drop_position == -1:
			drop_position = self.table.rowCount() - 1

		selected_rows = sorted(set([i.row() for i in self.table.selectedIndexes()]))
		if not selected_rows:
			event.ignore()
			return

		# Copy data of selected rows
		rows_data = []
		for r in selected_rows:
			row_data = {}
			for c in range(5):
				item = self.table.item(r, c)
				row_data[self.table.horizontalHeaderItem(c).text().lower()] = item.text() if item else ""
			rows_data.append(row_data)

		# Remove selected rows bottom-up to avoid index shifting
		for r in reversed(selected_rows):
			self.table.removeRow(r)
			if r < drop_position:
				drop_position -= 1

		# Insert rows at drop position
		for i, data in enumerate(rows_data):
			signal=self.signal_manager.signals[int(data["id"])]
			self.add_signal_row(signal=signal,insert_row=drop_position + i)

		self.update_remove_buttons()
		event.accept()

	def load_signals(self, signals):
		"""Load a list of dicts with keys: id, name, units, description"""
		self.table.setRowCount(0)
		for signal in signals:
			print("add row signal",signal)
			self.add_signal_row(signal)
		self.update_remove_buttons()

	def get_signals(self):
		"""Return list of signals as dicts"""
		signals = []
		for row in range(self.table.rowCount()):
			signal = {
				"id":self.table.item(row, 0).text() if self.table.item(row, 0) else "",
				"name":self.table.item(row, 1).text() if self.table.item(row, 1) else "",
				"units":self.table.item(row, 2).text() if self.table.item(row, 2) else "",
				"description":self.table.item(row, 3).text() if self.table.item(row, 3) else ""
			}
			signals.append(signal)
		return signals


class ScrollableLabelList(QWidget):
	def __init__(self,max_width=250):
		super().__init__()
		self.max_width = max_width
		self.layout = QVBoxLayout(self)
		self.layout.setAlignment(Qt.AlignTop)
		self.setLayout(self.layout)

	def add_label(self, text):
		label = QLabel(text)
		label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		label.setStyleSheet("padding: 4px;")
		self.layout.addWidget(label)
		self._update_size()

	def _update_size(self):
		"""Adjust scroll width based on content, with max width limit."""
		self.adjustSize()
		content_width = self.sizeHint().width()
		final_width = min(content_width, self.max_width)
		self.setMinimumWidth(final_width)

# Skeleton dialog for Event Conversion Rules
class RuleEditorDialog(QDialog):
	def __init__(self, event_abstraction_manager, signal_manager, parent=None):
		super().__init__(parent)
		self.setWindowFlags(
			Qt.Dialog |
			Qt.WindowTitleHint |
			Qt.WindowCloseButtonHint
		)
		self.signal_manager=signal_manager
		self.event_parser=EventSignalParser(self.signal_manager)
		self.event_abstraction_manager=event_abstraction_manager
		self.TLSPN=self.event_abstraction_manager.TLSPN
		self.setWindowTitle("Event Conversion Rules Editor")
		self.layout = QHBoxLayout(self)
		self.resize(600, 400)
		self.info_label = QTableWidget()
		self.info_label.setColumnCount(3)
		self.info_label.setHorizontalHeaderLabels(["Event Name", "event ID", "Condition"])
		self.info_label.verticalHeader().setVisible(False)
		self.info_label.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.info_label.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.info_label.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.info_label.cellDoubleClicked.connect(self.open_condition_editor)
		self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		# Scroll area
		self.scroll = QScrollArea()
		self.scroll.setWidgetResizable(True)
		self.scroll.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

		# Container for labels
		self.label_list = ScrollableLabelList()
		self.scroll.setWidget(self.label_list)


		self.layout.addWidget(self.scroll)
		self.layout.addWidget(self.info_label)

		for signal_id in self.signal_manager.signals.keys():
			self.label_list.add_label(self.signal_manager.signals[signal_id].name)
		content_width = self.label_list.sizeHint().width() + self.scroll.verticalScrollBar().sizeHint().width()
		self.scroll.setMinimumWidth(content_width)


		# Store rules as list of dicts
		self.rules = {}
		self.event_abstraction_manager.update_TLSPN(self.TLSPN)
		self.load_rules()

	def insert_separator_row_end(self, color=QColor("red")):
		table=self.info_label
		row_index = table.rowCount()  # end of table
		table.insertRow(row_index)
		table.setRowHeight(row_index, 2)  # thin line

		for col in range(table.columnCount()):
			item = QTableWidgetItem("")
			item.setBackground(color)
			# Make it non-editable and non-selectable
			item.setFlags(Qt.NoItemFlags)
			table.setItem(row_index, col, item)

	def open_condition_editor(self, row, column):
		# Only act on last column (index 2)
		if column != 2:
			return

		current_text = self.info_label.item(row, column).text() if self.info_label.item(row, column) else ""
		current_event_id= int(self.info_label.item(row, 1).text())

		# Create dialog manually
		dialog = QInputDialog(self)
		dialog.setWindowTitle("Edit Condition")
		dialog.setLabelText("Condition:")
		dialog.setTextValue(current_text)
		dialog.setOption(QInputDialog.UsePlainTextEditForTextInput)

		# Get OK button from the button box
		text_edit = dialog.findChild(QPlainTextEdit)
		button_box = dialog.findChild(QDialogButtonBox)
		ok_button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)

		def on_text_changed():
			ok_button.setEnabled(self.is_valid_condition(dialog.textValue()))

		text_edit.textChanged.connect(on_text_changed)


		if dialog.exec_() == QInputDialog.Accepted:
			text = dialog.textValue()
			parsed_text=self.event_parser.parse_to_id(text)
			self.event_abstraction_manager.events[current_event_id].rule=parsed_text
			if not self.info_label.item(row, column):
				self.info_label.setItem(row, column, QTableWidgetItem())
			self.info_label.item(row, column).setText(self.event_parser.convert_parsed_id_into_txt_name(self.event_abstraction_manager.events[int(current_event_id)].rule))

	def is_valid_condition(self, text):
		# Example rule: must not be empty and contain "if"
		test = self.event_parser.check_validity(text)
		if test==True:
			test, res = self.event_parser.tryParsing(text)
			print("with id",self.event_parser.convert_to_id(text))
			print("math: ",self.event_parser.reformat_math_expression(res.asList()))
			print("reformat_txt: ",self.event_parser.reformat_txt(text))

			parseid=self.event_parser.parse_to_id(text)
			print("parse_to_id: ",parseid)
			print("reconvert: ", self.event_parser.convert_parsed_id_to_parse_name(parseid))


		return test

	def add_event_abstraction(self, event_abstraction):
		row = self.info_label.rowCount()
		self.info_label.insertRow(row)

		for col in range(3):
			item = QTableWidgetItem("")
			item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			self.info_label.setItem(row, col, item)


		self.info_label.item(row, 0).setText(self.TLSPN.events[event_abstraction.event_id].name)
		self.info_label.item(row, 1).setText(str(event_abstraction.event_id))
		self.info_label.item(row, 2).setText(self.event_parser.convert_parsed_id_into_txt_name(event_abstraction.rule))

	def add_output_abstraction(self, event_abstraction):
		row = self.info_label.rowCount()
		self.info_label.insertRow(row)

		for col in range(3):
			item = QTableWidgetItem("")
			item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			self.info_label.setItem(row, col, item)


		self.info_label.item(row, 0).setText(self.TLSPN.outputs[event_abstraction.event_id].name)
		self.info_label.item(row, 1).setText(str(event_abstraction.event_id))
		self.info_label.item(row, 2).setText(self.event_parser.convert_parsed_id_into_txt_name(event_abstraction.rule))




	def load_rules(self):
		self.info_label.setRowCount(0)
		for event_abstraction in self.event_abstraction_manager.events.values():
			self.add_event_abstraction(event_abstraction)
		self.insert_separator_row_end()
		for event_abstraction in self.event_abstraction_manager.outputs.values():
			self.add_output_abstraction(event_abstraction)


	def get_rules(self):
		rules = {}
		for row in range(self.info_label.rowCount()):
			rule = {
				"rule_id":self.info_label.item(row, 0).text() if self.info_label.item(row, 0) else "",
				"condition":self.info_label.item(row, 1).text() if self.info_label.item(row, 1) else "",
				"event_id":self.info_label.item(row, 2).text() if self.info_label.item(row, 2) else ""
			}
			rules[int(self.info_label.item(row, 1).text())]=rule
		return rules