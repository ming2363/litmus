"""CSV 账目文件读取与校验。"""

import csv
from pathlib import Path
from typing import List

from src.models import LedgerEntry, VALID_KINDS, parse_iso_date

EXPECTED_HEADER = ["id", "date", "category", "kind", "amount_cents", "note"]


def load_entries(path: Path) -> List[LedgerEntry]:
    """从 CSV 文件加载全部账目记录。"""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError("账目文件不存在: {}".format(file_path))

    entries: List[LedgerEntry] = []
    with file_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != EXPECTED_HEADER:
            raise ValueError("CSV 表头无效: {}".format(reader.fieldnames))
        for line_no, row in enumerate(reader, start=2):
            entry_id = (row.get("id") or "").strip()
            if not entry_id:
                raise ValueError("第 {} 行缺少 id".format(line_no))
            tx_date = parse_iso_date((row.get("date") or "").strip())
            category = (row.get("category") or "").strip()
            if not category:
                raise ValueError("第 {} 行缺少 category".format(line_no))
            kind = (row.get("kind") or "").strip()
            if kind not in VALID_KINDS:
                raise ValueError("第 {} 行类型非法: {}".format(line_no, kind))
            amount_raw = (row.get("amount_cents") or "").strip()
            amount_cents = int(amount_raw)
            if amount_cents < 0:
                raise ValueError("第 {} 行金额不能为负: {}".format(line_no, amount_cents))
            note = (row.get("note") or "").strip()
            entries.append(
                LedgerEntry(
                    entry_id=entry_id,
                    tx_date=tx_date,
                    category=category,
                    kind=kind,
                    amount_cents=amount_cents,
                    note=note,
                )
            )
    return entries
