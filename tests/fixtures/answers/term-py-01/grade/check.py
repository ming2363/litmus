from pathlib import Path
import sys

out = Path("output.txt")
if not out.is_file():
    print("缺少 output.txt", file=sys.stderr)
    sys.exit(1)

lines = [line.strip() for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
if lines != ["apple", "banana", "cherry"]:
    print("输出内容不正确: {}".format(lines), file=sys.stderr)
    sys.exit(1)
sys.exit(0)
