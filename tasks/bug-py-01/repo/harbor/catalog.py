"""按组件名收集构建，并挑出最新版本或满足约束的版本。"""

from typing import Dict, List, Sequence

from harbor.constraint import Constraint, parse_constraint
from harbor.version import compare, parse_version, sort_versions


class Catalog:
    """内存中的组件发布目录。同名同版本重复登记会被忽略。"""

    def __init__(self) -> None:
        self._builds: Dict[str, List[str]] = {}

    def add(self, name: str, version: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("组件名不能为空")
        parse_version(version)
        bucket = self._builds.setdefault(name, [])
        if version not in bucket:
            bucket.append(version)

    def names(self) -> List[str]:
        return sorted(self._builds)

    def versions(self, name: str) -> List[str]:
        self._require(name)
        return sort_versions(self._builds[name])

    def latest(self, name: str) -> str:
        ordered = self.versions(name)
        return ordered[-1]

    def satisfying(self, name: str, constraint: str) -> List[str]:
        parsed = constraint if isinstance(constraint, Constraint) else parse_constraint(constraint)
        ordered = self.versions(name)
        return [item for item in ordered if parsed.matches(item)]

    def count(self, name: str) -> int:
        self._require(name)
        return len(self._builds[name])

    def earliest(self, name: str) -> str:
        return self.versions(name)[0]

    def newer_than(self, name: str, version: str) -> List[str]:
        """返回严格晚于给定版本的构建。"""
        parse_version(version)
        ordered = self.versions(name)
        return [item for item in ordered if compare(item, version) > 0]

    def _require(self, name: str) -> None:
        if name not in self._builds:
            raise KeyError(name)


def load_pairs(pairs: Sequence[Sequence[str]]) -> Catalog:
    """从 (组件名, 版本) 序列建立目录。"""
    catalog = Catalog()
    for pair in pairs:
        if len(pair) != 2:
            raise ValueError("每一项必须是组件名和版本")
        catalog.add(pair[0], pair[1])
    return catalog
