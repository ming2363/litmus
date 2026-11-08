"""harbor 版本目录使用的异常。"""


class HarborError(Exception):
    """版本目录的基类异常。"""


class UnknownComponent(HarborError, KeyError):
    """目录里没有这个组件。"""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__("未知组件: {}".format(name))
