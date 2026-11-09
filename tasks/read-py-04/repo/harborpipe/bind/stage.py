"""把动词收成可调用对象。"""

from typing import Any

from harborpipe.wrap.bind import WRAP_REGISTRY
from harborpipe.wrap.shell import Freeze, Loud, Sample, Stamp, seal


class Stage:
    def __init__(self, prefix: str = "do") -> None:
        self.prefix = prefix

    def materialize(self, plugin: Any, verb: str) -> Any:
        name = "{}_{}".format(self.prefix, verb)
        found = getattr(plugin, name, None)
        if found is None:
            found = getattr(plugin, "perform_" + verb, None)
        chosen = [item for item in WRAP_REGISTRY if item[0] == verb]
        chosen.sort(key=lambda item: (item[1], item[3]))
        wrapped = found
        for _verb, _priority, kind, _seq in chosen:
            if kind == "stamp":
                wrapped = Stamp(wrapped)
            elif kind == "sample":
                wrapped = Sample(wrapped)
            elif kind == "freeze":
                wrapped = Freeze(wrapped)
            elif kind == "seal":
                wrapped = seal(wrapped)
            elif kind == "loud":
                wrapped = Loud(wrapped)
        return wrapped


class StageLegacy:
    def __init__(self) -> None:
        self.prefix = "run"

    def materialize(self, plugin: Any, verb: str) -> Any:
        name = "{}_{}".format(self.prefix, verb)
        return getattr(plugin, name)
