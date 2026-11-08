"""潮窗现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "range_cm", "op": "ge", "value": 197, "extra_field": "samples", "extra_mod": 4, "score": 107, "tag": "潮窗-01"},
{"id": "R02", "field": "range_cm", "op": "lt", "value": 214, "extra_field": "samples", "extra_mod": 8, "score": 114, "tag": "潮窗-02"},
{"id": "R03", "field": "range_cm", "op": "ge", "value": 231, "extra_field": "samples", "extra_mod": 3, "score": 121, "tag": "潮窗-03"},
{"id": "R04", "field": "range_cm", "op": "ge", "value": 248, "extra_field": "samples", "extra_mod": 7, "score": 128, "tag": "潮窗-04"},
{"id": "R05", "field": "range_cm", "op": "ge", "value": 265, "extra_field": "samples", "extra_mod": 2, "score": 135, "tag": "潮窗-05"},
{"id": "R06", "field": "range_cm", "op": "ge", "value": 282, "extra_field": "samples", "extra_mod": 6, "score": 142, "tag": "潮窗-06"},
{"id": "R07", "field": "range_cm", "op": "lt", "value": 299, "extra_field": "samples", "extra_mod": 1, "score": 149, "tag": "潮窗-07"},
{"id": "R08", "field": "range_cm", "op": "ge", "value": 316, "extra_field": "samples", "extra_mod": 5, "score": 156, "tag": "潮窗-08"},
{"id": "R09", "field": "range_cm", "op": "ge", "value": 333, "extra_field": "samples", "extra_mod": 0, "score": 163, "tag": "潮窗-09"},
{"id": "R10", "field": "range_cm", "op": "ge", "value": 350, "extra_field": "samples", "extra_mod": 4, "score": 170, "tag": "潮窗-10"},
{"id": "R11", "field": "range_cm", "op": "ge", "value": 367, "extra_field": "samples", "extra_mod": 8, "score": 177, "tag": "潮窗-11"},
{"id": "R12", "field": "range_cm", "op": "lt", "value": 384, "extra_field": "samples", "extra_mod": 3, "score": 184, "tag": "潮窗-12"},
{"id": "R13", "field": "range_cm", "op": "ge", "value": 401, "extra_field": "samples", "extra_mod": 7, "score": 191, "tag": "潮窗-13"},
{"id": "R14", "field": "range_cm", "op": "ge", "value": 418, "extra_field": "samples", "extra_mod": 2, "score": 198, "tag": "潮窗-14"},
{"id": "R15", "field": "range_cm", "op": "ge", "value": 435, "extra_field": "samples", "extra_mod": 6, "score": 205, "tag": "潮窗-15"},
{"id": "R16", "field": "range_cm", "op": "ge", "value": 452, "extra_field": "samples", "extra_mod": 1, "score": 212, "tag": "潮窗-16"},
{"id": "R17", "field": "range_cm", "op": "lt", "value": 469, "extra_field": "samples", "extra_mod": 5, "score": 219, "tag": "潮窗-17"},
{"id": "R18", "field": "range_cm", "op": "ge", "value": 486, "extra_field": "samples", "extra_mod": 0, "score": 226, "tag": "潮窗-18"},
{"id": "R19", "field": "range_cm", "op": "ge", "value": 503, "extra_field": "samples", "extra_mod": 4, "score": 233, "tag": "潮窗-19"},
{"id": "R20", "field": "range_cm", "op": "ge", "value": 520, "extra_field": "samples", "extra_mod": 8, "score": 240, "tag": "潮窗-20"},
{"id": "R21", "field": "range_cm", "op": "ge", "value": 537, "extra_field": "samples", "extra_mod": 3, "score": 247, "tag": "潮窗-21"},
{"id": "R22", "field": "range_cm", "op": "lt", "value": 554, "extra_field": "samples", "extra_mod": 7, "score": 254, "tag": "潮窗-22"},
{"id": "R23", "field": "range_cm", "op": "ge", "value": 571, "extra_field": "samples", "extra_mod": 2, "score": 261, "tag": "潮窗-23"},
{"id": "R24", "field": "range_cm", "op": "ge", "value": 588, "extra_field": "samples", "extra_mod": 6, "score": 268, "tag": "潮窗-24"},
{"id": "R25", "field": "range_cm", "op": "ge", "value": 605, "extra_field": "samples", "extra_mod": 1, "score": 275, "tag": "潮窗-25"},
{"id": "R26", "field": "range_cm", "op": "ge", "value": 622, "extra_field": "samples", "extra_mod": 5, "score": 282, "tag": "潮窗-26"},
{"id": "R27", "field": "range_cm", "op": "lt", "value": 639, "extra_field": "samples", "extra_mod": 0, "score": 289, "tag": "潮窗-27"},
{"id": "R28", "field": "range_cm", "op": "ge", "value": 656, "extra_field": "samples", "extra_mod": 4, "score": 296, "tag": "潮窗-28"},
{"id": "R29", "field": "range_cm", "op": "ge", "value": 673, "extra_field": "samples", "extra_mod": 8, "score": 303, "tag": "潮窗-29"},
{"id": "R30", "field": "range_cm", "op": "ge", "value": 690, "extra_field": "samples", "extra_mod": 3, "score": 310, "tag": "潮窗-30"},
{"id": "R31", "field": "range_cm", "op": "ge", "value": 707, "extra_field": "samples", "extra_mod": 7, "score": 317, "tag": "潮窗-31"},
{"id": "R32", "field": "range_cm", "op": "lt", "value": 724, "extra_field": "samples", "extra_mod": 2, "score": 324, "tag": "潮窗-32"},
{"id": "R33", "field": "range_cm", "op": "ge", "value": 741, "extra_field": "samples", "extra_mod": 6, "score": 331, "tag": "潮窗-33"},
{"id": "R34", "field": "range_cm", "op": "ge", "value": 758, "extra_field": "samples", "extra_mod": 1, "score": 338, "tag": "潮窗-34"},
{"id": "R35", "field": "range_cm", "op": "ge", "value": 775, "extra_field": "samples", "extra_mod": 5, "score": 345, "tag": "潮窗-35"},
{"id": "R36", "field": "range_cm", "op": "ge", "value": 792, "extra_field": "samples", "extra_mod": 0, "score": 352, "tag": "潮窗-36"},
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
    return {"hits": hits, "score": total, "theme": "潮窗"}


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
