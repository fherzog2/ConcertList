from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import concert_list
import dates_grid_view
import datetime


def format_date(date: datetime.date):
    qdate = QDate(date.year, date.month, date.day)
    return QLocale.system().toString(qdate, "dd.MM.yyyy")


class NumericSortTableWidgetItem(QTableWidgetItem):
    """ Special table item which uses a QCollator for sorting. """

    def __init__(self, text: str, collator: QCollator):
        super().__init__(text)
        self.collator = collator

    def __lt__(self, other):
        return self.collator.compare(self.text(), other.text()) < 0

    def clone(self):
        return NumericSortTableWidgetItem(self.text(), self.collator)


class DateTableWidgetItem(QTableWidgetItem):
    def __init__(self, date: datetime.date):
        super().__init__()
        self.setText(format_date(date))
        self.date = date

    def __lt__(self, other):
        return self.date < other.date

    def clone(self):
        return DateTableWidgetItem(self.date)


class ConcertListView(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.collator = QCollator()
        self.collator.setNumericMode(True)

        self.table = QTableWidget(self)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

    def rebuild_table(self, header, data, sort_column: int, sort_order: Qt.SortOrder):
        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(header))
        self.table.setHorizontalHeaderLabels(header)

        for row, row_data in enumerate(data):
            for column, value in enumerate(row_data):
                if isinstance(value, datetime.date):
                    item = DateTableWidgetItem(value)
                else:
                    item = NumericSortTableWidgetItem(str(value), self.collator)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, column, item)

        self.table.resizeColumnsToContents()
        self.table.sortItems(sort_column, sort_order)
        self.table.setSortingEnabled(True)

    def dump(self):
        rows = []
        if self.table.isVisibleTo(self):
            header = []
            for c in range(self.table.columnCount()):
                header.append(self.table.horizontalHeaderItem(c).text())
            rows.append(";".join(header))

            for r in range(self.table.rowCount()):
                row = []
                for c in range(self.table.columnCount()):
                    row.append(self.table.item(r, c).text())
                rows.append(";".join(row))

        return "\n".join(rows)


class ConcertListViewUnfiltered(ConcertListView):
    def __init__(self, parent):
        super().__init__(parent)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        data = []
        for concert in concert_list_model.get_concerts():
            data.append([concert.date, concert.location, concert.name, ", ".join(concert.bands)])

        self.rebuild_table(["Date", "Location", "Name", "Bands"], data, 0, Qt.SortOrder.DescendingOrder)


class ConcertListViewConcertsGroupedByBand(ConcertListView):
    def __init__(self, parent):
        super().__init__(parent)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        data = []
        for concert in concert_list_model.get_concerts():
            for band in concert.bands:
                data.append([concert.date, concert.location, concert.name, band])

        self.rebuild_table(["Date", "Location", "Name", "Band"], data, 3, Qt.SortOrder.AscendingOrder)


class ConcertListViewMostSeenBands(ConcertListView):
    def __init__(self, parent):
        super().__init__(parent)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        times_seen = dict()

        for concert in concert_list_model.get_concerts():
            for band in concert.bands:
                times_seen[band] = times_seen.get(band, 0) + 1

        data = []
        for band, times in times_seen.items():
            data.append([band, times])

        self.rebuild_table(["Band", "Times Seen"], data, 1, Qt.SortOrder.DescendingOrder)


class ConcertListViewConcertsPerYear(ConcertListView):
    def __init__(self, parent):
        super().__init__(parent)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        class YearValues:
            def __init__(self):
                self.bands = 0
                self.distinct_bands = set()
                self.concerts = 0
                self.festivals = set()

        year_map: dict[int, YearValues] = dict()

        for concert in concert_list_model.get_concerts():
            year = concert.date.year
            year_map[year] = year_map.get(year, YearValues())
            values = year_map[year]

            values.bands += len(concert.bands)
            if concert.festival:
                values.festivals.add(concert.name)
            else:
                values.concerts += 1

            for band in concert.bands:
                values.distinct_bands.add(band)

        total_bands = 0
        total_distinct_bands = set()
        total_concerts = 0
        total_festivals = 0

        data = []
        for year, values in year_map.items():
            data.append([year, values.bands, len(values.distinct_bands), values.concerts, len(values.festivals)])

            total_bands += values.bands
            total_distinct_bands = total_distinct_bands.union(values.distinct_bands)
            total_concerts += values.concerts
            total_festivals += len(values.festivals)

        data.append(["Total", total_bands, len(total_distinct_bands), total_concerts, total_festivals])

        self.rebuild_table(["Year", "Bands", "Distinct Bands", "Concerts", "Festivals"], data, 0, Qt.SortOrder.AscendingOrder)


class ConcertListViewFestivals(ConcertListView):
    def __init__(self, parent):
        super().__init__(parent)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        class FestivalValues:
            def __init__(self, concert: concert_list.Concert):
                self.startdate = concert.date
                self.location = concert.location
                self.name = concert.name
                self.bands_seen = 0

        festival_map: dict[str, FestivalValues] = dict()

        for concert in concert_list_model.get_concerts():
            if not concert.festival:
                continue

            festival_key = str(concert.date.year) + concert.name + concert.location
            festival_map[festival_key] = festival_map.get(festival_key, FestivalValues(concert))
            festival_map[festival_key].bands_seen += len(concert.bands)

        data = []
        for values in festival_map.values():
            data.append([values.startdate, values.location, values.name, values.bands_seen])

        self.rebuild_table(["Start date", "Location", "Name", "Bands seen"], data, 0, Qt.SortOrder.AscendingOrder)


class ConcertListViewLocations(ConcertListView):
    def __init__(self, parent):
        super().__init__(parent)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        location_map = dict()
        festival_year_set = set()

        for concert in concert_list_model.get_concerts():
            if concert.festival:
                festival_key = str(concert.date.year) + concert.name
                if festival_key in festival_year_set:
                    # prevent counting the same festival multiple times
                    continue

                festival_year_set.add(festival_key)

            location_map[concert.location] = location_map.get(concert.location, 0) + 1

        data = []
        for location, count in location_map.items():
            data.append([location, count])

        self.rebuild_table(["Location", "Concerts"], data, 0, Qt.SortOrder.AscendingOrder)


class ConcertListViewGrid(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_view = dates_grid_view.DatesGridView(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.grid_view)

    def set_model(self, concert_list_model: concert_list.ConcertListModel):
        values = []

        for concert in concert_list_model.get_concerts():
            tooltip_lines = [format_date(concert.date)]
            if len(concert.name) > 0:
                tooltip_lines.append(concert.name)
            tooltip_lines.append(concert.location)
            tooltip_lines.append("")
            tooltip_lines += concert.bands

            tooltip = "\n".join(tooltip_lines)
            value = dates_grid_view.DateGridValue(concert.date, len(concert.bands), tooltip)
            values.append(value)

        self.grid_view.set_values(values)

    def dump(self):
        if self.grid_view.isVisibleTo(self):
            return self.grid_view.dump()
        else:
            return []
