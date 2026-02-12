from PyQt6.QtWidgets import *
import concert_list_view
import concert_list
import example_data
import unittest


class TestApp:
    def __init__(self):
        self.app = QApplication([])

        self.model = concert_list.ConcertListModel()
        self.model.set_concerts(example_data.get_example_concerts())

    def show_view(self, view: concert_list_view.ConcertListView):
        self.view = view
        self.view.set_model(self.model)


class TestConcertListView(unittest.TestCase):
    def test_default_view(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewUnfiltered(None))
        expected = r"""Date;Location;Name;Bands
29.06.2024;Clisson;Hellfest;Mammoth WVH, Kataklysm, Metallica
28.06.2024;Clisson;Hellfest;Fear Factory, Machine Head, The Prodigy
24.05.2024;München, Olympiastadion;;Mammoth WVH, Architects, Metallica
02.02.2024;Hamburg, Grosse Freiheit 36;;Chaosbay, Flash Forward, Emil Bulls
02.02.2024;Hamburg, Gruenspan;;Any Given Day"""
        self.assertEqual(app.view.dump(), expected)

    def test_concerts_grouped_by_band(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewConcertsGroupedByBand(None))
        expected = r"""Date;Location;Name;Band
02.02.2024;Hamburg, Gruenspan;;Any Given Day
24.05.2024;München, Olympiastadion;;Architects
02.02.2024;Hamburg, Grosse Freiheit 36;;Chaosbay
02.02.2024;Hamburg, Grosse Freiheit 36;;Emil Bulls
28.06.2024;Clisson;Hellfest;Fear Factory
02.02.2024;Hamburg, Grosse Freiheit 36;;Flash Forward
29.06.2024;Clisson;Hellfest;Kataklysm
28.06.2024;Clisson;Hellfest;Machine Head
24.05.2024;München, Olympiastadion;;Mammoth WVH
29.06.2024;Clisson;Hellfest;Mammoth WVH
24.05.2024;München, Olympiastadion;;Metallica
29.06.2024;Clisson;Hellfest;Metallica
28.06.2024;Clisson;Hellfest;The Prodigy"""
        self.assertEqual(app.view.dump(), expected)

    def test_most_seen_bands(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewMostSeenBands(None))
        expected = r"""Band;Times Seen
Mammoth WVH;2
Metallica;2
Any Given Day;1
Architects;1
Chaosbay;1
Emil Bulls;1
Fear Factory;1
Flash Forward;1
Kataklysm;1
Machine Head;1
The Prodigy;1"""
        self.assertEqual(app.view.dump(), expected)

    def test_concerts_per_year(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewConcertsPerYear(None))
        expected = r"""Year;Bands;Distinct Bands;Concerts;Festivals
2024;13;11;3;1
Total;13;11;3;1"""
        self.assertEqual(app.view.dump(), expected)

    def test_festivals(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewFestivals(None))
        expected = r"""Start date;Location;Name;Bands seen
28.06.2024;Clisson;Hellfest;6"""
        self.assertEqual(app.view.dump(), expected)

    def test_locations(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewLocations(None))
        expected = r"""Location;Concerts
Clisson;1
Hamburg, Grosse Freiheit 36;1
Hamburg, Gruenspan;1
München, Olympiastadion;1"""
        self.assertEqual(app.view.dump(), expected)

    def test_grid(self):
        app = TestApp()
        app.show_view(concert_list_view.ConcertListViewGrid(None))
        expected = r"""Year 2024
54 columns, 7 rows
Column 53 has gaps: ['2024-12-30', '2024-12-31', None, None, None, None, None]
Item at (5,4), value: 4, date: 2024-02-02
Item at (21,4), value: 3, date: 2024-05-24
Item at (26,4), value: 3, date: 2024-06-28
Item at (26,5), value: 3, date: 2024-06-29"""
        self.assertEqual(app.view.dump(), expected)
