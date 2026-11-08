"""生效路由表。顺序参与字面路径的先后判定。"""


ROUTES = [
    ("GET", "/harbor/v2/berths", "berth.list"),
    ("GET", "/harbor/v2/berths/activity", "berth.activity"),
    ("GET", "/harbor/v2/berths/{view}", "berth.view"),
    ("POST", "/harbor/v2/berths/active", "berth.activate"),
    ("GET", "/harbor/v2/berths/active", "berth.active"),
    ("GET", "/harbor/v2/yards/{yard}/map", "yard.map"),
    ("GET", "/harbor/v2/tide/windows", "tide.windows"),
    ("PUT", "/harbor/v2/berths/{code}/note", "berth.note"),
    ("GET", "/harbor/v1/berths/active", "berth.legacy"),
    ("GET", "/harbor/v2/berths/active/export", "berth.export"),
    ("DELETE", "/harbor/v2/berths/{code}", "berth.close"),
]
