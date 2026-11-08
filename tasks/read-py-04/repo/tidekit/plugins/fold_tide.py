"""插件 p-tide-fold。"""

from tidekit.wrap.audit import audit_call
from tidekit.wrap.guard import unit_guard
from tidekit.runtime.registry import plugin, stage


@plugin(family="tide", plugin_id="p-tide-fold", priority=20, needs=("clock",))
@stage("apply")
class TideFoldPlugin(object):
    """家族 tide 的一个实现。"""

    @audit_call
    @unit_guard
    def apply_fold(self, ctx):
        """返回业务结果，不返回调用链。"""
        return {"label": "fold", "rows": len(ctx.rows)}
