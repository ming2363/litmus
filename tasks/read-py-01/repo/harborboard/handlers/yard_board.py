"""按堆场画出占用格子"""

from harborboard.http.models import Response


class YardMapHandler(object):
    """按堆场画出占用格子"""

    def render(self, request):
        return Response(200, {"kind": "yard", "path": request.path})
