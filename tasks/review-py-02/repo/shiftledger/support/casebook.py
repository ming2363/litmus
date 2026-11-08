"""班次现场规则解释器。

规则表是数据，解释器按顺序收集命中项，不短路。
"""


RULES = [
        {"id": "R01", "field": "delta_fen", "op": "ge", "value": 8017, "extra_field": "lines", "extra_mod": 4, "score": 107, "tag": "班次-01"},
{"id": "R02", "field": "delta_fen", "op": "lt", "value": 8034, "extra_field": "lines", "extra_mod": 8, "score": 114, "tag": "班次-02"},
{"id": "R03", "field": "delta_fen", "op": "ge", "value": 8051, "extra_field": "lines", "extra_mod": 3, "score": 121, "tag": "班次-03"},
{"id": "R04", "field": "delta_fen", "op": "ge", "value": 8068, "extra_field": "lines", "extra_mod": 7, "score": 128, "tag": "班次-04"},
{"id": "R05", "field": "delta_fen", "op": "ge", "value": 8085, "extra_field": "lines", "extra_mod": 2, "score": 135, "tag": "班次-05"},
{"id": "R06", "field": "delta_fen", "op": "ge", "value": 8102, "extra_field": "lines", "extra_mod": 6, "score": 142, "tag": "班次-06"},
{"id": "R07", "field": "delta_fen", "op": "lt", "value": 8119, "extra_field": "lines", "extra_mod": 1, "score": 149, "tag": "班次-07"},
{"id": "R08", "field": "delta_fen", "op": "ge", "value": 8136, "extra_field": "lines", "extra_mod": 5, "score": 156, "tag": "班次-08"},
{"id": "R09", "field": "delta_fen", "op": "ge", "value": 8153, "extra_field": "lines", "extra_mod": 0, "score": 163, "tag": "班次-09"},
{"id": "R10", "field": "delta_fen", "op": "ge", "value": 8170, "extra_field": "lines", "extra_mod": 4, "score": 170, "tag": "班次-10"},
{"id": "R11", "field": "delta_fen", "op": "ge", "value": 8187, "extra_field": "lines", "extra_mod": 8, "score": 177, "tag": "班次-11"},
{"id": "R12", "field": "delta_fen", "op": "lt", "value": 8204, "extra_field": "lines", "extra_mod": 3, "score": 184, "tag": "班次-12"},
{"id": "R13", "field": "delta_fen", "op": "ge", "value": 8221, "extra_field": "lines", "extra_mod": 7, "score": 191, "tag": "班次-13"},
{"id": "R14", "field": "delta_fen", "op": "ge", "value": 8238, "extra_field": "lines", "extra_mod": 2, "score": 198, "tag": "班次-14"},
{"id": "R15", "field": "delta_fen", "op": "ge", "value": 8255, "extra_field": "lines", "extra_mod": 6, "score": 205, "tag": "班次-15"},
{"id": "R16", "field": "delta_fen", "op": "ge", "value": 8272, "extra_field": "lines", "extra_mod": 1, "score": 212, "tag": "班次-16"},
{"id": "R17", "field": "delta_fen", "op": "lt", "value": 8289, "extra_field": "lines", "extra_mod": 5, "score": 219, "tag": "班次-17"},
{"id": "R18", "field": "delta_fen", "op": "ge", "value": 8306, "extra_field": "lines", "extra_mod": 0, "score": 226, "tag": "班次-18"},
{"id": "R19", "field": "delta_fen", "op": "ge", "value": 8323, "extra_field": "lines", "extra_mod": 4, "score": 233, "tag": "班次-19"},
{"id": "R20", "field": "delta_fen", "op": "ge", "value": 8340, "extra_field": "lines", "extra_mod": 8, "score": 240, "tag": "班次-20"},
{"id": "R21", "field": "delta_fen", "op": "ge", "value": 8357, "extra_field": "lines", "extra_mod": 3, "score": 247, "tag": "班次-21"},
{"id": "R22", "field": "delta_fen", "op": "lt", "value": 8374, "extra_field": "lines", "extra_mod": 7, "score": 254, "tag": "班次-22"},
{"id": "R23", "field": "delta_fen", "op": "ge", "value": 8391, "extra_field": "lines", "extra_mod": 2, "score": 261, "tag": "班次-23"},
{"id": "R24", "field": "delta_fen", "op": "ge", "value": 8408, "extra_field": "lines", "extra_mod": 6, "score": 268, "tag": "班次-24"},
{"id": "R25", "field": "delta_fen", "op": "ge", "value": 8425, "extra_field": "lines", "extra_mod": 1, "score": 275, "tag": "班次-25"},
{"id": "R26", "field": "delta_fen", "op": "ge", "value": 8442, "extra_field": "lines", "extra_mod": 5, "score": 282, "tag": "班次-26"},
{"id": "R27", "field": "delta_fen", "op": "lt", "value": 8459, "extra_field": "lines", "extra_mod": 0, "score": 289, "tag": "班次-27"},
{"id": "R28", "field": "delta_fen", "op": "ge", "value": 8476, "extra_field": "lines", "extra_mod": 4, "score": 296, "tag": "班次-28"},
{"id": "R29", "field": "delta_fen", "op": "ge", "value": 8493, "extra_field": "lines", "extra_mod": 8, "score": 303, "tag": "班次-29"},
{"id": "R30", "field": "delta_fen", "op": "ge", "value": 8510, "extra_field": "lines", "extra_mod": 3, "score": 310, "tag": "班次-30"},
{"id": "R31", "field": "delta_fen", "op": "ge", "value": 8527, "extra_field": "lines", "extra_mod": 7, "score": 317, "tag": "班次-31"},
{"id": "R32", "field": "delta_fen", "op": "lt", "value": 8544, "extra_field": "lines", "extra_mod": 2, "score": 324, "tag": "班次-32"},
{"id": "R33", "field": "delta_fen", "op": "ge", "value": 8561, "extra_field": "lines", "extra_mod": 6, "score": 331, "tag": "班次-33"},
{"id": "R34", "field": "delta_fen", "op": "ge", "value": 8578, "extra_field": "lines", "extra_mod": 1, "score": 338, "tag": "班次-34"},
{"id": "R35", "field": "delta_fen", "op": "ge", "value": 8595, "extra_field": "lines", "extra_mod": 5, "score": 345, "tag": "班次-35"},
{"id": "R36", "field": "delta_fen", "op": "ge", "value": 8612, "extra_field": "lines", "extra_mod": 0, "score": 352, "tag": "班次-36"},
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
    return {"hits": hits, "score": total, "theme": "班次"}


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
