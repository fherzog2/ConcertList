from concert_list import *
import unittest
import tempfile
import os
import datetime
import example_data


class TestConcertList(unittest.TestCase):
    def test_load(self):
        self.assertEqual(load_concerts(example_data.get_example_yaml_str()), example_data.get_example_concerts())

    def test_save(self):
        self.assertEqual(dump_concerts(example_data.get_example_concerts()), example_data.get_example_yaml_str())

    def test_unicode(self):
        data = """- bands:
  - äöüÄÖÜéㅍ
  date: 2010-02-03
  location: Berlin
"""
        self.assertEqual(dump_concerts(load_concerts(data)), data)

    def test_add_to_file(self):
        concert = create_concert(datetime.date(2012, 12, 1), "Location", ["Band 1", "Band 2"])

        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, "concerts.yaml")
            with open(filepath, "w", encoding="utf8") as f:
                f.write(example_data.get_example_yaml_str())

            add_concert_to_file(filepath, concert)

            with open(filepath, "r", encoding="utf8") as f:
                content = f.read()
                loaded = load_concerts(content)

            expected = example_data.get_example_concerts() + [concert]
            self.assertEqual(loaded, expected)

            self.assertFalse(os.path.exists(filepath + ".tmp"))
            self.assertFalse(os.path.exists(filepath + ".bak"))

        with self.assertRaises(FileNotFoundError):
            add_concert_to_file("invalid path", concert)

    def test_model(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, "concerts.yaml")
            with open(filepath, "w", encoding="utf8") as f:
                f.write(example_data.get_example_yaml_str())

            model = ConcertListModel()
            model.load_file(filepath)

            self.assertEqual(model.concerts, example_data.get_example_concerts())

            filepath = os.path.join(tmpdirname, "empty.yaml")
            with open(filepath, "w", encoding="utf8") as f:
                f.write("")

            model.load_file(filepath)

            self.assertEqual(model.concerts, example_data.get_example_concerts())

        model = ConcertListModel()
        with self.assertRaises(FileNotFoundError):
            model.load_file("invalid path")

    def test_info(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, "concerts.yaml")
            with open(filepath, "w", encoding="utf8") as f:
                f.write(example_data.get_example_yaml_str())

            model = ConcertListModel()
            model.load_file(filepath)
            info = ConcertListInfo(model)

            self.assertEqual(info.get_number_of_concerts(), 3)
            self.assertEqual(sorted(info.get_locations()), ['Clisson', 'München, Olympiastadion'])
            self.assertEqual(sorted(info.get_names()), ["Hellfest"])
            self.assertEqual(sorted(info.get_bands()), ['Architects', 'Fear Factory', 'Kataklysm', 'Machine Head', 'Mammoth WVH', 'Metallica', 'The Prodigy'])

        info = ConcertListInfo(ConcertListModel())

        self.assertEqual(info.get_number_of_concerts(), 0)
        self.assertEqual(info.get_locations(), set())
        self.assertEqual(info.get_names(), set())
        self.assertEqual(info.get_bands(), set())
