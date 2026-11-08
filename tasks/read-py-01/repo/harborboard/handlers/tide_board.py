"""列出还能进港的潮窗"""

from harborboard.http.models import Response


class TideWindowHandler(object):
    """列出还能进港的潮窗"""

    def render(self, request):
        return Response(200, {"kind": "tide", "path": request.path})
