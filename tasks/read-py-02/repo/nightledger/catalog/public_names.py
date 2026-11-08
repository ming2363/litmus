"""对外事件名只出现在这张表里。"""


class PublicCatalog(object):
    """公开名到线码。"""

    _TABLE = {
        "ledger.nightly.opened": "WL-4E",
        "ledger.nightly.closed": "WL-4F",
        "ledger.nightly.voided": "WL-4G",
        "yard.shift.closed": "YS-2A",
        "ledger.nightly.preview": "WL-4H",
    }

    def to_wire(self, public_name):
        """找不到公开名时抛出 KeyError。"""
        if public_name not in self._TABLE:
            raise KeyError(public_name)
        return self._TABLE[public_name]
