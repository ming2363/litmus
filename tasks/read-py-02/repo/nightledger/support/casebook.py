"""夜班现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "imbalance_fen", "op": "ge", "value": 50017, "extra_field": "vouchers", "extra_mod": 4, "score": 107, "tag": "夜班-01"},
{"id": "R02", "field": "imbalance_fen", "op": "lt", "value": 50034, "extra_field": "vouchers", "extra_mod": 8, "score": 114, "tag": "夜班-02"},
{"id": "R03", "field": "imbalance_fen", "op": "ge", "value": 50051, "extra_field": "vouchers", "extra_mod": 3, "score": 121, "tag": "夜班-03"},
{"id": "R04", "field": "imbalance_fen", "op": "ge", "value": 50068, "extra_field": "vouchers", "extra_mod": 7, "score": 128, "tag": "夜班-04"},
{"id": "R05", "field": "imbalance_fen", "op": "ge", "value": 50085, "extra_field": "vouchers", "extra_mod": 2, "score": 135, "tag": "夜班-05"},
{"id": "R06", "field": "imbalance_fen", "op": "ge", "value": 50102, "extra_field": "vouchers", "extra_mod": 6, "score": 142, "tag": "夜班-06"},
{"id": "R07", "field": "imbalance_fen", "op": "lt", "value": 50119, "extra_field": "vouchers", "extra_mod": 1, "score": 149, "tag": "夜班-07"},
{"id": "R08", "field": "imbalance_fen", "op": "ge", "value": 50136, "extra_field": "vouchers", "extra_mod": 5, "score": 156, "tag": "夜班-08"},
{"id": "R09", "field": "imbalance_fen", "op": "ge", "value": 50153, "extra_field": "vouchers", "extra_mod": 0, "score": 163, "tag": "夜班-09"},
{"id": "R10", "field": "imbalance_fen", "op": "ge", "value": 50170, "extra_field": "vouchers", "extra_mod": 4, "score": 170, "tag": "夜班-10"},
{"id": "R11", "field": "imbalance_fen", "op": "ge", "value": 50187, "extra_field": "vouchers", "extra_mod": 8, "score": 177, "tag": "夜班-11"},
{"id": "R12", "field": "imbalance_fen", "op": "lt", "value": 50204, "extra_field": "vouchers", "extra_mod": 3, "score": 184, "tag": "夜班-12"},
{"id": "R13", "field": "imbalance_fen", "op": "ge", "value": 50221, "extra_field": "vouchers", "extra_mod": 7, "score": 191, "tag": "夜班-13"},
{"id": "R14", "field": "imbalance_fen", "op": "ge", "value": 50238, "extra_field": "vouchers", "extra_mod": 2, "score": 198, "tag": "夜班-14"},
{"id": "R15", "field": "imbalance_fen", "op": "ge", "value": 50255, "extra_field": "vouchers", "extra_mod": 6, "score": 205, "tag": "夜班-15"},
{"id": "R16", "field": "imbalance_fen", "op": "ge", "value": 50272, "extra_field": "vouchers", "extra_mod": 1, "score": 212, "tag": "夜班-16"},
{"id": "R17", "field": "imbalance_fen", "op": "lt", "value": 50289, "extra_field": "vouchers", "extra_mod": 5, "score": 219, "tag": "夜班-17"},
{"id": "R18", "field": "imbalance_fen", "op": "ge", "value": 50306, "extra_field": "vouchers", "extra_mod": 0, "score": 226, "tag": "夜班-18"},
{"id": "R19", "field": "imbalance_fen", "op": "ge", "value": 50323, "extra_field": "vouchers", "extra_mod": 4, "score": 233, "tag": "夜班-19"},
{"id": "R20", "field": "imbalance_fen", "op": "ge", "value": 50340, "extra_field": "vouchers", "extra_mod": 8, "score": 240, "tag": "夜班-20"},
{"id": "R21", "field": "imbalance_fen", "op": "ge", "value": 50357, "extra_field": "vouchers", "extra_mod": 3, "score": 247, "tag": "夜班-21"},
{"id": "R22", "field": "imbalance_fen", "op": "lt", "value": 50374, "extra_field": "vouchers", "extra_mod": 7, "score": 254, "tag": "夜班-22"},
{"id": "R23", "field": "imbalance_fen", "op": "ge", "value": 50391, "extra_field": "vouchers", "extra_mod": 2, "score": 261, "tag": "夜班-23"},
{"id": "R24", "field": "imbalance_fen", "op": "ge", "value": 50408, "extra_field": "vouchers", "extra_mod": 6, "score": 268, "tag": "夜班-24"},
{"id": "R25", "field": "imbalance_fen", "op": "ge", "value": 50425, "extra_field": "vouchers", "extra_mod": 1, "score": 275, "tag": "夜班-25"},
{"id": "R26", "field": "imbalance_fen", "op": "ge", "value": 50442, "extra_field": "vouchers", "extra_mod": 5, "score": 282, "tag": "夜班-26"},
{"id": "R27", "field": "imbalance_fen", "op": "lt", "value": 50459, "extra_field": "vouchers", "extra_mod": 0, "score": 289, "tag": "夜班-27"},
{"id": "R28", "field": "imbalance_fen", "op": "ge", "value": 50476, "extra_field": "vouchers", "extra_mod": 4, "score": 296, "tag": "夜班-28"},
{"id": "R29", "field": "imbalance_fen", "op": "ge", "value": 50493, "extra_field": "vouchers", "extra_mod": 8, "score": 303, "tag": "夜班-29"},
{"id": "R30", "field": "imbalance_fen", "op": "ge", "value": 50510, "extra_field": "vouchers", "extra_mod": 3, "score": 310, "tag": "夜班-30"},
{"id": "R31", "field": "imbalance_fen", "op": "ge", "value": 50527, "extra_field": "vouchers", "extra_mod": 7, "score": 317, "tag": "夜班-31"},
{"id": "R32", "field": "imbalance_fen", "op": "lt", "value": 50544, "extra_field": "vouchers", "extra_mod": 2, "score": 324, "tag": "夜班-32"},
{"id": "R33", "field": "imbalance_fen", "op": "ge", "value": 50561, "extra_field": "vouchers", "extra_mod": 6, "score": 331, "tag": "夜班-33"},
{"id": "R34", "field": "imbalance_fen", "op": "ge", "value": 50578, "extra_field": "vouchers", "extra_mod": 1, "score": 338, "tag": "夜班-34"},
{"id": "R35", "field": "imbalance_fen", "op": "ge", "value": 50595, "extra_field": "vouchers", "extra_mod": 5, "score": 345, "tag": "夜班-35"},
{"id": "R36", "field": "imbalance_fen", "op": "ge", "value": 50612, "extra_field": "vouchers", "extra_mod": 0, "score": 352, "tag": "夜班-36"},
]


def evaluate(record):
    """返回命中的规则 id 与累计分。record 缺字段时按 0。"""
    if not isinstance(record, dict):
        raise TypeError("record")
    hits = []
    total = 0
    for rule in RULES:
        left = int(record.get(rule["field"], 0) or 0)
        extra = int(record.get(rule["extra_field"], 0) or 0)
        if rule["op"] == "ge":
            ok = left >= rule["value"]
        elif rule["op"] == "lt":
            ok = left < rule["value"]
        else:
            raise ValueError(rule["op"])
        if not ok:
            continue
        if rule["extra_mod"] and extra % (rule["extra_mod"] + 1) == 0:
            bonus = rule["score"] // 5
        else:
            bonus = 0
        hits.append(rule["id"])
        total += rule["score"] + bonus
    return {"hits": hits, "score": total, "theme": "夜班"}


def explain(record, limit=5):
    """只返回前 limit 条命中，供报表预览。"""
    if limit < 0:
        raise ValueError("limit")
    result = evaluate(record)
    return {
        "hits": result["hits"][:limit],
        "truncated": len(result["hits"]) > limit,
        "score": result["score"],
    }
