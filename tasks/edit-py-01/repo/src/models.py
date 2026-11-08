"""请求/响应数据模型与传输异常定义。"""

from dataclasses import dataclass, field
from typing import Dict


class TransportError(Exception):
    """底层传输故障（可触发重试）。"""


class HttpStatusError(Exception):
    """服务端返回非预期 HTTP 状态码。"""

    def __init__(self, status_code: int, body: str) -> None:
        super().__init__("HTTP {}: {}".format(status_code, body))
        self.status_code = status_code
        self.body = body


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    timeout: float = 5.0


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    body: str
    headers: Dict[str, str] = field(default_factory=dict)
