#!/usr/bin/env python3
"""按汇率与区域映射表丰富分片记录并折算为 USD。"""

import csv
import json
import os
import sys
from pathlib import Path


def main() -> int:
    src_csv = Path(sys.argv[1])
    rates_path = Path(sys.argv[2])
    regions_path = Path(sys.argv[3])
    dst_json = Path(sys.argv[4])

    rates = json.loads(rates_path.read_text(encoding="utf-8"))
    regions = json.loads(regions_path.read_text(encoding="utf-8"))

    records = []
    with src_csv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            cur = row["currency"]
            amt_usd = round(float(row["amount"]) * float(rates[cur]), 2)
            records.append({
                "tx_id": row["tx_id"],
                "region": regions[row["region_code"]],
                "usd_amount": amt_usd,
            })

    dst_json.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(str(tmp), str(dst_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
