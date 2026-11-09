"""调度台能直接跑到的检查。"""

import unittest

from tidebook.span import check_minute, cut_minutes, fold_minutes
from wharfbook import WharfLedger
from wharfbook.dwell import billable_spans, open_spans


class TestTide(unittest.TestCase):
    def test_touching_merges(self) -> None:
        self.assertEqual(fold_minutes([(0, 10), (10, 20)]), [(0, 20)])

    def test_one_minute_gap_stays(self) -> None:
        self.assertEqual(fold_minutes([(0, 10), (11, 20)]), [(0, 10), (11, 20)])

    def test_contained_span_is_absorbed(self) -> None:
        self.assertEqual(fold_minutes([(0, 30), (5, 10)]), [(0, 30)])

    def test_bridge_span_joins_both_sides(self) -> None:
        self.assertEqual(fold_minutes([(0, 10), (20, 30), (10, 20)]), [(0, 30)])

    def test_closure_splits_middle(self) -> None:
        self.assertEqual(cut_minutes([(0, 20)], [(5, 10)]), [(0, 5), (10, 20)])

    def test_closure_touching_start_keeps_window(self) -> None:
        self.assertEqual(cut_minutes([(10, 20)], [(0, 10)]), [(10, 20)])

    def test_adjacent_closures_leave_the_tail(self) -> None:
        self.assertEqual(cut_minutes([(0, 30)], [(0, 10), (10, 20)]), [(20, 30)])

    def test_bool_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_minute(True)
        with self.assertRaises(ValueError):
            fold_minutes([(True, 2)])

    def test_inputs_stay_put(self) -> None:
        spans = [(10, 20), (0, 10)]
        snapshot = list(spans)
        fold_minutes(spans)
        self.assertEqual(spans, snapshot)

    def test_dwell_uses_the_same_minutes(self) -> None:
        self.assertEqual(billable_spans([(0, 10), (10, 15)]), [(0, 15)])
        self.assertEqual(open_spans([(0, 20)], [(5, 8)]), [(0, 5), (8, 20)])


class TestWharfStable(unittest.TestCase):
    def test_empty_holds(self) -> None:
        self.assertEqual(WharfLedger().plan([], []), [])

    def test_single_hold(self) -> None:
        self.assertEqual(WharfLedger().plan([(0, 10, "A")], []), [(0, 10, "A")])

    def test_gap_stays_split(self) -> None:
        got = WharfLedger().plan([(0, 10, "A"), (11, 20, "A")], [])
        self.assertEqual(got, [(0, 10, "A"), (11, 20, "A")])

    def test_different_lanes_stay_apart(self) -> None:
        got = WharfLedger().plan([(0, 10, "A"), (0, 10, "B")], [])
        self.assertEqual(got, [(0, 10, "A"), (0, 10, "B")])

    def test_other_lane_touch_stays_apart(self) -> None:
        got = WharfLedger().plan([(0, 10, "A"), (10, 20, "B")], [])
        self.assertEqual(got, [(0, 10, "A"), (10, 20, "B")])

    def test_block_far_outside(self) -> None:
        got = WharfLedger().plan([(0, 10, "A")], [(20, 30)])
        self.assertEqual(got, [(0, 10, "A")])

    def test_block_touching_the_end(self) -> None:
        got = WharfLedger().plan([(0, 10, "A")], [(10, 12)])
        self.assertEqual(got, [(0, 10, "A")])

    def test_block_covers_the_hold(self) -> None:
        self.assertEqual(WharfLedger().plan([(0, 10, "A")], [(0, 10)]), [])

    def test_reversed_range_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WharfLedger().plan([(5, 5, "A")], [])

    def test_lane_must_be_text(self) -> None:
        with self.assertRaises(ValueError):
            WharfLedger().plan([(0, 1, 3)], [])

    def test_blank_lane_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WharfLedger().plan([(0, 1, "  ")], [])

    def test_hold_shape(self) -> None:
        with self.assertRaises(ValueError):
            WharfLedger().plan([(0, 1)], [])

    def test_large_minute(self) -> None:
        huge = 10 ** 18
        got = WharfLedger().plan([(0, huge, "A")], [])
        self.assertEqual(got, [(0, huge, "A")])


class TestWharfReported(unittest.TestCase):
    def test_touching_same_lane(self) -> None:
        got = WharfLedger().plan([(0, 10, "A"), (10, 20, "A")], [])
        self.assertEqual(got, [(0, 20, "A")])
