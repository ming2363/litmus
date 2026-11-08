"""开账处理器。"""


class NightOpenHandler(object):
    """开账。"""

    def apply(self, payload):
        """正式入账。"""
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        total = 0
        for row in rows:
            total += int(row.get("fen", 0))
        return {"status": "opened", "count": len(rows), "fen": total}

