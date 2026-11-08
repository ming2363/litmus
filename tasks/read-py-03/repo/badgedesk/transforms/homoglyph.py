"""把常见全角数字折成半角"""


def fold_homoglyph_digits(text):
    """把常见全角数字折成半角"""
    if not isinstance(text, str):
        raise TypeError("text")
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


class DigitStep(object):
    """落库步骤。"""

    def apply(self, text):
        return fold_homoglyph_digits(text)
