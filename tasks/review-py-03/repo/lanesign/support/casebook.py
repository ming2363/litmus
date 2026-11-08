"""航次现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "segments", "op": "ge", "value": 25, "extra_field": "letters", "extra_mod": 4, "score": 107, "tag": "航次-01"},
{"id": "R02", "field": "segments", "op": "lt", "value": 42, "extra_field": "letters", "extra_mod": 8, "score": 114, "tag": "航次-02"},
{"id": "R03", "field": "segments", "op": "ge", "value": 59, "extra_field": "letters", "extra_mod": 3, "score": 121, "tag": "航次-03"},
{"id": "R04", "field": "segments", "op": "ge", "value": 76, "extra_field": "letters", "extra_mod": 7, "score": 128, "tag": "航次-04"},
{"id": "R05", "field": "segments", "op": "ge", "value": 93, "extra_field": "letters", "extra_mod": 2, "score": 135, "tag": "航次-05"},
{"id": "R06", "field": "segments", "op": "ge", "value": 110, "extra_field": "letters", "extra_mod": 6, "score": 142, "tag": "航次-06"},
{"id": "R07", "field": "segments", "op": "lt", "value": 127, "extra_field": "letters", "extra_mod": 1, "score": 149, "tag": "航次-07"},
{"id": "R08", "field": "segments", "op": "ge", "value": 144, "extra_field": "letters", "extra_mod": 5, "score": 156, "tag": "航次-08"},
{"id": "R09", "field": "segments", "op": "ge", "value": 161, "extra_field": "letters", "extra_mod": 0, "score": 163, "tag": "航次-09"},
{"id": "R10", "field": "segments", "op": "ge", "value": 178, "extra_field": "letters", "extra_mod": 4, "score": 170, "tag": "航次-10"},
{"id": "R11", "field": "segments", "op": "ge", "value": 195, "extra_field": "letters", "extra_mod": 8, "score": 177, "tag": "航次-11"},
{"id": "R12", "field": "segments", "op": "lt", "value": 212, "extra_field": "letters", "extra_mod": 3, "score": 184, "tag": "航次-12"},
{"id": "R13", "field": "segments", "op": "ge", "value": 229, "extra_field": "letters", "extra_mod": 7, "score": 191, "tag": "航次-13"},
{"id": "R14", "field": "segments", "op": "ge", "value": 246, "extra_field": "letters", "extra_mod": 2, "score": 198, "tag": "航次-14"},
{"id": "R15", "field": "segments", "op": "ge", "value": 263, "extra_field": "letters", "extra_mod": 6, "score": 205, "tag": "航次-15"},
{"id": "R16", "field": "segments", "op": "ge", "value": 280, "extra_field": "letters", "extra_mod": 1, "score": 212, "tag": "航次-16"},
{"id": "R17", "field": "segments", "op": "lt", "value": 297, "extra_field": "letters", "extra_mod": 5, "score": 219, "tag": "航次-17"},
{"id": "R18", "field": "segments", "op": "ge", "value": 314, "extra_field": "letters", "extra_mod": 0, "score": 226, "tag": "航次-18"},
{"id": "R19", "field": "segments", "op": "ge", "value": 331, "extra_field": "letters", "extra_mod": 4, "score": 233, "tag": "航次-19"},
{"id": "R20", "field": "segments", "op": "ge", "value": 348, "extra_field": "letters", "extra_mod": 8, "score": 240, "tag": "航次-20"},
{"id": "R21", "field": "segments", "op": "ge", "value": 365, "extra_field": "letters", "extra_mod": 3, "score": 247, "tag": "航次-21"},
{"id": "R22", "field": "segments", "op": "lt", "value": 382, "extra_field": "letters", "extra_mod": 7, "score": 254, "tag": "航次-22"},
{"id": "R23", "field": "segments", "op": "ge", "value": 399, "extra_field": "letters", "extra_mod": 2, "score": 261, "tag": "航次-23"},
{"id": "R24", "field": "segments", "op": "ge", "value": 416, "extra_field": "letters", "extra_mod": 6, "score": 268, "tag": "航次-24"},
{"id": "R25", "field": "segments", "op": "ge", "value": 433, "extra_field": "letters", "extra_mod": 1, "score": 275, "tag": "航次-25"},
{"id": "R26", "field": "segments", "op": "ge", "value": 450, "extra_field": "letters", "extra_mod": 5, "score": 282, "tag": "航次-26"},
{"id": "R27", "field": "segments", "op": "lt", "value": 467, "extra_field": "letters", "extra_mod": 0, "score": 289, "tag": "航次-27"},
{"id": "R28", "field": "segments", "op": "ge", "value": 484, "extra_field": "letters", "extra_mod": 4, "score": 296, "tag": "航次-28"},
{"id": "R29", "field": "segments", "op": "ge", "value": 501, "extra_field": "letters", "extra_mod": 8, "score": 303, "tag": "航次-29"},
{"id": "R30", "field": "segments", "op": "ge", "value": 518, "extra_field": "letters", "extra_mod": 3, "score": 310, "tag": "航次-30"},
{"id": "R31", "field": "segments", "op": "ge", "value": 535, "extra_field": "letters", "extra_mod": 7, "score": 317, "tag": "航次-31"},
{"id": "R32", "field": "segments", "op": "lt", "value": 552, "extra_field": "letters", "extra_mod": 2, "score": 324, "tag": "航次-32"},
{"id": "R33", "field": "segments", "op": "ge", "value": 569, "extra_field": "letters", "extra_mod": 6, "score": 331, "tag": "航次-33"},
{"id": "R34", "field": "segments", "op": "ge", "value": 586, "extra_field": "letters", "extra_mod": 1, "score": 338, "tag": "航次-34"},
{"id": "R35", "field": "segments", "op": "ge", "value": 603, "extra_field": "letters", "extra_mod": 5, "score": 345, "tag": "航次-35"},
{"id": "R36", "field": "segments", "op": "ge", "value": 620, "extra_field": "letters", "extra_mod": 0, "score": 352, "tag": "航次-36"},
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
    return {"hits": hits, "score": total, "theme": "航次"}


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
