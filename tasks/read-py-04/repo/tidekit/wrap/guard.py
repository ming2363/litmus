"""内层单位检查。"""


def unit_guard(fn):
    """只接受分钟。"""

    def wrapped(self, ctx):
        if ctx.unit != "minute":
            raise ValueError("unit")
        return fn(self, ctx)

    return wrapped
