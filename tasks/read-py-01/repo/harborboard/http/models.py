"""请求与响应。服务不监听端口。"""


class Request(object):
    """一次看板查询。"""

    def __init__(self, method, path, query=None):
        self.method = method
        self.path = path
        self.query = dict(query or {})


class Response(object):
    """状态码与 JSON 载荷。"""

    def __init__(self, status, payload):
        self.status = status
        self.payload = payload
        self.headers = {}
