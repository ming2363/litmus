"""调用上下文。"""


class Context(object):
    """单位与备注。"""

    def __init__(self, unit, rows):
        self.unit = unit
        self.rows = list(rows)
        self.notes = []
