"""停用登记，单独一张表。"""

from typing import List, Tuple

RETIRED: List[Tuple[str, str]] = [
    ("audit", "audit"),
    ("lane.reefer.audit", "audit"),
    ("inspect", "inspect"),
]


def lookup(operation: str) -> str:
    stem = operation.rsplit(".", 1)[-1]
    for key, verb in RETIRED:
        if key == operation or key == stem:
            return verb
    raise KeyError(operation)
