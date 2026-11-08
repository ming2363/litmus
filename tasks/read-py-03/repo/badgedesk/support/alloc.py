"""把有限库存按优先级分给申请。"""


def fulfill(stock, requests):
    """requests: (request_id, sku, qty, priority)。priority 小的先满足。

    返回 (allocations, leftover_stock)。同一优先级按 request_id 排序。
    """
    left = dict(stock)
    ordered = sorted(requests, key=lambda item: (item[3], item[0]))
    granted = []
    for request_id, sku, qty, _priority in ordered:
        if qty < 0:
            raise ValueError(request_id)
        have = left.get(sku, 0)
        take = qty if have >= qty else have
        if take:
            left[sku] = have - take
            granted.append((request_id, sku, take))
        else:
            granted.append((request_id, sku, 0))
    return granted, left


def shortages(requests, granted):
    """按申请汇总缺口。"""
    got = {}
    for request_id, _sku, take in granted:
        got[request_id] = got.get(request_id, 0) + take
    lack = []
    for request_id, sku, qty, _priority in requests:
        missing = qty - got.get(request_id, 0)
        if missing > 0:
            lack.append((request_id, sku, missing))
    return lack
