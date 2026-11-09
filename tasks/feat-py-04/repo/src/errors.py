"""参数错误都用内建异常，不另起类型。"""


class LimitError(ValueError):
    """保留给旧草稿的别名。现行入口仍抛 ValueError。"""
