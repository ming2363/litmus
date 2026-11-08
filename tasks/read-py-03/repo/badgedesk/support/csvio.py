"""足够小的 CSV 读写，支持引号与逗号。"""


def parse_csv(text):
    """返回行列表。空行跳过。"""
    rows = []
    row = []
    cell = []
    quoted = False
    i = 0
    while i < len(text):
        ch = text[i]
        if quoted:
            if ch == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    cell.append('"')
                    i += 2
                    continue
                quoted = False
                i += 1
                continue
            cell.append(ch)
            i += 1
            continue
        if ch == '"':
            quoted = True
            i += 1
            continue
        if ch == ",":
            row.append("".join(cell))
            cell = []
            i += 1
            continue
        if ch == "\n":
            row.append("".join(cell))
            cell = []
            if any(part != "" for part in row):
                rows.append(row)
            row = []
            i += 1
            continue
        if ch == "\r":
            i += 1
            continue
        cell.append(ch)
        i += 1
    if quoted:
        raise ValueError("unclosed-quote")
    if cell or row:
        row.append("".join(cell))
        if any(part != "" for part in row):
            rows.append(row)
    return rows


def emit_csv(rows):
    """写出 CSV 文本，单元格含逗号或引号时加引号。"""
    lines = []
    for row in rows:
        cells = []
        for value in row:
            text = "" if value is None else str(value)
            if any(ch in text for ch in ",\"\n"):
                text = '"' + text.replace('"', '""') + '"'
            cells.append(text)
        lines.append(",".join(cells))
    return "\n".join(lines) + ("\n" if lines else "")


def rows_as_dicts(rows):
    """首行是表头。"""
    if not rows:
        return []
    header = rows[0]
    out = []
    for row in rows[1:]:
        if len(row) != len(header):
            raise ValueError("width")
        out.append(dict(zip(header, row)))
    return out
