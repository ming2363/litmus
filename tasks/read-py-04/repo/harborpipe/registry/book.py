"""插件类的登记与挑选。"""

from typing import List, Tuple

ACTIVE_CAPS = frozenset({"read", "meter"})


class Plugin:
    """子类在定义时进入 registry。"""

    registry: List[type] = []
    abstract = False
    family = ""
    priority = 0
    plugin_id = ""
    manual = False
    caps: Tuple[str, ...] = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("abstract"):
            return
        Plugin.registry.append(cls)


class Book:
    def __init__(self, manual_open: bool) -> None:
        self.manual_open = manual_open

    def select(self, family: str) -> type:
        eligible = []
        for cls in Plugin.registry:
            if cls.family != family:
                continue
            if type(cls.priority) is not int:
                continue
            if any(cap not in ACTIVE_CAPS for cap in cls.caps):
                continue
            if cls.manual and not self.manual_open:
                continue
            eligible.append(cls)
        if not eligible:
            raise LookupError(family)
        eligible.sort(key=lambda item: (-item.priority, item.plugin_id))
        return eligible[0]
