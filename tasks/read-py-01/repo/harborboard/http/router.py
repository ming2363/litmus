"""把请求交给业务处理函数。"""

from harborboard.handlers.registry import invoke
from harborboard.http.match import handler_key
from harborboard.http.models import Response
from harborboard.http.table import ROUTES


class Router(object):
    """看板入口。"""

    def resolve(self, request):
        """返回响应。业务函数由生效路由表和 invoke 决定。"""
        key = handler_key(request.method, request.path, ROUTES)
        if key is None:
            return Response(404, {"error": "not_found"})
        response = invoke(key, request)
        response.headers["X-Harbor-Trace"] = "router"
        return response
