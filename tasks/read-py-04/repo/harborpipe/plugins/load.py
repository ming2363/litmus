"""装载会进入登记表的插件模块。"""


def load() -> None:
    import harborpipe.plugins.cold.audit_primary  # noqa: F401
    import harborpipe.plugins.cold.cold_primary  # noqa: F401
    import harborpipe.plugins.cold.manual_cold  # noqa: F401
    import harborpipe.plugins.cold.reefer_watch  # noqa: F401
    import harborpipe.plugins.cold.seal_cold  # noqa: F401
    import harborpipe.plugins.yard.yard_audit  # noqa: F401
