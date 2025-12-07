import yaml
import os
import datetime
from typing import Any


class Concert:
    def __init__(self, map: dict[str, Any]):
        self.date: datetime.date = map["date"]
        self.location: str = map["location"]
        self.bands: str = map["bands"]
        self.name: str = map.get("name", "")
        self.festival: bool = map.get("festival", False)


class ConcertListModel:
    def __init__(self):
        self.concerts = []

    def load_file(self, filepath: str):
        with open(filepath, "r", encoding="utf8") as f:
            content = f.read()

            concerts = load_concerts(content)
            if concerts is not None:
                self.concerts = concerts

    def save_file(self, filepath: str):
        content = dump_concerts(self.concerts)
        safe_write_file(filepath, content)

    def add_concert(self, concert: dict[str, Any]):
        self.concerts.append(concert)

    def get_concerts(self) -> list[Concert]:
        concerts = []
        for concert in self.concerts:
            concerts.append(Concert(concert))
        return concerts

    def set_concerts(self, concerts: list[dict[str, Any]]):
        self.concerts = concerts


class ConcertListInfo:
    def __init__(self, model: ConcertListModel):
        self.concerts = model.get_concerts()

    def get_number_of_concerts(self):
        return len(self.concerts)

    def get_locations(self):
        result = set()

        for c in self.concerts:
            result.add(c.location)

        return result

    def get_names(self):
        result = set()

        for c in self.concerts:
            if len(c.name) > 0:
                result.add(c.name)

        return result

    def get_bands(self):
        result = set()

        for c in self.concerts:
            for b in c.bands:
                result.add(b)

        return result


def create_concert(date, location, bands, name="", festival=False) -> dict[str, Any]:
    concert = {"date": date, "location": location, "bands": bands}
    if len(name) > 0:
        concert["name"] = name
    if festival:
        concert["festival"] = festival
    return concert


def dump_concerts(concerts):
    return yaml.dump(concerts, allow_unicode=True)


def load_concerts(data):
    return yaml.safe_load(data)


def safe_write_file(filepath: str, content):
    if os.path.exists(filepath):
        filepath_tmp = filepath + ".tmp"
        filepath_bak = filepath + ".bak"

        with open(filepath_tmp, "w", encoding="utf8") as f:
            f.write(content)

        os.rename(filepath, filepath_bak)
        os.rename(filepath_tmp, filepath)
        os.remove(filepath_bak)
    else:
        with open(filepath, "w", encoding="utf8") as f:
            f.write(content)


def add_concert_to_file(filepath: str, concert: dict[str, Any]):
    model = ConcertListModel()
    model.load_file(filepath)
    model.add_concert(concert)
    model.save_file(filepath)
