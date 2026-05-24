from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class Settings:
    def set_filepath(self, filepath: str):
        QSettings().setValue("filepath", filepath)

    def get_filepath(self) -> str:
        v = QSettings().value("filepath")
        return v if v else ""

    def push_recent_file(self, filepath: str):
        recent_files = self.get_recent_files()
        try:
            recent_files.remove(filepath)
        except ValueError:
            pass
        recent_files.insert(0, filepath)
        QSettings().setValue("recent_files", recent_files)

    def get_recent_files(self) -> list[str]:
        v = QSettings().value("recent_files")
        return v if v else []

    def save_window_geometry(self, name: str, widget: QWidget):
        bytes = widget.saveGeometry()
        QSettings().setValue(name, bytes)

    def restore_window_geometry(self, name: str, widget: QWidget):
        bytes = QSettings().value(name)
        if bytes:
            widget.restoreGeometry(bytes)
