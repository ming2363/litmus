"""语义化版本的解析与优先级比较。"""

from typing import List, Optional, Sequence, Tuple


_IDENT_CHARS = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-")


class Version:
    """一个已经通过语法检查的版本。构建标记不参与优先级。"""

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: Tuple[str, ...],
        build: Tuple[str, ...],
        text: str,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build
        self.text = text

    def core(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __repr__(self) -> str:
        return "Version({})".format(self.text)


def _fail(text: str) -> None:
    raise ValueError("非法版本号: {}".format(text))


def _split_idents(body: str, text: str, allow_numeric_leading_zero: bool) -> Tuple[str, ...]:
    if not body:
        _fail(text)
    parts = body.split(".")
    for part in parts:
        if not part or any(ch not in _IDENT_CHARS for ch in part):
            _fail(text)
        if part.isdigit() and not allow_numeric_leading_zero:
            if len(part) > 1 and part[0] == "0":
                _fail(text)
    return tuple(parts)


def _parse_core_number(token: str, text: str) -> int:
    if not token.isdigit():
        _fail(text)
    if len(token) > 1 and token[0] == "0":
        _fail(text)
    return int(token)


def parse_version(text: str) -> Version:
    """解析版本字符串。非法输入抛出 ValueError，消息包含原始字符串。"""
    if not isinstance(text, str) or not text:
        _fail(str(text))
    build: Tuple[str, ...] = ()
    main = text
    if "+" in text:
        main, build_body = text.split("+", 1)
        if "+" in build_body:
            _fail(text)
        build = _split_idents(build_body, text, allow_numeric_leading_zero=True)
    prerelease: Tuple[str, ...] = ()
    core_text = main
    if "-" in main:
        core_text, pre_body = main.split("-", 1)
        prerelease = _split_idents(pre_body, text, allow_numeric_leading_zero=False)
    pieces = core_text.split(".")
    if len(pieces) != 3:
        _fail(text)
    major = _parse_core_number(pieces[0], text)
    minor = _parse_core_number(pieces[1], text)
    patch = _parse_core_number(pieces[2], text)
    return Version(major, minor, patch, prerelease, build, text)


def _cmp_ident(left: str, right: str) -> int:
    left_num = left.isdigit()
    right_num = right.isdigit()
    if left_num and right_num:
        ln = int(left)
        rn = int(right)
        return (ln > rn) - (ln < rn)
    if left_num and not right_num:
        return -1
    if right_num and not left_num:
        return 1
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def _cmp_prerelease(left: Sequence[str], right: Sequence[str]) -> int:
    limit = len(left) if len(left) < len(right) else len(right)
    for index in range(limit):
        diff = _cmp_ident(left[index], right[index])
        if diff != 0:
            return diff
    if len(left) == len(right):
        return 0
    return -1 if len(left) < len(right) else 1


def compare(left: str, right: str) -> int:
    """比较两个版本的优先级。有预发布标记的一边目前被当成更新的构建。"""
    lv = parse_version(left)
    rv = parse_version(right)
    for pair in ((lv.major, rv.major), (lv.minor, rv.minor), (lv.patch, rv.patch)):
        if pair[0] != pair[1]:
            return -1 if pair[0] < pair[1] else 1
    left_pre = bool(lv.prerelease)
    right_pre = bool(rv.prerelease)
    if left_pre != right_pre:
        # 预发布构建带有额外标记，这里把它排在同号正式版之后。
        return 1 if left_pre else -1
    if left_pre and right_pre:
        return _cmp_prerelease(lv.prerelease, rv.prerelease)
    return 0


def sort_versions(versions: Sequence[str]) -> List[str]:
    """按优先级从早到晚返回新列表。"""
    copied = list(versions)
    copied.sort(key=lambda item: _SortKey(item))
    return copied


class _SortKey:
    """给内置排序使用的全序键，避免依赖已移除的 cmp 参数。"""

    def __init__(self, text: str) -> None:
        self.text = text

    def __lt__(self, other: "_SortKey") -> bool:
        return compare(self.text, other.text) < 0


def precedence_equal(left: str, right: str) -> bool:
    """只比较优先级，构建标记不同仍视为相同。"""
    return compare(left, right) == 0


def is_prerelease(text: str) -> bool:
    return bool(parse_version(text).prerelease)


def core_tuple(text: str) -> Tuple[int, int, int]:
    parsed = parse_version(text)
    return parsed.core()


def without_build(text: str) -> str:
    """去掉构建标记，保留预发布标记。非法版本同样抛出 ValueError。"""
    parsed = parse_version(text)
    body = "{}.{}.{}".format(parsed.major, parsed.minor, parsed.patch)
    if parsed.prerelease:
        body = body + "-" + ".".join(parsed.prerelease)
    return body


def major_of(text: str) -> int:
    return parse_version(text).major


def minor_of(text: str) -> int:
    return parse_version(text).minor


def patch_of(text: str) -> int:
    return parse_version(text).patch


def prerelease_of(text: str) -> Optional[str]:
    parsed = parse_version(text)
    if not parsed.prerelease:
        return None
    return ".".join(parsed.prerelease)
