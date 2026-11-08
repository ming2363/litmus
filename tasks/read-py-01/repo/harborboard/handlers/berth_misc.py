"""泊位周边视图。"""

from harborboard.handlers.catalog_data import BERTHS, by_state
from harborboard.http.models import Response


class ActivityFeedHandler(object):
    """近期动态，不是在泊清单。"""

    def render(self, request):
        rows = [row for row in BERTHS if row["state"] in ("idle", "repair")]
        return Response(200, {"feed": rows})


class BerthViewHandler(object):
    """按路径变量查看某一类泊位。"""

    def render(self, request):
        view = request.path.rstrip("/").split("/")[-1]
        return Response(200, {"view": view, "rows": by_state(view)})


class BerthNoteHandler(object):
    """改备注。"""

    def update(self, request):
        note = request.query.get("note", "")
        return Response(200, {"note": note[:40]})


class ActiveExportHandler(object):
    """导出活跃泊位的编码列表。"""

    def render(self, request):
        codes = [row["code"] for row in by_state("active")]
        return Response(200, {"format": "codes", "codes": codes})
