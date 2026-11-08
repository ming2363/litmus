"""路由匹配。字面路径优先于模板。"""


def handler_key(method, path, routes):
    """按登记顺序返回处理器键；没有匹配时返回 None。"""
    if not isinstance(method, str) or not isinstance(path, str):
        raise TypeError("request")
    folded = method.upper()
    same = []
    for idx, item in enumerate(routes):
        route_method, pattern, key = item
        if route_method.upper() == folded:
            same.append((idx, pattern, key))
    for _idx, pattern, key in same:
        if "{" not in pattern and pattern == path:
            return key
    best_key = None
    best_static = -1
    best_idx = 10 ** 9
    for idx, pattern, key in same:
        if "{" not in pattern:
            continue
        static = _template_static(pattern, path)
        if static is None:
            continue
        if static > best_static or (static == best_static and idx < best_idx):
            best_static = static
            best_idx = idx
            best_key = key
    return best_key


def _template_static(pattern, path):
    """匹配成功时返回静态段数量，否则 None。"""
    left = pattern.split("/")
    right = path.split("/")
    if len(left) != len(right):
        return None
    static = 0
    for part, actual in zip(left, right):
        if part.startswith("{") and part.endswith("}") and len(part) > 2:
            if actual == "":
                return None
            continue
        if part != actual:
            return None
        if part != "":
            static += 1
    return static
