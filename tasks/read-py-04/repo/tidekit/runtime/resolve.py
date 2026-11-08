"""选择插件与方法名。"""

from tidekit.runtime.aliases import ACTION_ALIAS
from tidekit.runtime.caps import ACTIVE_CAPS
from tidekit.runtime.registry import REGISTRY


class Resolver(object):
    """优先级数字小的优先，其次比插件 id。"""

    def select(self, family):
        """能力不全的登记直接跳过。"""
        ready = []
        for rec in REGISTRY.by_family(family):
            if all(ACTIVE_CAPS.get(name) for name in rec.needs):
                ready.append(rec)
        if not ready:
            raise LookupError(family)
        ready.sort(key=lambda rec: (rec.priority, rec.plugin_id))
        return ready[0]

    def verb_for(self, rec, action):
        """前缀加下划线加词干。"""
        stem = ACTION_ALIAS[action]
        return rec.stage + "_" + stem
