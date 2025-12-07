from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import calendar
import datetime


class DateGridValue:
    def __init__(self, date, value, tooltip):
        self.date: datetime.date = date
        self.value: int = value
        self.tooltip: str = tooltip


class DatesGridView(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.year_select = QComboBox(self)
        self.year_select.currentIndexChanged.connect(self.year_changed)

        self.grid_container = QStackedWidget(self)
        self.grid = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.year_select, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.grid_container, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

    def set_values(self, values: list[DateGridValue]):
        if len(values) == 0:
            return

        self.values = values

        years = map(lambda v: v.date.year, values)
        unique_years = list(set(years))

        self.year_select.clear()

        for year in reversed(unique_years):
            self.year_select.addItem(str(year), year)

        self.year_changed()

    def year_changed(self):
        if self.year_select.count() == 0:
            return

        year = self.year_select.currentData()

        if self.grid is not None:
            self.grid.deleteLater()

        self.grid = self.create_year_grid(self.values, year)
        self.grid_container.addWidget(self.grid)

    def show_year(self, year):
        for i in range(self.year_select.count()):
            if self.year_select.itemData(i) == year:
                self.year_select.setCurrentIndex(i)
                break

    def create_year_grid(self, values: list[DateGridValue], year):
        year_values = filter(lambda v: v.date.year == year, values)
        max_value = max(map(lambda v: v.value, year_values))

        grid = QFrame(self)
        grid_layout = QGridLayout(grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        cell_map = dict()

        for i, day in enumerate(calendar.day_name):
            grid_layout.addWidget(QLabel(day, self), i, 0)

        week = 1
        for date in self.get_dates_in_year(year):
            iso = date.isocalendar()

            cell = QFrame(grid)
            cell.setFixedSize(16, 16)
            cell.setStyleSheet("background:rgb(224, 224, 224);")
            cell.setProperty("date", date)

            cell_map[date] = cell

            # weekday should start at 0
            # week starts at 1, because there are labels in the first column
            grid_layout.addWidget(cell, iso.weekday - 1, week)

            if iso.weekday == 7:
                week += 1

        for value in values:
            try:
                cell: QFrame = cell_map[value.date]
                brightness = value.value*255/max_value
                cell.setStyleSheet(f"background:rgb(0, 0, {brightness});")
                cell.setProperty("value", value.value)
                cell.setToolTip(value.tooltip)
            except KeyError:
                pass

        return grid

    def get_dates_in_year(self, year):
        for month in range(1, 13):
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                yield datetime.date(year, month, day)

    def dump(self):
        lines = []

        lines.append(f"Year {self.year_select.currentData()}")

        grid_layout: QGridLayout = self.grid.layout()

        lines.append(f"{grid_layout.columnCount()} columns, {grid_layout.rowCount()} rows")

        items = []

        for column in range(grid_layout.columnCount()):
            column_list = []
            for row in range(grid_layout.rowCount()):
                item = grid_layout.itemAtPosition(row, column)

                if item is not None and item.widget().property("value"):
                    value = item.widget().property("value")
                    date = item.widget().property("date")
                    items.append(f"Item at ({column},{row}), value: {value}, date: {date}")

                if item is None:
                    column_list.append(None)
                else:
                    column_list.append(str(item.widget().property("date")))

            if None in column_list:
                lines.append(f"Column {column} has gaps: {column_list}")

        lines += items

        return "\n".join(lines)
