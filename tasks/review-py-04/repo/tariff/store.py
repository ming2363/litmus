"""费率表。"""

import threading
from decimal import Decimal
from typing import Dict, Tuple

Rate = Tuple[Decimal, Decimal]


class RateStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.rates: Dict[str, Rate] = {}

    def reload(self, rows: Dict[str, Rate]) -> None:
        with self._lock:
            self.rates.clear()
            self.rates.update(rows)

    def rate_for(self, lane: str) -> Rate:
        with self._lock:
            found = self.rates.get(lane)
            if found is None:
                raise KeyError(lane)
            return found
