"""外层审计包装。"""


def audit_call(fn):
    """先记一笔再调用原方法。"""

    def wrapped(self, ctx):
        ctx.notes.append("audit")
        return fn(self, ctx)

    return wrapped
