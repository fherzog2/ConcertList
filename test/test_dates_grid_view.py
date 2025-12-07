from PyQt6.QtWidgets import *
import dates_grid_view
import datetime
import unittest


class TestDatesGridView(unittest.TestCase):
    def test_empty_grid(self):
        app = QApplication([])

        grid = dates_grid_view.DatesGridView(None)

        values = []

        for year in range(2020, 2026):
            values.append(dates_grid_view.DateGridValue(datetime.date(year, 1, 1), 1, ""))

        grid.set_values(values)

        with self.subTest(msg='2021'):
            grid.show_year(2021)
            expected = r"""Year 2021
54 columns, 7 rows
Column 1 has gaps: [None, None, None, None, '2021-01-01', '2021-01-02', '2021-01-03']
Column 53 has gaps: ['2021-12-27', '2021-12-28', '2021-12-29', '2021-12-30', '2021-12-31', None, None]
Item at (1,4), value: 1, date: 2021-01-01"""
            self.assertEqual(grid.dump(), expected)

        with self.subTest(msg='2022'):
            grid.show_year(2022)
            expected = r"""Year 2022
54 columns, 7 rows
Column 1 has gaps: [None, None, None, None, None, '2022-01-01', '2022-01-02']
Column 53 has gaps: ['2022-12-26', '2022-12-27', '2022-12-28', '2022-12-29', '2022-12-30', '2022-12-31', None]
Item at (1,5), value: 1, date: 2022-01-01"""
            self.assertEqual(grid.dump(), expected)

        with self.subTest(msg='2023'):
            grid.show_year(2023)
            expected = r"""Year 2023
54 columns, 7 rows
Column 1 has gaps: [None, None, None, None, None, None, '2023-01-01']
Item at (1,6), value: 1, date: 2023-01-01"""
            self.assertEqual(grid.dump(), expected)

        with self.subTest(msg='2024'):
            grid.show_year(2024)
            expected = r"""Year 2024
54 columns, 7 rows
Column 53 has gaps: ['2024-12-30', '2024-12-31', None, None, None, None, None]
Item at (1,0), value: 1, date: 2024-01-01"""
            self.assertEqual(grid.dump(), expected)

        with self.subTest(msg='2025'):
            grid.show_year(2025)
            expected = r"""Year 2025
54 columns, 7 rows
Column 1 has gaps: [None, None, '2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']
Column 53 has gaps: ['2025-12-29', '2025-12-30', '2025-12-31', None, None, None, None]
Item at (1,2), value: 1, date: 2025-01-01"""
            self.assertEqual(grid.dump(), expected)
