"""日志副本打码，不进库"""


def redact_for_log(text):
    """日志副本打码，不进库"""
    if not isinstance(text, str):
        raise TypeError("text")
    return text[:2] + "***" if text else ""


class MaskStep(object):
    """日志步骤，不进库。"""

    def apply(self, text):
        return redact_for_log(text)
