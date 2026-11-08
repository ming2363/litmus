"""操作入口。"""

import tidekit.plugins  # noqa: F401  导入以完成登记
from tidekit.runtime.resolve import Resolver


class Entry(object):
    """按操作名调用插件。"""

    def __init__(self):
        self.resolver = Resolver()

    def invoke(self, operation, ctx):
        """operation 形如 family.action。返回业务字典。"""
        family, action = operation.split(".", 1)
        rec = self.resolver.select(family)
        verb = self.resolver.verb_for(rec, action)
        target = getattr(rec.spawn(), verb)
        return target(ctx)
