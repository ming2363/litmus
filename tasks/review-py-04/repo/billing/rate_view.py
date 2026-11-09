"""费率整表视图。"""

from decimal import Decimal
from typing import List, Tuple

from tariff.store import RateStore

RateRow = Tuple[str, Tuple[Decimal, Decimal]]


class RateView:
    def snapshot(self, store: RateStore) -> List[RateRow]:
        rows: List[RateRow] = []
        for key in store.rates:
            rows.append((key, store.rates[key]))
        rows.sort(key=lambda item: item[0])
        return rows
