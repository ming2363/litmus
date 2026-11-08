"""插件 p-tide-legacy。"""

from tidekit.runtime.registry import plugin, stage


@plugin(family="tide", plugin_id="p-tide-legacy", priority=5, needs=("clock", "legacy_bus"))
@stage("apply")
class TideLegacyPlugin(object):
    """家族 tide 的一个实现。"""

    def apply_fold(self, ctx):
        """返回业务结果，不返回调用链。"""
        return {"label": "legacy", "rows": len(ctx.rows)}
