import concert_adder
import unittest


class TestConcertAdder(unittest.TestCase):
    def test_sort_numeric(self):
        s = concert_adder.sort_numeric(["1", "10", "100", "2", "30", "4", "a", "A", "B", "c"])
        self.assertEqual(s, ['1', '2', '4', '10', '30', '100', 'a', 'A', 'B', 'c'])
