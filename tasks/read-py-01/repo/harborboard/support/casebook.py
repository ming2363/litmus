"""停泊现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "draught_m", "op": "ge", "value": 29, "extra_field": "hours", "extra_mod": 4, "score": 107, "tag": "停泊-01"},
{"id": "R02", "field": "draught_m", "op": "lt", "value": 46, "extra_field": "hours", "extra_mod": 8, "score": 114, "tag": "停泊-02"},
{"id": "R03", "field": "draught_m", "op": "ge", "value": 63, "extra_field": "hours", "extra_mod": 3, "score": 121, "tag": "停泊-03"},
{"id": "R04", "field": "draught_m", "op": "ge", "value": 80, "extra_field": "hours", "extra_mod": 7, "score": 128, "tag": "停泊-04"},
{"id": "R05", "field": "draught_m", "op": "ge", "value": 97, "extra_field": "hours", "extra_mod": 2, "score": 135, "tag": "停泊-05"},
{"id": "R06", "field": "draught_m", "op": "ge", "value": 114, "extra_field": "hours", "extra_mod": 6, "score": 142, "tag": "停泊-06"},
{"id": "R07", "field": "draught_m", "op": "lt", "value": 131, "extra_field": "hours", "extra_mod": 1, "score": 149, "tag": "停泊-07"},
{"id": "R08", "field": "draught_m", "op": "ge", "value": 148, "extra_field": "hours", "extra_mod": 5, "score": 156, "tag": "停泊-08"},
{"id": "R09", "field": "draught_m", "op": "ge", "value": 165, "extra_field": "hours", "extra_mod": 0, "score": 163, "tag": "停泊-09"},
{"id": "R10", "field": "draught_m", "op": "ge", "value": 182, "extra_field": "hours", "extra_mod": 4, "score": 170, "tag": "停泊-10"},
{"id": "R11", "field": "draught_m", "op": "ge", "value": 199, "extra_field": "hours", "extra_mod": 8, "score": 177, "tag": "停泊-11"},
{"id": "R12", "field": "draught_m", "op": "lt", "value": 216, "extra_field": "hours", "extra_mod": 3, "score": 184, "tag": "停泊-12"},
{"id": "R13", "field": "draught_m", "op": "ge", "value": 233, "extra_field": "hours", "extra_mod": 7, "score": 191, "tag": "停泊-13"},
{"id": "R14", "field": "draught_m", "op": "ge", "value": 250, "extra_field": "hours", "extra_mod": 2, "score": 198, "tag": "停泊-14"},
{"id": "R15", "field": "draught_m", "op": "ge", "value": 267, "extra_field": "hours", "extra_mod": 6, "score": 205, "tag": "停泊-15"},
{"id": "R16", "field": "draught_m", "op": "ge", "value": 284, "extra_field": "hours", "extra_mod": 1, "score": 212, "tag": "停泊-16"},
{"id": "R17", "field": "draught_m", "op": "lt", "value": 301, "extra_field": "hours", "extra_mod": 5, "score": 219, "tag": "停泊-17"},
{"id": "R18", "field": "draught_m", "op": "ge", "value": 318, "extra_field": "hours", "extra_mod": 0, "score": 226, "tag": "停泊-18"},
{"id": "R19", "field": "draught_m", "op": "ge", "value": 335, "extra_field": "hours", "extra_mod": 4, "score": 233, "tag": "停泊-19"},
{"id": "R20", "field": "draught_m", "op": "ge", "value": 352, "extra_field": "hours", "extra_mod": 8, "score": 240, "tag": "停泊-20"},
{"id": "R21", "field": "draught_m", "op": "ge", "value": 369, "extra_field": "hours", "extra_mod": 3, "score": 247, "tag": "停泊-21"},
{"id": "R22", "field": "draught_m", "op": "lt", "value": 386, "extra_field": "hours", "extra_mod": 7, "score": 254, "tag": "停泊-22"},
{"id": "R23", "field": "draught_m", "op": "ge", "value": 403, "extra_field": "hours", "extra_mod": 2, "score": 261, "tag": "停泊-23"},
{"id": "R24", "field": "draught_m", "op": "ge", "value": 420, "extra_field": "hours", "extra_mod": 6, "score": 268, "tag": "停泊-24"},
{"id": "R25", "field": "draught_m", "op": "ge", "value": 437, "extra_field": "hours", "extra_mod": 1, "score": 275, "tag": "停泊-25"},
{"id": "R26", "field": "draught_m", "op": "ge", "value": 454, "extra_field": "hours", "extra_mod": 5, "score": 282, "tag": "停泊-26"},
{"id": "R27", "field": "draught_m", "op": "lt", "value": 471, "extra_field": "hours", "extra_mod": 0, "score": 289, "tag": "停泊-27"},
{"id": "R28", "field": "draught_m", "op": "ge", "value": 488, "extra_field": "hours", "extra_mod": 4, "score": 296, "tag": "停泊-28"},
{"id": "R29", "field": "draught_m", "op": "ge", "value": 505, "extra_field": "hours", "extra_mod": 8, "score": 303, "tag": "停泊-29"},
{"id": "R30", "field": "draught_m", "op": "ge", "value": 522, "extra_field": "hours", "extra_mod": 3, "score": 310, "tag": "停泊-30"},
{"id": "R31", "field": "draught_m", "op": "ge", "value": 539, "extra_field": "hours", "extra_mod": 7, "score": 317, "tag": "停泊-31"},
{"id": "R32", "field": "draught_m", "op": "lt", "value": 556, "extra_field": "hours", "extra_mod": 2, "score": 324, "tag": "停泊-32"},
{"id": "R33", "field": "draught_m", "op": "ge", "value": 573, "extra_field": "hours", "extra_mod": 6, "score": 331, "tag": "停泊-33"},
{"id": "R34", "field": "draught_m", "op": "ge", "value": 590, "extra_field": "hours", "extra_mod": 1, "score": 338, "tag": "停泊-34"},
{"id": "R35", "field": "draught_m", "op": "ge", "value": 607, "extra_field": "hours", "extra_mod": 5, "score": 345, "tag": "停泊-35"},
{"id": "R36", "field": "draught_m", "op": "ge", "value": 624, "extra_field": "hours", "extra_mod": 0, "score": 352, "tag": "停泊-36"},
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
    return {"hits": hits, "score": total, "theme": "停泊"}


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
