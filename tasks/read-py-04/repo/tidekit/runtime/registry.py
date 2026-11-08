"""插件登记表。"""


class PluginRec(object):
    """一条登记。"""

    def __init__(self, family, plugin_id, priority, needs, stage, cls):
        self.family = family
        self.plugin_id = plugin_id
        self.priority = priority
        self.needs = tuple(needs)
        self.stage = stage
        self.cls = cls

    def spawn(self):
        return self.cls()


class Registry(object):
    """按导入顺序保存登记。"""

    def __init__(self):
        self.rows = []

    def add(self, rec):
        self.rows.append(rec)

    def by_family(self, family):
        return [rec for rec in self.rows if rec.family == family]


REGISTRY = Registry()


def plugin(family, plugin_id, priority, needs):
    """登记装饰器。需要放在 stage 装饰器外面。"""

    def deco(cls):
        stage = getattr(cls, "stage_prefix", "")
        REGISTRY.add(PluginRec(family, plugin_id, priority, needs, stage, cls))
        return cls

    return deco


def stage(prefix):
    """给类记下方法前缀。"""

    def deco(cls):
        cls.stage_prefix = prefix
        return cls

    return deco
