"""堆场封账处理器。"""


class YardSealHandler(object):
    """堆场封账。"""

    def apply(self, payload):
        """正式入账。"""
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        total = 0
        for row in rows:
            total += int(row.get("fen", 0))
        return {"status": "yard-sealed", "count": len(rows), "fen": total}

