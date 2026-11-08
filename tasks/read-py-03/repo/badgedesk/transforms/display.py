"""展示用引号，不进库"""


def wrap_display_quotes(text):
    """展示用引号，不进库"""
    if not isinstance(text, str):
        raise TypeError("text")
    return '"' + text + '"'


class QuoteStep(object):
    """展示步骤，不进库。"""

    def apply(self, text):
        return wrap_display_quotes(text)
