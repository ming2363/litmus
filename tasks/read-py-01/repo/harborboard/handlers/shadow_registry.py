"""草稿登记，路由不会读取这份表。"""


SHADOW_HANDLERS = {
    "berth.active": "harborboard.handlers.legacy.LegacyActiveHandler#dump",
    "berth.list": "harborboard.handlers.legacy.LegacyActiveHandler#dump",
}


SHADOW_ROUTES = [
    ("GET", "/harbor/v2/berths/active", "berth.legacy"),
]
