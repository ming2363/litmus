"""去掉中间空格"""


def strip_inner_spaces(text):
    """去掉中间空格"""
    if not isinstance(text, str):
        raise TypeError("text")
    return "".join(text.split())


class GapStep(object):
    """落库步骤。"""

    def apply(self, text):
        return strip_inner_spaces(text)
