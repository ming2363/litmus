"""泊位主处理器。"""

from harborboard.handlers.catalog_data import BERTHS, by_state
from harborboard.http.models import Response


def _page(rows, request):
    """query 里的 limit 只影响本响应，缺省 20。"""
    raw = request.query.get("limit", "20")
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        limit = 20
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    return rows[:limit]


class BerthListHandler(object):
    """全部泊位。"""

    def render(self, request):
        return Response(200, {"rows": _page(list(BERTHS), request)})


class ActiveBerthHandler(object):
    """当前可作业泊位。"""

    def render(self, request):
        rows = by_state("active")
        return Response(200, {"view": "active", "rows": _page(rows, request)})


class ActivateBerthHandler(object):
    """把泊位标记为可作业。这里只回显，不写盘。"""

    def submit(self, request):
        code = request.query.get("code", "")
        return Response(202, {"code": code, "state": "active"})


class CloseBerthHandler(object):
    """关闭泊位。"""

    def submit(self, request):
        code = request.query.get("code", "")
        return Response(202, {"code": code, "state": "closed"})
