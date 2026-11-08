"""插件 p-tide-preview。"""

from tidekit.runtime.registry import plugin, stage


@plugin(family="tide", plugin_id="p-tide-preview", priority=10, needs=("preview_mode",))
@stage("show")
class TidePeekPlugin(object):
    """家族 tide 的一个实现。"""

    def show_peek(self, ctx):
        """返回业务结果，不返回调用链。"""
        return {"label": "peek", "rows": len(ctx.rows)}
