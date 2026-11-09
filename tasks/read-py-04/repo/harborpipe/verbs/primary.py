"""主表登记。"""

from harborpipe.verbs.book import alias


@alias("audit", "audit", 1)
def audit_as_audit() -> str:
    return "audit"


@alias("settle", "settle", 1)
def settle_as_settle() -> str:
    return "settle"
