"""从目录里为每条依赖选出最新的可用构建。"""

from typing import Dict, List, Sequence, Tuple

from harbor.catalog import Catalog
from harbor.constraint import parse_constraint
from harbor.version import compare


class Dependency:
    """组件名加一条约束。"""

    def __init__(self, name: str, constraint: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("组件名不能为空")
        self.name = name
        self.constraint = parse_constraint(constraint)

    def __repr__(self) -> str:
        return "Dependency({} {})".format(self.name, self.constraint)


def resolve(catalog: Catalog, dependencies: Sequence[Dependency]) -> Dict[str, str]:
    """返回 {组件名: 版本}。同一组件出现多次时，后出现的约束覆盖前面的结果。

    没有满足约束的构建时抛出 KeyError，异常消息包含组件名。
    """
    chosen: Dict[str, str] = {}
    for dep in dependencies:
        candidates = catalog.satisfying(dep.name, dep.constraint)
        if not candidates:
            raise KeyError(dep.name)
        chosen[dep.name] = candidates[-1]
    return chosen


def explain(catalog: Catalog, dep: Dependency) -> List[Tuple[str, int]]:
    """列出该组件全部构建相对约束版本的 compare 差值，按版本从早到晚。"""
    rows = []
    for version in catalog.versions(dep.name):
        rows.append((version, compare(version, dep.constraint.version)))
    return rows
