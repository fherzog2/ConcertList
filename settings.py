from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class Settings:
    def set_filepath(self, filepath: str):
        QSettings().setValue("filepath", filepath)

    def get_filepath(self) -> str:
        v = QSettings().value("filepath")
        return v if v else ""

    def save_window_geometry(self, name: str, widget: QWidget):
        bytes = widget.saveGeometry()
        QSettings().setValue(name, bytes)

    def restore_window_geometry(self, name: str, widget: QWidget):
        bytes = QSettings().value(name)
        if bytes:
            widget.restoreGeometry(bytes)
