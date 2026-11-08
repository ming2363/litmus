#!/usr/bin/env python3
"""将 summary.json 渲染为 TSV 报表。"""

import json
import os
import sys
from pathlib import Path


def main() -> int:
    summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dst = Path(sys.argv[2])
    lines = ["region\tcount\ttotal_usd"]
    for region, stats in sorted(summary["by_region"].items()):
        lines.append("{}\t{}\t{:.2f}".format(region, stats["count"], stats["total_usd"]))
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tsv.tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    os.replace(str(tmp), str(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
