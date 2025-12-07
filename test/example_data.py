import concert_list
import datetime


def get_example_concerts():
    c1 = concert_list.create_concert(datetime.date(2024, 5, 24), "München, Olympiastadion", ["Mammoth WVH", "Architects", "Metallica"])
    c2 = concert_list.create_concert(datetime.date(2024, 6, 28), "Clisson", ["Fear Factory", "Machine Head", "The Prodigy"], "Hellfest", True)
    c3 = concert_list.create_concert(datetime.date(2024, 6, 29), "Clisson", ["Mammoth WVH", "Kataklysm", "Metallica"], "Hellfest", True)
    return [c1, c2, c3]


def get_example_yaml_str():
    with open("test/example_data.yaml", "r", encoding="utf8") as f:
        return f.read()
