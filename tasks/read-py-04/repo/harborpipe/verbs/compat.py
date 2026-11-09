"""兼容登记。"""

from harborpipe.verbs.book import alias


@alias("audit", "inspect", 5)
def audit_as_inspect() -> str:
    return "inspect"


@alias("probe", "inspect", 1)
def probe_as_inspect() -> str:
    return "inspect"
