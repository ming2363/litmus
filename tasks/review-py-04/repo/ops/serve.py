"""对外服务。费率刷新和整表导出走同一个线程池。"""

from concurrent.futures import Future, ThreadPoolExecutor
from decimal import Decimal
from typing import Dict, Tuple

from billing.rate_view import RateView
from tariff.store import RateStore

Rate = Tuple[Decimal, Decimal]


class Service:
    def __init__(self, store: RateStore) -> None:
        self.store = store
        self.view = RateView()
        self.pool = ThreadPoolExecutor(max_workers=4)

    def refresh(self, rows: Dict[str, Rate]) -> Future:
        return self.pool.submit(self.store.reload, rows)

    def export_rates(self) -> Future:
        return self.pool.submit(self.view.snapshot, self.store)

    def close(self) -> None:
        self.pool.shutdown(wait=True)
