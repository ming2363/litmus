"""插件 p-tide-archive。"""

from tidekit.runtime.registry import plugin, stage


@plugin(family="tide", plugin_id="p-tide-archive", priority=30, needs=("clock", "archive_bin"))
@stage("apply")
class TideBoxPlugin(object):
    """家族 tide 的一个实现。"""

    def apply_box(self, ctx):
        """返回业务结果，不返回调用链。"""
        return {"label": "box", "rows": len(ctx.rows)}
