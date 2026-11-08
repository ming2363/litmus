"""滞期现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "minutes", "op": "ge", "value": 737, "extra_field": "holds", "extra_mod": 4, "score": 107, "tag": "滞期-01"},
{"id": "R02", "field": "minutes", "op": "lt", "value": 754, "extra_field": "holds", "extra_mod": 8, "score": 114, "tag": "滞期-02"},
{"id": "R03", "field": "minutes", "op": "ge", "value": 771, "extra_field": "holds", "extra_mod": 3, "score": 121, "tag": "滞期-03"},
{"id": "R04", "field": "minutes", "op": "ge", "value": 788, "extra_field": "holds", "extra_mod": 7, "score": 128, "tag": "滞期-04"},
{"id": "R05", "field": "minutes", "op": "ge", "value": 805, "extra_field": "holds", "extra_mod": 2, "score": 135, "tag": "滞期-05"},
{"id": "R06", "field": "minutes", "op": "ge", "value": 822, "extra_field": "holds", "extra_mod": 6, "score": 142, "tag": "滞期-06"},
{"id": "R07", "field": "minutes", "op": "lt", "value": 839, "extra_field": "holds", "extra_mod": 1, "score": 149, "tag": "滞期-07"},
{"id": "R08", "field": "minutes", "op": "ge", "value": 856, "extra_field": "holds", "extra_mod": 5, "score": 156, "tag": "滞期-08"},
{"id": "R09", "field": "minutes", "op": "ge", "value": 873, "extra_field": "holds", "extra_mod": 0, "score": 163, "tag": "滞期-09"},
{"id": "R10", "field": "minutes", "op": "ge", "value": 890, "extra_field": "holds", "extra_mod": 4, "score": 170, "tag": "滞期-10"},
{"id": "R11", "field": "minutes", "op": "ge", "value": 907, "extra_field": "holds", "extra_mod": 8, "score": 177, "tag": "滞期-11"},
{"id": "R12", "field": "minutes", "op": "lt", "value": 924, "extra_field": "holds", "extra_mod": 3, "score": 184, "tag": "滞期-12"},
{"id": "R13", "field": "minutes", "op": "ge", "value": 941, "extra_field": "holds", "extra_mod": 7, "score": 191, "tag": "滞期-13"},
{"id": "R14", "field": "minutes", "op": "ge", "value": 958, "extra_field": "holds", "extra_mod": 2, "score": 198, "tag": "滞期-14"},
{"id": "R15", "field": "minutes", "op": "ge", "value": 975, "extra_field": "holds", "extra_mod": 6, "score": 205, "tag": "滞期-15"},
{"id": "R16", "field": "minutes", "op": "ge", "value": 992, "extra_field": "holds", "extra_mod": 1, "score": 212, "tag": "滞期-16"},
{"id": "R17", "field": "minutes", "op": "lt", "value": 1009, "extra_field": "holds", "extra_mod": 5, "score": 219, "tag": "滞期-17"},
{"id": "R18", "field": "minutes", "op": "ge", "value": 1026, "extra_field": "holds", "extra_mod": 0, "score": 226, "tag": "滞期-18"},
{"id": "R19", "field": "minutes", "op": "ge", "value": 1043, "extra_field": "holds", "extra_mod": 4, "score": 233, "tag": "滞期-19"},
{"id": "R20", "field": "minutes", "op": "ge", "value": 1060, "extra_field": "holds", "extra_mod": 8, "score": 240, "tag": "滞期-20"},
{"id": "R21", "field": "minutes", "op": "ge", "value": 1077, "extra_field": "holds", "extra_mod": 3, "score": 247, "tag": "滞期-21"},
{"id": "R22", "field": "minutes", "op": "lt", "value": 1094, "extra_field": "holds", "extra_mod": 7, "score": 254, "tag": "滞期-22"},
{"id": "R23", "field": "minutes", "op": "ge", "value": 1111, "extra_field": "holds", "extra_mod": 2, "score": 261, "tag": "滞期-23"},
{"id": "R24", "field": "minutes", "op": "ge", "value": 1128, "extra_field": "holds", "extra_mod": 6, "score": 268, "tag": "滞期-24"},
{"id": "R25", "field": "minutes", "op": "ge", "value": 1145, "extra_field": "holds", "extra_mod": 1, "score": 275, "tag": "滞期-25"},
{"id": "R26", "field": "minutes", "op": "ge", "value": 1162, "extra_field": "holds", "extra_mod": 5, "score": 282, "tag": "滞期-26"},
{"id": "R27", "field": "minutes", "op": "lt", "value": 1179, "extra_field": "holds", "extra_mod": 0, "score": 289, "tag": "滞期-27"},
{"id": "R28", "field": "minutes", "op": "ge", "value": 1196, "extra_field": "holds", "extra_mod": 4, "score": 296, "tag": "滞期-28"},
{"id": "R29", "field": "minutes", "op": "ge", "value": 1213, "extra_field": "holds", "extra_mod": 8, "score": 303, "tag": "滞期-29"},
{"id": "R30", "field": "minutes", "op": "ge", "value": 1230, "extra_field": "holds", "extra_mod": 3, "score": 310, "tag": "滞期-30"},
{"id": "R31", "field": "minutes", "op": "ge", "value": 1247, "extra_field": "holds", "extra_mod": 7, "score": 317, "tag": "滞期-31"},
{"id": "R32", "field": "minutes", "op": "lt", "value": 1264, "extra_field": "holds", "extra_mod": 2, "score": 324, "tag": "滞期-32"},
{"id": "R33", "field": "minutes", "op": "ge", "value": 1281, "extra_field": "holds", "extra_mod": 6, "score": 331, "tag": "滞期-33"},
{"id": "R34", "field": "minutes", "op": "ge", "value": 1298, "extra_field": "holds", "extra_mod": 1, "score": 338, "tag": "滞期-34"},
{"id": "R35", "field": "minutes", "op": "ge", "value": 1315, "extra_field": "holds", "extra_mod": 5, "score": 345, "tag": "滞期-35"},
{"id": "R36", "field": "minutes", "op": "ge", "value": 1332, "extra_field": "holds", "extra_mod": 0, "score": 352, "tag": "滞期-36"},
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
    return {"hits": hits, "score": total, "theme": "滞期"}


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
