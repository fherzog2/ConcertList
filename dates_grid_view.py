from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import calendar
import collections
import datetime


class DatesGridModelDay:
    def __init__(self):
        self.value: int = 0
        self.tooltip: list[str] = []

    def add(self, value: int, tooltip: str):
        self.value += value
        self.tooltip.append(tooltip)

    def get_tooltip(self) -> str:
        return "\n\n".join(self.tooltip)


class DatesGridModelYear:
    def __init__(self):
        self.days = collections.defaultdict(DatesGridModelDay)

    def add_value(self, date: datetime.date, value: int, tooltip: str):
        self.days[date].add(value, tooltip)

    def get_days_with_values(self):
        return self.days.items()

    def get_max_value(self) -> int:
        return max(map(lambda v: v.value, self.days.values()))


class DatesGridModel:
    def __init__(self):
        self.years = collections.defaultdict(DatesGridModelYear)

    def add_value(self, date: datetime.date, value: int, tooltip: str):
        self.years[date.year].add_value(date, value, tooltip)

    def is_empty(self) -> bool:
        return len(self.years) == 0

    def get_years(self):
        return self.years.keys()

    def get_year_values(self, year) -> DatesGridModelYear:
        return self.years.get(year, None)


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

    def set_values(self, model: DatesGridModel):
        self.model = model

        years = self.model.get_years()

        self.year_select.clear()

        for year in reversed(years):
            self.year_select.addItem(str(year), year)

        self.year_changed()

    def year_changed(self):
        year = self.year_select.currentData()

        if self.grid is not None:
            self.grid.deleteLater()
            self.grid = None

        if year is None:
            return

        self.grid = self.create_year_grid(self.model.get_year_values(year), year)
        self.grid_container.addWidget(self.grid)

    def show_year(self, year):
        for i in range(self.year_select.count()):
            if self.year_select.itemData(i) == year:
                self.year_select.setCurrentIndex(i)
                break

    def create_year_grid(self, year_model: DatesGridModelYear, year):
        max_value = year_model.get_max_value()

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

        for date, day in year_model.get_days_with_values():
            try:
                cell: QFrame = cell_map[date]
                brightness = day.value*255/max_value
                cell.setStyleSheet(f"background:rgb(0, 0, {brightness});")
                cell.setProperty("value", day.value)
                cell.setToolTip(day.get_tooltip())
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

        if self.grid is not None:
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
