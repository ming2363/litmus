"""访客现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "stay_min", "op": "ge", "value": 257, "extra_field": "escorts", "extra_mod": 4, "score": 107, "tag": "访客-01"},
{"id": "R02", "field": "stay_min", "op": "lt", "value": 274, "extra_field": "escorts", "extra_mod": 8, "score": 114, "tag": "访客-02"},
{"id": "R03", "field": "stay_min", "op": "ge", "value": 291, "extra_field": "escorts", "extra_mod": 3, "score": 121, "tag": "访客-03"},
{"id": "R04", "field": "stay_min", "op": "ge", "value": 308, "extra_field": "escorts", "extra_mod": 7, "score": 128, "tag": "访客-04"},
{"id": "R05", "field": "stay_min", "op": "ge", "value": 325, "extra_field": "escorts", "extra_mod": 2, "score": 135, "tag": "访客-05"},
{"id": "R06", "field": "stay_min", "op": "ge", "value": 342, "extra_field": "escorts", "extra_mod": 6, "score": 142, "tag": "访客-06"},
{"id": "R07", "field": "stay_min", "op": "lt", "value": 359, "extra_field": "escorts", "extra_mod": 1, "score": 149, "tag": "访客-07"},
{"id": "R08", "field": "stay_min", "op": "ge", "value": 376, "extra_field": "escorts", "extra_mod": 5, "score": 156, "tag": "访客-08"},
{"id": "R09", "field": "stay_min", "op": "ge", "value": 393, "extra_field": "escorts", "extra_mod": 0, "score": 163, "tag": "访客-09"},
{"id": "R10", "field": "stay_min", "op": "ge", "value": 410, "extra_field": "escorts", "extra_mod": 4, "score": 170, "tag": "访客-10"},
{"id": "R11", "field": "stay_min", "op": "ge", "value": 427, "extra_field": "escorts", "extra_mod": 8, "score": 177, "tag": "访客-11"},
{"id": "R12", "field": "stay_min", "op": "lt", "value": 444, "extra_field": "escorts", "extra_mod": 3, "score": 184, "tag": "访客-12"},
{"id": "R13", "field": "stay_min", "op": "ge", "value": 461, "extra_field": "escorts", "extra_mod": 7, "score": 191, "tag": "访客-13"},
{"id": "R14", "field": "stay_min", "op": "ge", "value": 478, "extra_field": "escorts", "extra_mod": 2, "score": 198, "tag": "访客-14"},
{"id": "R15", "field": "stay_min", "op": "ge", "value": 495, "extra_field": "escorts", "extra_mod": 6, "score": 205, "tag": "访客-15"},
{"id": "R16", "field": "stay_min", "op": "ge", "value": 512, "extra_field": "escorts", "extra_mod": 1, "score": 212, "tag": "访客-16"},
{"id": "R17", "field": "stay_min", "op": "lt", "value": 529, "extra_field": "escorts", "extra_mod": 5, "score": 219, "tag": "访客-17"},
{"id": "R18", "field": "stay_min", "op": "ge", "value": 546, "extra_field": "escorts", "extra_mod": 0, "score": 226, "tag": "访客-18"},
{"id": "R19", "field": "stay_min", "op": "ge", "value": 563, "extra_field": "escorts", "extra_mod": 4, "score": 233, "tag": "访客-19"},
{"id": "R20", "field": "stay_min", "op": "ge", "value": 580, "extra_field": "escorts", "extra_mod": 8, "score": 240, "tag": "访客-20"},
{"id": "R21", "field": "stay_min", "op": "ge", "value": 597, "extra_field": "escorts", "extra_mod": 3, "score": 247, "tag": "访客-21"},
{"id": "R22", "field": "stay_min", "op": "lt", "value": 614, "extra_field": "escorts", "extra_mod": 7, "score": 254, "tag": "访客-22"},
{"id": "R23", "field": "stay_min", "op": "ge", "value": 631, "extra_field": "escorts", "extra_mod": 2, "score": 261, "tag": "访客-23"},
{"id": "R24", "field": "stay_min", "op": "ge", "value": 648, "extra_field": "escorts", "extra_mod": 6, "score": 268, "tag": "访客-24"},
{"id": "R25", "field": "stay_min", "op": "ge", "value": 665, "extra_field": "escorts", "extra_mod": 1, "score": 275, "tag": "访客-25"},
{"id": "R26", "field": "stay_min", "op": "ge", "value": 682, "extra_field": "escorts", "extra_mod": 5, "score": 282, "tag": "访客-26"},
{"id": "R27", "field": "stay_min", "op": "lt", "value": 699, "extra_field": "escorts", "extra_mod": 0, "score": 289, "tag": "访客-27"},
{"id": "R28", "field": "stay_min", "op": "ge", "value": 716, "extra_field": "escorts", "extra_mod": 4, "score": 296, "tag": "访客-28"},
{"id": "R29", "field": "stay_min", "op": "ge", "value": 733, "extra_field": "escorts", "extra_mod": 8, "score": 303, "tag": "访客-29"},
{"id": "R30", "field": "stay_min", "op": "ge", "value": 750, "extra_field": "escorts", "extra_mod": 3, "score": 310, "tag": "访客-30"},
{"id": "R31", "field": "stay_min", "op": "ge", "value": 767, "extra_field": "escorts", "extra_mod": 7, "score": 317, "tag": "访客-31"},
{"id": "R32", "field": "stay_min", "op": "lt", "value": 784, "extra_field": "escorts", "extra_mod": 2, "score": 324, "tag": "访客-32"},
{"id": "R33", "field": "stay_min", "op": "ge", "value": 801, "extra_field": "escorts", "extra_mod": 6, "score": 331, "tag": "访客-33"},
{"id": "R34", "field": "stay_min", "op": "ge", "value": 818, "extra_field": "escorts", "extra_mod": 1, "score": 338, "tag": "访客-34"},
{"id": "R35", "field": "stay_min", "op": "ge", "value": 835, "extra_field": "escorts", "extra_mod": 5, "score": 345, "tag": "访客-35"},
{"id": "R36", "field": "stay_min", "op": "ge", "value": 852, "extra_field": "escorts", "extra_mod": 0, "score": 352, "tag": "访客-36"},
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
    return {"hits": hits, "score": total, "theme": "访客"}


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
