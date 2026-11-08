"""轻量可重试 HTTP 客户端。"""

from typing import Callable, Dict, Optional

from src.models import HttpRequest, HttpResponse, HttpStatusError, TransportError

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3

TransportFn = Callable[[HttpRequest], HttpResponse]


def _default_transport(req: HttpRequest) -> HttpResponse:
    raise TransportError("未注入 transport 传输实现: {}".format(req.url))


class HttpClient:
    """支持固定重试次数的简易 HTTP 客户端。"""

    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        transport: Optional[TransportFn] = None,
    ) -> None:
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url 不能为空")
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.max_retries = max_retries
        self._transport = transport or _default_transport

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        body: str = "",
        timeout: Optional[float] = None,
    ) -> HttpResponse:
        if not path.startswith("/"):
            path = "/" + path
        effective_timeout = self.timeout if timeout is None else float(timeout)
        req = HttpRequest(
            method=method.upper(),
            url=self.base_url + path,
            headers=dict(headers or {}),
            body=body,
            timeout=effective_timeout,
        )

        last_err: Optional[Exception] = None
        for _ in range(self.max_retries + 1):
            try:
                resp = self._transport(req)
            except TransportError as exc:
                last_err = exc
                continue
            if resp.status_code >= 500:
                last_err = HttpStatusError(resp.status_code, resp.body)
                continue
            return resp

        if last_err is not None:
            raise last_err
        raise TransportError("请求失败")

    def get(self, path: str, *, timeout: Optional[float] = None) -> HttpResponse:
        return self.request("GET", path, timeout=timeout)

    def post(self, path: str, body: str = "", *, timeout: Optional[float] = None) -> HttpResponse:
        return self.request("POST", path, body=body, timeout=timeout)
