#!/usr/bin/python3
import settings
import main_window
import sys
import traceback
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


def except_hook(exctype, value, tb):
    formatted_frames = traceback.format_tb(tb)
    formatted_str = "".join(formatted_frames)

    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)

    global exception_display

    exception_display = QTextEdit()
    exception_display.setFont(font)
    exception_display.setWindowTitle("Exception")
    exception_display.setText(f"{exctype.__name__}\n{formatted_str}")

    metrics = exception_display.fontMetrics()
    size = QSize(0, 0)

    for line in exception_display.toPlainText().splitlines():
        rect = metrics.boundingRect(line)
        size.setWidth(max(size.width(), rect.width()))
        size.setHeight(size.height() + rect.height())

    size += QSize(20, 20)

    exception_display.resize(size)
    exception_display.show()
    exception_display.setEnabled(False)


if __name__ == '__main__':
    # catch exceptions to avoid crashing the app
    sys.excepthook = except_hook

    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QCoreApplication.setApplicationName("ConcertList")

    app = QApplication([])
    window = main_window.MainWindow(settings.Settings())
    window.load_filepath_from_settings()
    window.show()
    app.exec()
