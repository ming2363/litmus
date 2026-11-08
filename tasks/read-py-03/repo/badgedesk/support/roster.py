"""班次覆盖。一个人同一天不能上两班。"""


SHIFTS = ("dawn", "day", "night")


def assign(people, days, demand):
    """demand[(day, shift)] = 需要人数。按人名排序轮转，人不够就留下空缺。"""
    if not people:
        raise ValueError("people")
    names = sorted(people)
    cursor = 0
    table = {}
    used = set()
    for day in days:
        for shift in SHIFTS:
            need = int(demand.get((day, shift), 0))
            chosen = []
            guard = 0
            while len(chosen) < need and guard < len(names) * 2:
                name = names[cursor % len(names)]
                cursor += 1
                guard += 1
                if (name, day) in used:
                    continue
                used.add((name, day))
                chosen.append(name)
            table[(day, shift)] = chosen
    return table


def uncovered(table, demand):
    """返回仍缺人的 (day, shift, 缺口)。"""
    gaps = []
    for key, need in sorted(demand.items()):
        have = len(table.get(key, ()))
        if have < need:
            gaps.append((key[0], key[1], need - have))
    return gaps


def load_of(table):
    """每个人被排到的班次数。"""
    loads = {}
    for names in table.values():
        for name in names:
            loads[name] = loads.get(name, 0) + 1
    return loads
