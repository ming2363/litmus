"""冷箱审计。"""

from typing import Any

from harborpipe.registry.book import Plugin


class AuditPrimary(Plugin):
    family = "cold"
    priority = 40
    plugin_id = "cold.audit"
    caps = ("read",)

    def do_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "shift": ctx.get("shift")}

    def do_audit(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "verb": "audit"}

    def perform_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "fallback": True}
