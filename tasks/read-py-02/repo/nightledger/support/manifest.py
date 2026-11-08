"""简单行协议：KEY=VALUE，# 开头是注释，空行跳过。"""


def parse_manifest(text):
    """返回有序键值。重复键以最后一次为准，但保留首次出现的位置顺序。"""
    order = []
    values = {}
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError("line {}".format(line_no))
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("line {}".format(line_no))
        if key not in values:
            order.append(key)
        values[key] = value.strip()
    return [(key, values[key]) for key in order]


def require(pairs, key):
    for name, value in pairs:
        if name == key:
            return value
    raise KeyError(key)


def section_groups(text):
    """以 [name] 分段。段名之前的行归入空段。"""
    groups = {}
    order = []
    current = ""
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]") and len(line) > 2:
            current = line[1:-1].strip()
            if current not in groups:
                groups[current] = []
                order.append(current)
            continue
        groups.setdefault(current, [])
        if current not in order:
            order.append(current)
        groups[current].append(raw)
    return [(name, parse_manifest("\n".join(groups[name]))) for name in order]
