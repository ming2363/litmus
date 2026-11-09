"""包装体。"""

import functools
from typing import Any, Callable


class Stamp:
    def __init__(self, fn: Callable[..., Any]) -> None:
        self.fn = fn

    def __call__(self, ctx: Any) -> Any:
        return self.fn(ctx)


class Sample:
    def __init__(self, fn: Callable[..., Any]) -> None:
        self.fn = fn

    def __call__(self, ctx: Any) -> Any:
        return self.fn(ctx)


class Freeze:
    def __init__(self, fn: Callable[..., Any]) -> None:
        self.fn = fn

    def __call__(self, ctx: Any) -> Any:
        return self.fn(ctx)


class Loud:
    def __init__(self, fn: Callable[..., Any]) -> None:
        self.fn = fn

    def __call__(self, ctx: Any) -> Any:
        return self.fn(ctx)


def seal(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def sealed(ctx: Any) -> Any:
        return fn(ctx)

    return sealed
