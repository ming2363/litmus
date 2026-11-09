"""包装登记。元组是 (动词, 优先级, 种类, 序号)。"""

from typing import List, Tuple

Binding = Tuple[str, int, str, int]
WRAP_REGISTRY: List[Binding] = []


def register(verb: str, priority: int, kind: str) -> None:
    WRAP_REGISTRY.append((verb, priority, kind, len(WRAP_REGISTRY)))


def load_bindings() -> None:
    if WRAP_REGISTRY:
        return
    register("inspect", 10, "stamp")
    register("inspect", 20, "sample")
    register("inspect", 30, "freeze")
    register("inspect", 40, "seal")
    register("audit", 100, "loud")
    register("audit", 5, "stamp")


load_bindings()
