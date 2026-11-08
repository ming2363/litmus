"""按折好的键调用业务方法。"""

from nightledger.handlers.open_night import NightOpenHandler
from nightledger.handlers.seal_night import NightSealHandler
from nightledger.handlers.seal_yard import YardSealHandler
from nightledger.handlers.void_night import NightVoidHandler


class Binder(object):
    """键不存在时抛出 KeyError。返回业务结果，不返回函数。"""

    def lookup(self, key, payload):
        """正式入账和预览不是同一个方法。"""
        if key == "night:open":
            return NightOpenHandler().apply(payload)
        if key == "night:seal":
            return NightSealHandler().apply(payload)
        if key == "night:void":
            return NightVoidHandler().apply(payload)
        if key == "night:preview":
            return NightSealHandler().preview(payload)
        if key == "yard:seal":
            return YardSealHandler().apply(payload)
        if key == "seal:night":
            return NightSealHandler().preview(payload)
        raise KeyError(key)
