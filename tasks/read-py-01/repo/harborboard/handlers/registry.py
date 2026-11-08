"""按生效键调用业务方法。这里不保存函数名字符串。"""

from harborboard.handlers.berth_board import (
    ActivateBerthHandler,
    ActiveBerthHandler,
    BerthListHandler,
    CloseBerthHandler,
)
from harborboard.handlers.berth_misc import (
    ActiveExportHandler,
    ActivityFeedHandler,
    BerthNoteHandler,
    BerthViewHandler,
)
from harborboard.handlers.legacy import LegacyActiveHandler
from harborboard.handlers.tide_board import TideWindowHandler
from harborboard.handlers.yard_board import YardMapHandler


def invoke(key, request):
    """未知键抛出 KeyError。返回业务响应。"""
    if key == "berth.list":
        return BerthListHandler().render(request)
    if key == "berth.activity":
        return ActivityFeedHandler().render(request)
    if key == "berth.view":
        return BerthViewHandler().render(request)
    if key == "berth.activate":
        return ActivateBerthHandler().submit(request)
    if key == "yard.map":
        return YardMapHandler().render(request)
    if key == "tide.windows":
        return TideWindowHandler().render(request)
    if key == "berth.note":
        return BerthNoteHandler().update(request)
    if key == "berth.legacy":
        return LegacyActiveHandler().dump(request)
    if key == "berth.export":
        return ActiveExportHandler().render(request)
    if key == "berth.close":
        return CloseBerthHandler().submit(request)
    if key == "berth.active":
        return ActiveBerthHandler().render(request)
    raise KeyError(key)
