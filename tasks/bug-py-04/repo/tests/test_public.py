import unittest

from snippets.preview import card
from snippets.truncate import grapheme_length, truncate_graphemes


class TestPublic(unittest.TestCase):
    def test_ascii_and_cjk(self):
        self.assertEqual(grapheme_length("hello"), 5)
        self.assertEqual(truncate_graphemes("hello", 2), "he")
        self.assertEqual(grapheme_length("你好世界"), 4)
        self.assertEqual(truncate_graphemes("你好世界", 2), "你好")

    def test_limit_edges(self):
        self.assertEqual(truncate_graphemes("abc", 0), "")
        self.assertEqual(truncate_graphemes("abc", 10), "abc")
        self.assertEqual(grapheme_length(""), 0)

    def test_reject_bad_limit(self):
        with self.assertRaises(ValueError) as caught:
            truncate_graphemes("abc", -1)
        self.assertIn("limit", str(caught.exception))
        with self.assertRaises(TypeError):
            truncate_graphemes("abc", True)
        with self.assertRaises(TypeError):
            grapheme_length(None)

    def test_card_ascii(self):
        preview = card("标题一二三四", "正文保持不变", 2, 20)
        self.assertEqual(preview, {"title": "标题", "body": "正文保持不变"})
