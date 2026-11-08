"""字母折成大写"""


def fold_badge_case(text):
    """字母折成大写"""
    if not isinstance(text, str):
        raise TypeError("text")
    return text.upper()


class UpperStep(object):
    """落库步骤。"""

    def apply(self, text):
        return fold_badge_case(text)
