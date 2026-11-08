"""账目过滤与汇总计算逻辑。"""

from typing import Dict, List, Optional, Sequence

from src.models import LedgerEntry, format_cents


def filter_entries(
    entries: Sequence[LedgerEntry],
    *,
    category: Optional[str] = None,
) -> List[LedgerEntry]:
    """按条件过滤账目并保持原有顺序。"""
    result: List[LedgerEntry] = []
    for entry in entries:
        if category is not None and entry.category != category:
            continue
        result.append(entry)
    return result


def summarize_entries(entries: Sequence[LedgerEntry]) -> Dict[str, object]:
    """统计总收入、总支出、净结余及各分类汇总（单位：分）。"""
    total_income = 0
    total_expense = 0
    by_category: Dict[str, Dict[str, int]] = {}

    for entry in entries:
        bucket = by_category.setdefault(
            entry.category, {"income_cents": 0, "expense_cents": 0, "net_cents": 0}
        )
        if entry.kind == "income":
            total_income += entry.amount_cents
            bucket["income_cents"] += entry.amount_cents
            bucket["net_cents"] += entry.amount_cents
        else:
            total_expense += entry.amount_cents
            bucket["expense_cents"] += entry.amount_cents
            bucket["net_cents"] -= entry.amount_cents

    return {
        "count": len(entries),
        "income_cents": total_income,
        "expense_cents": total_expense,
        "net_cents": total_income - total_expense,
        "by_category": by_category,
    }


def format_list_output(entries: Sequence[LedgerEntry]) -> str:
    """渲染明细输出文本。"""
    if not entries:
        return "暂无匹配记录。\n"
    lines: List[str] = []
    for entry in entries:
        sign = "+" if entry.kind == "income" else "-"
        lines.append(
            "{} | {} | {} | {}{} | {}".format(
                entry.entry_id,
                entry.tx_date.isoformat(),
                entry.category,
                sign,
                format_cents(entry.amount_cents),
                entry.note,
            )
        )
    return "\n".join(lines) + "\n"


def format_summary_output(summary: Dict[str, object]) -> str:
    """渲染分类汇总输出文本。"""
    lines = [
        "记录数: {}".format(summary["count"]),
        "总收入: {}".format(format_cents(int(summary["income_cents"]))),
        "总支出: {}".format(format_cents(int(summary["expense_cents"]))),
        "净结余: {}".format(format_cents(int(summary["net_cents"]))),
    ]
    by_cat: Dict[str, Dict[str, int]] = summary["by_category"]  # type: ignore[assignment]
    if by_cat:
        lines.append("分类明细:")
        for cat in sorted(by_cat.keys()):
            b = by_cat[cat]
            lines.append(
                "  {}: 收入 {} / 支出 {} / 净额 {}".format(
                    cat,
                    format_cents(b["income_cents"]),
                    format_cents(b["expense_cents"]),
                    format_cents(b["net_cents"]),
                )
            )
    return "\n".join(lines) + "\n"
