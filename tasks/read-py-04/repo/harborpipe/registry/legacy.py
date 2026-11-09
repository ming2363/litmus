"""另一套登记表。"""

from typing import List


class LegacyPlugin:
    registry: List[type] = []
    family = ""
    priority = 0
    plugin_id = ""

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        LegacyPlugin.registry.append(cls)


class LegacyBook:
    def select(self, family: str) -> type:
        rows = [cls for cls in LegacyPlugin.registry if cls.family == family]
        rows.sort(key=lambda item: (-int(item.priority), item.plugin_id))
        if not rows:
            raise LookupError(family)
        return rows[0]
