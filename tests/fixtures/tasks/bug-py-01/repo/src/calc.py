def add(a: int, b: int) -> int:
    return a + b


def safe_div(a: float, b: float) -> float:
    # 缺陷：未检查除数为 0
    return a / b
