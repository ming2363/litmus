"""借贷差额。分发链不调用。"""


def imbalance(lines):
    """lines 是 (debit_fen, credit_fen)。"""
    debit = 0
    credit = 0
    for left, right in lines:
        if left < 0 or right < 0:
            raise ValueError("line")
        debit += left
        credit += right
    return debit - credit
