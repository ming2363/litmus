"""摘录台账的可见示例。"""

import unittest

import markdown


class TestExcerptPublic(unittest.TestCase):
    """题面里的三个输入输出示例。"""

    def test_basic(self):
        md = markdown.Markdown(extensions=['excerpt'])
        html = md.convert(':::excerpt intro\n\nhello\n\n:::\n')
        self.assertEqual(html, '<p>hello</p>')
        self.assertEqual(len(md.excerpts), 1)
        excerpt = md.excerpts[0]
        self.assertEqual(excerpt.id, 'intro')
        self.assertEqual(excerpt.source, 'hello')
        self.assertEqual(excerpt.html, '<p>hello</p>')
        self.assertIs(md.get_excerpt('intro'), excerpt)

    def test_forward_ref(self):
        md = markdown.Markdown(extensions=['excerpt'])
        html = md.convert('see {@intro}\n\n:::excerpt intro\n\nhello\n\n:::\n')
        self.assertEqual(
            html,
            '<p>see <a class="excerpt-ref" href="#intro">intro</a></p>\n<p>hello</p>',
        )
        self.assertEqual(md.get_excerpt('intro').html, '<p>hello</p>')

    def test_wrapper(self):
        md = markdown.Markdown(
            extensions=['excerpt'],
            extension_configs={'excerpt': {'wrapper_class': 'callout'}},
        )
        html = md.convert(':::excerpt intro\n\nhello\n\n:::\n')
        self.assertEqual(
            html,
            '<div class="callout" id="intro">\n<p>hello</p>\n</div>',
        )
        self.assertEqual(md.excerpts[0].html, html)
        self.assertEqual(md.excerpts[0].source, 'hello')


if __name__ == '__main__':
    unittest.main()
