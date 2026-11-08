"""部门树汇总。"""


def rollup(nodes, parent_of, value_of):
    """每个节点的值加上全部子孙。nodes 是 id 列表。"""
    children = {node: [] for node in nodes}
    roots = []
    for node in nodes:
        parent = parent_of.get(node)
        if parent is None:
            roots.append(node)
            continue
        if parent not in children:
            raise KeyError(parent)
        children[parent].append(node)
    totals = {}

    def walk(node, stack):
        if node in stack:
            raise ValueError("cycle")
        stack.add(node)
        total = value_of.get(node, 0)
        for child in children[node]:
            total += walk(child, stack)
        stack.remove(node)
        totals[node] = total
        return total

    for root in roots:
        walk(root, set())
    missing = [node for node in nodes if node not in totals]
    for node in missing:
        walk(node, set())
    return totals


def leaves(nodes, parent_of):
    parents = set(parent_of.values())
    return sorted(node for node in nodes if node not in parents)
