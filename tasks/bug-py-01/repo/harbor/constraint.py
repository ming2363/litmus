"""单条版本约束。"""

from typing import Tuple

from harbor.version import compare, parse_version


_OPERATORS = (">=", "<=", "==", "!=", ">", "<")


class Constraint:
    """用一个比较符约束可接受的版本。"""

    def __init__(self, operator: str, version: str) -> None:
        if operator not in _OPERATORS:
            raise ValueError("不支持的比较符: {}".format(operator))
        # 先解析，尽早拒绝非法版本。
        parse_version(version)
        self.operator = operator
        self.version = version

    def matches(self, candidate: str) -> bool:
        diff = compare(candidate, self.version)
        if self.operator == ">=":
            return diff >= 0
        if self.operator == ">":
            return diff > 0
        if self.operator == "<=":
            return diff <= 0
        if self.operator == "<":
            return diff < 0
        if self.operator == "==":
            return diff == 0
        return diff != 0

    def __repr__(self) -> str:
        return "Constraint({} {})".format(self.operator, self.version)


def parse_constraint(text: str) -> Constraint:
    """解析 `>=1.2.3` 这种单条约束。比较符与版本之间的空白会被忽略。"""
    if not isinstance(text, str):
        raise ValueError("约束必须是字符串")
    raw = text.strip()
    operator = ""
    for candidate in _OPERATORS:
        if raw.startswith(candidate):
            operator = candidate
            break
    if not operator:
        raise ValueError("无法识别约束: {}".format(text))
    version = raw[len(operator) :].strip()
    if not version:
        raise ValueError("约束缺少版本: {}".format(text))
    return Constraint(operator, version)


def explain_match(constraint: Constraint, candidate: str) -> Tuple[bool, int]:
    """返回是否满足，以及 compare 的原始差值，供目录页展示。"""
    diff = compare(candidate, constraint.version)
    return constraint.matches(candidate), diff
