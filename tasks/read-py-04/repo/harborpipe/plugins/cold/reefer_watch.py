"""冷箱值守。"""

from typing import Any

from harborpipe.registry.book import Plugin


class ReeferWatch(Plugin):
    family = "cold"
    priority = 40
    plugin_id = "cold.reefer"
    caps = ("read", "meter")

    def do_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "shift": ctx.get("shift")}

    def do_audit(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "verb": "audit"}
