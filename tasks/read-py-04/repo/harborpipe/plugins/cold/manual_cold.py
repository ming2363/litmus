"""需要人工封签的冷箱处理。"""

from typing import Any

from harborpipe.registry.book import Plugin


class ManualCold(Plugin):
    family = "cold"
    priority = 80
    plugin_id = "cold.manual"
    manual = True
    caps = ("read",)

    def do_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "manual": True}

    def do_audit(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "verb": "audit"}
