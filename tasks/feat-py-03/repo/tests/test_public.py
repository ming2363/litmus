import unittest

from src.planner import find_min_steps, parse_grid


class TestPublic(unittest.TestCase):
    def test_stage1_basic_shortest_steps(self):
        grid = parse_grid([
            "..#..",
            ".#.#.",
            ".....",
        ])
        self.assertEqual(find_min_steps(grid, (0, 0), (0, 4)), 8)
        self.assertEqual(find_min_steps(grid, (0, 0), (0, 0)), 0)
        self.assertIsNone(find_min_steps(grid, (0, 0), (0, 2)))

    def test_stage1_unreachable_and_validation(self):
        grid = [
            ".#.",
            "###",
            "...",
        ]
        self.assertIsNone(find_min_steps(grid, (0, 0), (2, 2)))
        with self.assertRaises(ValueError):
            find_min_steps(grid, (-1, 0), (0, 0))


if __name__ == "__main__":
    unittest.main()
