"""外部事件入口。"""

from nightledger.catalog.public_names import PublicCatalog
from nightledger.catalog.wire_book import WireBook
from nightledger.dispatch.binder import Binder
from nightledger.dispatch.key_fold import KeyFold


class Ingress(object):
    """接收对外事件名。"""

    def __init__(self):
        self.catalog = PublicCatalog()
        self.wires = WireBook()
        self.fold = KeyFold()
        self.binder = Binder()

    def accept(self, public_name, payload):
        """映射后调用业务函数。返回值是业务结果，不含函数名。"""
        wire = self.catalog.to_wire(public_name)
        slug = self.wires.to_slug(wire)
        key = self.fold.fold(slug)
        return self.binder.lookup(key, payload)
