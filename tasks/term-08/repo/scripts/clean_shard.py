#!/usr/bin/env python3
"""清洗单个分片 CSV：过滤 valid == true 的有效记录。"""

import csv
import os
import sys
from pathlib import Path


def main() -> int:
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    kept = [r for r in rows if r.get("valid", "").strip().lower() == "true"]
    tmp = dst.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tx_id", "region_code", "currency", "amount"], lineterminator="\n")
        writer.writeheader()
        for r in kept:
            writer.writerow({
                "tx_id": r["tx_id"].strip(),
                "region_code": r["region_code"].strip(),
                "currency": r["currency"].strip(),
                "amount": r["amount"].strip(),
            })
    os.replace(str(tmp), str(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
