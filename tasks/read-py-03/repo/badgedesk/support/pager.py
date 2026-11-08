"""内存分页。页码从 1 开始，最后一页允许不足一页。"""


def page_slice(rows, page, size):
    """返回该页的子列表。越界页返回空列表，不抛下标异常。"""
    if page < 1 or size < 1:
        raise ValueError("page")
    start = (page - 1) * size
    if start >= len(rows):
        return []
    end = start + size
    if end > len(rows):
        end = len(rows)
    return list(rows[start:end])


def page_count(total, size):
    if size < 1 or total < 0:
        raise ValueError("size")
    if total == 0:
        return 0
    return (total + size - 1) // size


def page_meta(total, page, size):
    return {
        "page": page,
        "size": size,
        "pages": page_count(total, size),
        "total": total,
    }
