import concert_list
import concert_list_view
import example_data
import main_window
import os
import tempfile
import unittest
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class MockSettings:
    def __init__(self):
        self.filepath = ""

    def set_filepath(self, filepath: str):
        self.filepath = filepath

    def get_filepath(self) -> str:
        return self.filepath

    def save_window_geometry(self, name, widget):
        pass

    def restore_window_geometry(self, name, widget):
        pass


class ErrorHandler:
    def __init__(self):
        self.errors = []

    def error_occured(self, parent: QWidget, title: str, text: str):
        self.errors.append(title)


class TestMainWindow(unittest.TestCase):
    def add_concert(self, window: main_window.MainWindow, concert_raw):
        concert = concert_list.Concert(concert_raw)

        window.add_entries()

        window.adder.location.setText(concert.location)
        window.adder.name.setText(concert.name)
        window.adder.is_festival.setChecked(concert.festival)
        for band in concert.bands:
            window.adder.bands.add_name_internal(band)

        window.adder.validate_input()
        window.adder.button_add.click()
        window.adder.close()

    def test_build_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, "concerts.yaml")

            concerts = example_data.get_example_concerts()

            # add the concerts one by one, like the user would do it

            app = QApplication([])
            settings = MockSettings()
            window = main_window.MainWindow(settings)
            window.load_filepath_from_settings()
            self.assertEqual(window.concert_list_view.table.rowCount(), 0)

            # start clean and add first band

            self.add_concert(window, concerts[0])
            self.assertEqual(window.concert_list_view.table.rowCount(), 1)

            # actually safe the file and continue

            window.create_file(filepath)

            self.add_concert(window, concerts[1])
            self.assertEqual(window.concert_list_view.table.rowCount(), 2)

            # change view and continue

            window.show_view(concert_list_view.ConcertListViewConcertsGroupedByBand(window))
            self.assertEqual(window.concert_list_view.table.rowCount(), 6)

            self.add_concert(window, concerts[2])
            self.assertEqual(window.concert_list_view.table.rowCount(), 9)

            window.show_view(concert_list_view.ConcertListViewUnfiltered(window))
            self.assertEqual(window.concert_list_view.table.rowCount(), 3)

            # load the file again with a fresh main window instance

            window = main_window.MainWindow(settings)
            window.load_filepath_from_settings()
            self.assertEqual(window.concert_list_view.table.rowCount(), 3)

    def create_good_bad_file(self, tmpdirname: str):
        good_file = os.path.join(tmpdirname, "good.yaml")
        bad_file = os.path.join(tmpdirname, "bad.yaml")

        model = concert_list.ConcertListModel()
        model.set_concerts(example_data.get_example_concerts())
        model.save_file(good_file)

        with open(bad_file, "w") as f:
            f.write(",.-#+#+ bad file")

        return (good_file, bad_file)

    def test_open_good_bad_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            (good_file, bad_file) = self.create_good_bad_file(tmpdirname)

            app = QApplication([])
            settings = MockSettings()
            error_handler = ErrorHandler()
            window = main_window.MainWindow(settings, error_handler)

            window.open_file(good_file)

            self.assertEqual(window.concert_list_view.table.rowCount(), 3)
            self.assertEqual(settings.get_filepath(), good_file)
            self.assertEqual(error_handler.errors, [])

            window.open_file(bad_file)

            # expectation: the good content is still loaded after trying to open the bad file

            self.assertEqual(window.concert_list_view.table.rowCount(), 3)
            self.assertEqual(settings.get_filepath(), good_file)
            self.assertEqual(error_handler.errors, ["ParserError"])

            window.save_file()

    def test_open_bad_good_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            (good_file, bad_file) = self.create_good_bad_file(tmpdirname)

            app = QApplication([])
            settings = MockSettings()
            error_handler = ErrorHandler()
            window = main_window.MainWindow(settings, error_handler)

            window.open_file(bad_file)

            self.assertEqual(window.concert_list_view.table.rowCount(), 0)
            self.assertEqual(settings.get_filepath(), "")
            self.assertEqual(error_handler.errors, ["ParserError"])

            window.open_file(good_file)

            self.assertEqual(window.concert_list_view.table.rowCount(), 3)
            self.assertEqual(settings.get_filepath(), good_file)
            self.assertEqual(error_handler.errors, ["ParserError"])

            window.save_file()

    def test_restore_good_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            (good_file, bad_file) = self.create_good_bad_file(tmpdirname)

            app = QApplication([])
            settings = MockSettings()
            error_handler = ErrorHandler()
            window = main_window.MainWindow(settings, error_handler)

            settings.set_filepath(good_file)
            window.load_filepath_from_settings()

            self.assertEqual(window.concert_list_view.table.rowCount(), 3)
            self.assertEqual(settings.get_filepath(), good_file)
            self.assertEqual(error_handler.errors, [])

            window.save_file()

    def test_restore_bad_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            (good_file, bad_file) = self.create_good_bad_file(tmpdirname)

            app = QApplication([])
            settings = MockSettings()
            error_handler = ErrorHandler()
            window = main_window.MainWindow(settings, error_handler)

            settings.set_filepath(bad_file)
            window.load_filepath_from_settings()

            # expectation: if the file cannot be restored from the settings, reset the settings entry

            self.assertEqual(window.concert_list_view.table.rowCount(), 0)
            self.assertEqual(settings.get_filepath(), "")
            self.assertEqual(error_handler.errors, ["ParserError"])

            window.save_file()
