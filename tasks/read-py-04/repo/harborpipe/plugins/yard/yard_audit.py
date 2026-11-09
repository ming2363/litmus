"""堆场审计。"""

from typing import Any

from harborpipe.registry.book import Plugin


class YardAudit(Plugin):
    family = "yard"
    priority = 100
    plugin_id = "yard.audit"
    caps = ("read",)

    def do_audit(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "shift": ctx.get("shift")}

    def do_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "shift": ctx.get("shift"), "verb": "inspect"}
