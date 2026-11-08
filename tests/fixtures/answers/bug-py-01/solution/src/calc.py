def add(a: int, b: int) -> int:
    return a + b


def safe_div(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b
