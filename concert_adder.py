import datetime
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import concert_list
import settings
import functools


def sort_numeric(names: list[str]) -> list[str]:
    collator = QCollator()
    collator.setNumericMode(True)
    return sorted(names, key=functools.cmp_to_key(collator.compare))


def create_sorted_completer(names: list[str], parent):
    completer = QCompleter(sort_numeric(names), parent)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    return completer


class NameItemDelegate(QItemDelegate):
    """Opens an editor with auto-completion for the provided names."""

    def __init__(self):
        super().__init__()

    def set_names(self, names):
        self.names = names

    def createEditor(self, parent, option, index):
        edit_widget = super().createEditor(parent, option, index)
        completer = create_sorted_completer(self.names, edit_widget)
        edit_widget.setCompleter(completer)
        return edit_widget


class NameListWidget(QFrame):
    """An editable list of names."""

    def __init__(self):
        super().__init__()

        self.name_list = QListWidget()
        self.name_item_delegate = NameItemDelegate()
        self.name_list.setItemDelegate(self.name_item_delegate)

        action_add = QAction("＋", self)
        action_add.setToolTip("Add")
        action_add.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Plus))
        action_add.triggered.connect(self.add_name)

        button_add = QToolButton()
        button_add.setDefaultAction(action_add)

        action_remove = QAction("🗑", self)
        action_remove.setToolTip("Remove")
        action_remove.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        action_remove.triggered.connect(self.remove_name)

        button_remove = QToolButton()
        button_remove.setDefaultAction(action_remove)

        # list on the left, buttons vertically stacked on the right

        layout = QGridLayout(self)
        layout.addWidget(self.name_list, 0, 0, 3, 1)
        layout.addWidget(button_add, 0, 1)
        layout.addWidget(button_remove, 1, 1)
        layout.setRowStretch(2, 1)
        layout.setContentsMargins(0, 0, 0, 0)

    def set_list_changed_slot(self, slot):
        self.name_list.model().dataChanged.connect(slot)
        self.name_list.model().rowsRemoved.connect(slot)

    def set_auto_complete_names(self, names):
        self.name_item_delegate.set_names(names)

    def add_name(self):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.name_list.addItem(item)

        # open edit widget for the new item
        self.name_list.edit(self.name_list.indexFromItem(item))

    def add_name_internal(self, name: str):
        item = QListWidgetItem()
        item.setText(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.name_list.addItem(item)

    def remove_name(self):
        item = self.name_list.takeItem(self.name_list.currentRow())
        if item is not None:
            del item

    def clear(self):
        self.name_list.clear()

    def get_names(self):
        return [self.name_list.item(i).text()
                for i in range(self.name_list.count())]


class AddConcertWindow(QFrame):
    def __init__(self, parent, model: concert_list.ConcertListModel, settings: settings.Settings):
        super().__init__(parent, Qt.WindowType.Window)
        self.model = model
        self.settings = settings
        self.create_layout()
        self.load_info()
        self.validate_input()

        self.settings.restore_window_geometry("AddConcertWindow", self)

    def hideEvent(self, event):
        self.settings.save_window_geometry("AddConcertWindow", self)
        super().hideEvent(event)

    def set_added_callback(self, callback):
        self.added_callback = callback

    def load_info(self):
        info = concert_list.ConcertListInfo(self.model)

        completer = create_sorted_completer(info.get_locations(), self)
        self.location.setCompleter(completer)

        completer = create_sorted_completer(info.get_names(), self)
        self.name.setCompleter(completer)

        self.bands.set_auto_complete_names(info.get_bands())

    def validate_input(self):
        location_ok = len(self.location.text()) > 0

        bands = self.bands.get_names()
        bands_ok = "" not in bands and len(bands) > 0 and len(bands[0]) > 0

        self.button_add.setEnabled(location_ok and bands_ok)

    def add_concert_entry(self):
        qdate = self.date.date()
        date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        bands = self.bands.get_names()

        concert = concert_list.create_concert(
            date,
            self.location.text(),
            bands,
            name=self.name.text(),
            festival=self.is_festival.isChecked())

        self.model.add_concert(concert)

        # clear data after it has been saved

        self.location.setText("")
        self.name.setText("")
        self.bands.clear()

        # reload from file

        self.load_info()
        self.added_callback()

    def create_layout(self):
        self.setWindowTitle("Add Concert")

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())

        self.location = QLineEdit()
        self.location.textChanged.connect(self.validate_input)

        self.name = QLineEdit()

        self.is_festival = QCheckBox("Festival")

        self.bands = NameListWidget()
        self.bands.set_list_changed_slot(self.validate_input)

        self.button_add = QPushButton('Add To Concert File')
        self.button_add.clicked.connect(self.add_concert_entry)

        layout = QGridLayout()

        layout.addWidget(QLabel("Date"), 4, 0)
        layout.addWidget(self.date, 4, 1)

        layout.addWidget(QLabel("Location"))
        layout.addWidget(self.location)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name)

        layout.addWidget(QWidget())
        layout.addWidget(self.is_festival)

        layout.addWidget(QLabel("Bands"))
        layout.addWidget(self.bands)

        layout.addWidget(self.button_add, layout.rowCount(), 0, 1, 2)

        self.setLayout(layout)
