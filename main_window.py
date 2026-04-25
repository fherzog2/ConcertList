import os
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import concert_adder
import concert_list
import concert_list_view
import settings
import version_info_window


class ErrorHandler:
    def error_occured(self, parent: QWidget, title: str, text: str):
        QMessageBox.critical(parent, title, text)


class MainWindow(QFrame):
    def __init__(self, settings: settings.Settings, error_handler=ErrorHandler()):
        super().__init__()
        self.settings = settings
        self.error_handler = error_handler

        toolbar_layout = QHBoxLayout()

        self.model = concert_list.ConcertListModel()
        self.concert_list_view = concert_list_view.ConcertListViewUnfiltered(self)

        save_button = QToolButton(self)
        save_button.setText("Save As...")
        save_button.clicked.connect(self.create_file_interactive)
        toolbar_layout.addWidget(save_button)

        load_button = QToolButton(self)
        load_button.setText("Open...")
        load_button.clicked.connect(self.open_file_interactive)
        toolbar_layout.addWidget(load_button)

        add_button = QToolButton(self)
        add_button.setText("Add entries...")
        add_button.clicked.connect(self.add_entries)
        toolbar_layout.addWidget(add_button)

        toolbar_layout.addSpacing(20)

        def create_button(parent: QWidget, text: str, slot):
            button = QPushButton(text, parent)
            button.clicked.connect(slot)
            toolbar_layout.addWidget(button)
            return button

        default_view_button = create_button(self, "Default view", lambda: self.show_view(concert_list_view.ConcertListViewUnfiltered(self)))
        create_button(self, "Concerts grouped by band", lambda: self.show_view(concert_list_view.ConcertListViewConcertsGroupedByBand(self)))
        create_button(self, "Most seen bands", lambda: self.show_view(concert_list_view.ConcertListViewMostSeenBands(self)))
        create_button(self, "Concerts per year", lambda: self.show_view(concert_list_view.ConcertListViewConcertsPerYear(self)))
        create_button(self, "Festivals", lambda: self.show_view(concert_list_view.ConcertListViewFestivals(self)))
        create_button(self, "Locations", lambda: self.show_view(concert_list_view.ConcertListViewLocations(self)))
        create_button(self, "Grid", lambda: self.show_view(concert_list_view.ConcertListViewGrid(self)))

        toolbar_layout.addStretch()

        app_menu = QMenu()
        about_action = app_menu.addAction("About...")
        about_action.triggered.connect(self.show_version_info_window)
        app_menu_button = QToolButton(self)
        app_menu_button.setText("…")
        app_menu_button.setMenu(app_menu)
        app_menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar_layout.addWidget(app_menu_button)

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar_layout)
        default_view_button.click()

        self.settings.restore_window_geometry("MainWindow", self)

    def hideEvent(self, event):
        self.settings.save_window_geometry("MainWindow", self)
        super().hideEvent(event)

    def show_view(self, concert_list_view: concert_list_view.ConcertListView | concert_list_view.ConcertListViewGrid):
        self.concert_list_view.hide()
        self.concert_list_view.deleteLater()

        self.concert_list_view = concert_list_view
        self.concert_list_view.set_model(self.model)
        self.layout().addWidget(self.concert_list_view)

    def set_filepath(self, path: str):
        self.model.load_file(path)
        self.concert_list_view.set_model(self.model)
        self.setWindowTitle(f"{QCoreApplication.applicationName()} - {path}")

    def create_file(self, path: str):
        self.model.save_file(path)
        self.set_filepath(path)
        self.settings.set_filepath(path)

    def create_file_interactive(self):
        path = QFileDialog.getSaveFileName(filter="Concert list (*.yaml)")[0]
        if len(path) > 0:
            self.create_file(path)

    def open_file(self, path: str):
        try:
            self.set_filepath(path)
            self.settings.set_filepath(path)
        except Exception as e:
            self.error_handler.error_occured(self, str(e.__class__.__name__), str(e))

    def open_file_interactive(self):
        path = QFileDialog.getOpenFileName(filter="Concert list (*.yaml)")[0]
        if len(path) > 0:
            self.open_file(path)

    def load_filepath_from_settings(self):
        try:
            if os.path.exists(self.settings.get_filepath()):
                self.set_filepath(self.settings.get_filepath())
        except Exception as e:
            self.error_handler.error_occured(self, str(e.__class__.__name__), str(e))
            self.settings.set_filepath("")

    def save_file(self):
        if os.path.exists(self.settings.get_filepath()):
            self.model.save_file(self.settings.get_filepath())
        self.concert_list_view.set_model(self.model)

    def add_entries(self):
        self.adder = concert_adder.AddConcertWindow(self, self.model, self.settings)
        self.adder.set_added_callback(self.save_file)
        if self.isVisible():
            self.adder.show()

    def show_version_info_window(self):
        self.version_info_window = version_info_window.VersionInfoWindow(self)
        self.version_info_window.show()
