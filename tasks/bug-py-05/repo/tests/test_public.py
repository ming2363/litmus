import unittest

from booking.calendar import BookingCalendar
from booking.merge import merge_intervals


class TestPublic(unittest.TestCase):
    def test_empty_and_single(self):
        self.assertEqual(merge_intervals([]), [])
        self.assertEqual(merge_intervals([(1, 4)]), [(1, 4)])

    def test_overlap_touch_and_gap(self):
        self.assertEqual(merge_intervals([(0, 2), (1, 5), (8, 9)]), [(0, 5), (8, 9)])
        self.assertEqual(merge_intervals([(0, 2), (2, 4)]), [(0, 4)])
        self.assertEqual(merge_intervals([(5, 6), (0, 1)]), [(0, 1), (5, 6)])

    def test_nested_and_duplicates(self):
        self.assertEqual(merge_intervals([(0, 10), (2, 3), (4, 8)]), [(0, 10)])
        self.assertEqual(merge_intervals([(-3, -1), (-1, 2), (4, 5)]), [(-3, 2), (4, 5)])

    def test_reject_invalid(self):
        for bad in ([(1, 1)], [(2, 1)], [(True, 2)], [(1, 1.5)], ["ab"]):
            with self.assertRaises(ValueError):
                merge_intervals(bad)

    def test_calendar_ranges(self):
        calendar = BookingCalendar.from_pairs([(3, 5), (1, 2), (2, 3)])
        self.assertEqual(calendar.ranges(), [(1, 5)])
        self.assertEqual(calendar.raw_count(), 3)
        calendar.add(8, 9)
        self.assertEqual(calendar.ranges(), [(1, 5), (8, 9)])
