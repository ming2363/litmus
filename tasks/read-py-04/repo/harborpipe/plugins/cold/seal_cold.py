"""带封签能力的冷箱处理。"""

from typing import Any

from harborpipe.registry.book import Plugin


class SealCold(Plugin):
    family = "cold"
    priority = 70
    plugin_id = "cold.seal"
    caps = ("read", "seal")

    def do_inspect(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id}

    def do_audit(self, ctx: Any) -> Any:
        return {"plugin": self.plugin_id, "verb": "audit"}
