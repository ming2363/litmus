"""权限位。bit0 读，bit1 写，bit2 审核，bit3 导出。"""

READ = 1
WRITE = 2
AUDIT = 4
EXPORT = 8


def pack(names):
    """名字集合转成整数。未知名字抛错。"""
    table = {"read": READ, "write": WRITE, "audit": AUDIT, "export": EXPORT}
    value = 0
    for name in names:
        if name not in table:
            raise KeyError(name)
        value |= table[name]
    return value


def unpack(value):
    """整数转成排序后的名字列表。"""
    if value < 0 or value > 15:
        raise ValueError(value)
    names = []
    if value & READ:
        names.append("read")
    if value & WRITE:
        names.append("write")
    if value & AUDIT:
        names.append("audit")
    if value & EXPORT:
        names.append("export")
    return names


def allows(granted, required):
    """required 的每个位都必须已授予。"""
    return (granted & required) == required


def grant(granted, extra):
    return granted | extra


def revoke(granted, extra):
    return granted & ~extra
