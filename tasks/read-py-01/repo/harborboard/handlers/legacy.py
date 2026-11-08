"""旧版活跃泊位导出"""

from harborboard.http.models import Response


class LegacyActiveHandler(object):
    """旧版活跃泊位导出"""

    def dump(self, request):
        return Response(200, {"kind": "legacy", "path": request.path})
