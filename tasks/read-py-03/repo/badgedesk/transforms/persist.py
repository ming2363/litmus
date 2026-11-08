"""列宽 16，多出的截掉"""


def clip_to_column(text):
    """列宽 16，多出的截掉"""
    if not isinstance(text, str):
        raise TypeError("text")
    return text[:16]


class WidthStep(object):
    """落库步骤。"""

    def apply(self, text):
        return clip_to_column(text)
