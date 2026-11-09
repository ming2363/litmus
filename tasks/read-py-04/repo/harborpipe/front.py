"""另一扇门。按旁路文件挑选处理类。"""

import json
from pathlib import Path
from typing import Any

from harborpipe.plugins.yard.yard_audit import YardAudit


class FrontGate:
    def __init__(self, overlay_path: Path) -> None:
        self.overlay_path = overlay_path
        self.ctx = {"shift": "night"}

    def invoke(self, operation: str) -> Any:
        table = json.loads(self.overlay_path.read_text(encoding="utf-8"))
        family = table[operation]
        if family != "yard":
            raise KeyError(family)
        plugin = YardAudit()
        verb = operation.rsplit(".", 1)[-1]
        method = getattr(plugin, "do_" + verb)
        return method(self.ctx)
