"""冷箱优先候选。"""

from typing import Any

from harborpipe.registry.book import Plugin


class ColdPrimary(Plugin):
    family = "cold"
    priority = 90.0
    plugin_id = "cold.primary"
    caps = ("read", "meter")

    def do_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "shift": ctx.get("shift")}

    def do_audit(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "verb": "audit"}
