"""封账处理器。"""


class NightSealHandler(object):
    """封账。"""

    def apply(self, payload):
        """正式入账。"""
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        total = 0
        for row in rows:
            total += int(row.get("fen", 0))
        return {"status": "sealed", "count": len(rows), "fen": total}

    def preview(self, payload):
        """只计数，不作为正式入账。"""
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        return {"status": "preview", "count": len(rows)}

