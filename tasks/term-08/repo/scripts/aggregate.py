#!/usr/bin/env python3
"""汇总全部已丰富分片为 summary.json。"""

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args()

    by_region = defaultdict(lambda: {"count": 0, "total_usd": 0.0})
    total_tx = 0
    total_usd = 0.0

    for path_str in sorted(args.inputs):
        items = json.loads(Path(path_str).read_text(encoding="utf-8"))
        for item in items:
            reg = item["region"]
            amt = float(item["usd_amount"])
            by_region[reg]["count"] += 1
            by_region[reg]["total_usd"] = round(by_region[reg]["total_usd"] + amt, 2)
            total_tx += 1
            total_usd = round(total_usd + amt, 2)

    out = {
        "total_transactions": total_tx,
        "total_usd": total_usd,
        "by_region": {k: by_region[k] for k in sorted(by_region.keys())},
    }
    dst = Path(args.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(str(tmp), str(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
