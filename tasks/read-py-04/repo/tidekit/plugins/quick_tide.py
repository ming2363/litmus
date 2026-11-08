"""插件 p-tide-quick。"""

from tidekit.runtime.registry import plugin, stage


@plugin(family="tide", plugin_id="p-tide-quick", priority=15, needs=("clock", "manual"))
@stage("apply")
class TideQuickPlugin(object):
    """家族 tide 的一个实现。"""

    def apply_fold(self, ctx):
        """返回业务结果，不返回调用链。"""
        return {"label": "quick", "rows": len(ctx.rows)}
