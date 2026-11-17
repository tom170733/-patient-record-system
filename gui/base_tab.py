"""Reusable CRUD screen. Each tab (Patients, Doctors, ...) inherits from
BaseCrudTab and overrides a few "hook" methods - the same idea as an
abstract base class. (PyQt widgets cannot also use abc.ABC because of a
metaclass conflict, so the hooks raise NotImplementedError instead.)
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QFormLayout, QGridLayout,
                             QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from database import DatabaseError
from manager import RecordManager


class BaseCrudTab(QWidget):
    status_message = pyqtSignal(str)

    title = "Item"
    headers = ("ID",)

    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.repo = repository
        self.manager = RecordManager(self.title)   # in-memory dict cache
        self.selected_id = None
        self._build_ui()

    # ------------------------------------------------------------ hooks
    def build_form(self, form):
        raise NotImplementedError

    def read_form(self):
        """Create a model object from the form (validation happens in the model)."""
        raise NotImplementedError

    def fill_form(self, obj):
        raise NotImplementedError

    def clear_form(self):
        raise NotImplementedError

    def row_values(self, obj):
        raise NotImplementedError

    def refresh_choices(self):
        """Override when the form has drop-downs that come from other tables."""

    # ------------------------------------------------------------ layout
    def _build_ui(self):
        root = QHBoxLayout(self)

        # Left: form + buttons
        left = QVBoxLayout()
        box = QGroupBox(f"{self.title} details")
        self.form = QFormLayout(box)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.build_form(self.form)
        left.addWidget(box)

        buttons = QGridLayout()
        self.btn_add = self._button("&Add", "Save a new record (Ctrl+N)", self.on_add, "Ctrl+N")
        self.btn_update = self._button("&Update", "Save changes to the selected record (Ctrl+S)",
                                       self.on_update, "Ctrl+S")
        self.btn_delete = self._button("&Delete", "Delete the selected record (Del)",
                                       self.on_delete, QKeySequence.StandardKey.Delete)
        self.btn_clear = self._button("&Clear", "Clear the form (Esc)", self.on_clear, "Esc")
        for i, b in enumerate((self.btn_add, self.btn_update, self.btn_delete, self.btn_clear)):
            buttons.addWidget(b, i // 2, i % 2)
        left.addLayout(buttons)
        left.addStretch()
        root.addLayout(left, 2)

        # Right: search + table
        right = QVBoxLayout()
        search_row = QHBoxLayout()
        label = QLabel("&Search:")
        self.search = QLineEdit(placeholderText=f"Type to filter {self.title.lower()}s...")
        self.search.setAccessibleName(f"Search {self.title.lower()}s")
        label.setBuddy(self.search)
        self.search.textChanged.connect(self.on_search)
        search_row.addWidget(label)
        search_row.addWidget(self.search)
        right.addLayout(search_row)

        self.table = QTableWidget(0, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setAccessibleName(f"{self.title} list")
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self.on_select)
        right.addWidget(self.table)
        self.count_label = QLabel()
        right.addWidget(self.count_label)
        root.addLayout(right, 3)
        self.clear_form()
        self._update_buttons()

    def _button(self, text, tip, slot, shortcut):
        b = QPushButton(text)
        b.setToolTip(tip)
        b.setAccessibleName(text.replace("&", ""))
        b.setShortcut(QKeySequence(shortcut))
        b.clicked.connect(slot)
        return b

    def add_field(self, form, label_text, widget, help_text=""):
        """Add a labelled, accessible field to the form."""
        label = QLabel(label_text)
        label.setBuddy(widget)  # keyboard users can jump to the field with Alt+letter
        widget.setAccessibleName(label_text.replace("&", "").rstrip(":* "))
        if help_text:
            widget.setToolTip(help_text)
            widget.setAccessibleDescription(help_text)
        form.addRow(label, widget)
        return widget

    @staticmethod
    def combo(items):
        c = QComboBox()
        c.addItems(items)
        return c

    @staticmethod
    def select_data(combo, value):
        index = combo.findData(value)
        combo.setCurrentIndex(max(index, 0))

    # ------------------------------------------------------------ data
    def load(self):
        try:
            self.manager.replace_all(self.repo.get_all())
        except DatabaseError as exc:
            self._error(exc)
            return
        self.show_items(self.manager.all())
        self.on_search(self.search.text())

    def show_items(self, items):
        self.table.setRowCount(0)
        for obj in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate(self.row_values(obj)):
                cell = QTableWidgetItem(str(value))
                if col == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, obj.id)
                self.table.setItem(row, col, cell)
        self.count_label.setText(f"Showing {len(items)} of {len(self.manager)} {self.title.lower()}(s)")

    # ------------------------------------------------------------ slots
    def on_add(self):
        try:
            obj = self.read_form()
            self.repo.add(obj)
        except (ValueError, DatabaseError) as exc:
            self._error(exc)
            return
        self.load()
        self.on_clear()
        self.status_message.emit(f"{self.title} added: {obj.summary()}")

    def on_update(self):
        if self.selected_id is None:
            return
        try:
            obj = self.read_form()
            obj.id = self.selected_id
            self.repo.update(obj)
        except (ValueError, DatabaseError) as exc:
            self._error(exc)
            return
        self.load()
        self.status_message.emit(f"{self.title} #{obj.id} updated.")

    def on_delete(self):
        if self.selected_id is None:
            return
        obj = self.manager.get(self.selected_id)
        answer = QMessageBox.question(
            self, f"Delete {self.title.lower()}",
            f"Delete this {self.title.lower()}?\n\n{obj.summary()}\n\nThis cannot be undone.")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.repo.delete(self.selected_id)
        except DatabaseError as exc:
            self._error(exc)
            return
        self.manager.delete(self.selected_id)
        self.on_clear()
        self.load()
        self.status_message.emit(f"{self.title} #{obj.id} deleted.")

    def on_clear(self):
        self.table.clearSelection()
        self.selected_id = None
        self.clear_form()
        self._update_buttons()

    def on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        item_id = self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        obj = self.manager.get(item_id)
        if obj:
            self.selected_id = item_id
            self.fill_form(obj)
            self._update_buttons()

    def on_search(self, text):
        self.show_items(self.manager.search(text) if text else self.manager.all())

    def _update_buttons(self):
        selected = self.selected_id is not None
        self.btn_update.setEnabled(selected)
        self.btn_delete.setEnabled(selected)

    def _error(self, exc):
        QMessageBox.warning(self, "Please check", str(exc))


class PeopleChoicesMixin:
    """Mixin for tabs that need patient and doctor drop-downs.
    Used with BaseCrudTab -> another example of multiple inheritance."""

    def fill_people_combos(self, patient_combo, doctor_combo, patient_repo, doctor_repo):
        for combo, repo in ((patient_combo, patient_repo), (doctor_combo, doctor_repo)):
            current = combo.currentData()
            combo.clear()
            try:
                people = repo.get_all()
            except DatabaseError:
                people = []
            for person in people:
                combo.addItem(f"{person.full_name} (#{person.id})", person.id)
            self.select_data(combo, current)
