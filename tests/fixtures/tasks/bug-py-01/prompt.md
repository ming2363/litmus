# bug-py-01: 修复计算器整数除法函数

修改 `src/calc.py` 中的 `safe_div(a, b)`：当 `b == 0` 时抛出 `ValueError("division by zero")`，否则返回 `a / b`。
