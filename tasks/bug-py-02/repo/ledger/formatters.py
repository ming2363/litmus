"""把门店报表渲染成固定列宽的文本。"""

from typing import Dict, List


def format_report(rows: List[Dict]) -> str:
    header = "id  name        region  paid_orders  paid_amount  refunded"
    lines = [header]
    for row in rows:
        lines.append(
            "{:<3} {:<11} {:<7} {:>11} {:>12} {:>8}".format(
                row["store_id"],
                row["store_name"],
                row["region"],
                row["paid_orders"],
                row["paid_amount_cents"],
                row["refunded_orders"],
            )
        )
    return "\n".join(lines)
