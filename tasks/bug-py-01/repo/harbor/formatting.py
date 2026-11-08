"""把目录里的版本整理成固定宽度的文本表。"""

from typing import List

from harbor.catalog import Catalog
from harbor.version import is_prerelease, without_build


def format_component(catalog: Catalog, name: str) -> str:
    """每个版本一行：序号、去构建标记后的版本、是否预发布、原始字符串。"""
    lines: List[str] = ["# {}".format(name)]
    for index, version in enumerate(catalog.versions(name), start=1):
        kind = "pre" if is_prerelease(version) else "rel"
        lines.append(
            "{:>3}  {:<24}  {:<3}  {}".format(index, without_build(version), kind, version)
        )
    return "\n".join(lines)


def format_catalog(catalog: Catalog) -> str:
    blocks = [format_component(catalog, name) for name in catalog.names()]
    return "\n\n".join(blocks)
