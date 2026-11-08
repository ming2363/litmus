"""现场现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "amount", "op": "ge", "value": 27, "extra_field": "count", "extra_mod": 4, "score": 107, "tag": "现场-01"},
{"id": "R02", "field": "amount", "op": "lt", "value": 44, "extra_field": "count", "extra_mod": 8, "score": 114, "tag": "现场-02"},
{"id": "R03", "field": "amount", "op": "ge", "value": 61, "extra_field": "count", "extra_mod": 3, "score": 121, "tag": "现场-03"},
{"id": "R04", "field": "amount", "op": "ge", "value": 78, "extra_field": "count", "extra_mod": 7, "score": 128, "tag": "现场-04"},
{"id": "R05", "field": "amount", "op": "ge", "value": 95, "extra_field": "count", "extra_mod": 2, "score": 135, "tag": "现场-05"},
{"id": "R06", "field": "amount", "op": "ge", "value": 112, "extra_field": "count", "extra_mod": 6, "score": 142, "tag": "现场-06"},
{"id": "R07", "field": "amount", "op": "lt", "value": 129, "extra_field": "count", "extra_mod": 1, "score": 149, "tag": "现场-07"},
{"id": "R08", "field": "amount", "op": "ge", "value": 146, "extra_field": "count", "extra_mod": 5, "score": 156, "tag": "现场-08"},
{"id": "R09", "field": "amount", "op": "ge", "value": 163, "extra_field": "count", "extra_mod": 0, "score": 163, "tag": "现场-09"},
{"id": "R10", "field": "amount", "op": "ge", "value": 180, "extra_field": "count", "extra_mod": 4, "score": 170, "tag": "现场-10"},
{"id": "R11", "field": "amount", "op": "ge", "value": 197, "extra_field": "count", "extra_mod": 8, "score": 177, "tag": "现场-11"},
{"id": "R12", "field": "amount", "op": "lt", "value": 214, "extra_field": "count", "extra_mod": 3, "score": 184, "tag": "现场-12"},
{"id": "R13", "field": "amount", "op": "ge", "value": 231, "extra_field": "count", "extra_mod": 7, "score": 191, "tag": "现场-13"},
{"id": "R14", "field": "amount", "op": "ge", "value": 248, "extra_field": "count", "extra_mod": 2, "score": 198, "tag": "现场-14"},
{"id": "R15", "field": "amount", "op": "ge", "value": 265, "extra_field": "count", "extra_mod": 6, "score": 205, "tag": "现场-15"},
{"id": "R16", "field": "amount", "op": "ge", "value": 282, "extra_field": "count", "extra_mod": 1, "score": 212, "tag": "现场-16"},
{"id": "R17", "field": "amount", "op": "lt", "value": 299, "extra_field": "count", "extra_mod": 5, "score": 219, "tag": "现场-17"},
{"id": "R18", "field": "amount", "op": "ge", "value": 316, "extra_field": "count", "extra_mod": 0, "score": 226, "tag": "现场-18"},
{"id": "R19", "field": "amount", "op": "ge", "value": 333, "extra_field": "count", "extra_mod": 4, "score": 233, "tag": "现场-19"},
{"id": "R20", "field": "amount", "op": "ge", "value": 350, "extra_field": "count", "extra_mod": 8, "score": 240, "tag": "现场-20"},
{"id": "R21", "field": "amount", "op": "ge", "value": 367, "extra_field": "count", "extra_mod": 3, "score": 247, "tag": "现场-21"},
{"id": "R22", "field": "amount", "op": "lt", "value": 384, "extra_field": "count", "extra_mod": 7, "score": 254, "tag": "现场-22"},
{"id": "R23", "field": "amount", "op": "ge", "value": 401, "extra_field": "count", "extra_mod": 2, "score": 261, "tag": "现场-23"},
{"id": "R24", "field": "amount", "op": "ge", "value": 418, "extra_field": "count", "extra_mod": 6, "score": 268, "tag": "现场-24"},
{"id": "R25", "field": "amount", "op": "ge", "value": 435, "extra_field": "count", "extra_mod": 1, "score": 275, "tag": "现场-25"},
{"id": "R26", "field": "amount", "op": "ge", "value": 452, "extra_field": "count", "extra_mod": 5, "score": 282, "tag": "现场-26"},
{"id": "R27", "field": "amount", "op": "lt", "value": 469, "extra_field": "count", "extra_mod": 0, "score": 289, "tag": "现场-27"},
{"id": "R28", "field": "amount", "op": "ge", "value": 486, "extra_field": "count", "extra_mod": 4, "score": 296, "tag": "现场-28"},
{"id": "R29", "field": "amount", "op": "ge", "value": 503, "extra_field": "count", "extra_mod": 8, "score": 303, "tag": "现场-29"},
{"id": "R30", "field": "amount", "op": "ge", "value": 520, "extra_field": "count", "extra_mod": 3, "score": 310, "tag": "现场-30"},
{"id": "R31", "field": "amount", "op": "ge", "value": 537, "extra_field": "count", "extra_mod": 7, "score": 317, "tag": "现场-31"},
{"id": "R32", "field": "amount", "op": "lt", "value": 554, "extra_field": "count", "extra_mod": 2, "score": 324, "tag": "现场-32"},
{"id": "R33", "field": "amount", "op": "ge", "value": 571, "extra_field": "count", "extra_mod": 6, "score": 331, "tag": "现场-33"},
{"id": "R34", "field": "amount", "op": "ge", "value": 588, "extra_field": "count", "extra_mod": 1, "score": 338, "tag": "现场-34"},
{"id": "R35", "field": "amount", "op": "ge", "value": 605, "extra_field": "count", "extra_mod": 5, "score": 345, "tag": "现场-35"},
{"id": "R36", "field": "amount", "op": "ge", "value": 622, "extra_field": "count", "extra_mod": 0, "score": 352, "tag": "现场-36"},
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
    return {"hits": hits, "score": total, "theme": "现场"}


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
