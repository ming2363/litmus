"""泊位底账，供处理器读取。"""


BERTHS = [
    {"code": "B01", "name": "顺岸1号", "state": "idle", "length_m": 85, "note": "夜班可靠"},
    {"code": "B02", "name": "顺岸2号", "state": "closed", "length_m": 90, "note": "夜班可靠"},
    {"code": "B03", "name": "顺岸3号", "state": "repair", "length_m": 95, "note": "夜班可靠"},
    {"code": "B04", "name": "顺岸4号", "state": "active", "length_m": 100, "note": "夜班可靠"},
    {"code": "B05", "name": "顺岸5号", "state": "idle", "length_m": 105, "note": "夜班可靠"},
    {"code": "B06", "name": "顺岸6号", "state": "closed", "length_m": 110, "note": "夜班可靠"},
    {"code": "B07", "name": "顺岸7号", "state": "repair", "length_m": 115, "note": "夜班可靠"},
    {"code": "B08", "name": "顺岸8号", "state": "active", "length_m": 120, "note": "夜班可靠"},
    {"code": "B09", "name": "顺岸9号", "state": "idle", "length_m": 125, "note": "夜班可靠"},
    {"code": "B10", "name": "顺岸10号", "state": "closed", "length_m": 130, "note": "夜班可靠"},
    {"code": "B11", "name": "顺岸11号", "state": "repair", "length_m": 135, "note": "夜班可靠"},
    {"code": "B12", "name": "顺岸12号", "state": "active", "length_m": 140, "note": "夜班可靠"},
    {"code": "B13", "name": "顺岸13号", "state": "idle", "length_m": 145, "note": "夜班可靠"},
    {"code": "B14", "name": "顺岸14号", "state": "closed", "length_m": 150, "note": "夜班可靠"},
    {"code": "B15", "name": "顺岸15号", "state": "repair", "length_m": 155, "note": "夜班可靠"},
    {"code": "B16", "name": "顺岸16号", "state": "active", "length_m": 160, "note": "夜班可靠"},
    {"code": "B17", "name": "顺岸17号", "state": "idle", "length_m": 165, "note": "夜班可靠"},
    {"code": "B18", "name": "顺岸18号", "state": "closed", "length_m": 170, "note": "夜班可靠"},
    {"code": "B19", "name": "顺岸19号", "state": "repair", "length_m": 175, "note": "夜班可靠"},
    {"code": "B20", "name": "顺岸20号", "state": "active", "length_m": 180, "note": "夜班可靠"},
    {"code": "B21", "name": "顺岸21号", "state": "idle", "length_m": 185, "note": "夜班可靠"},
    {"code": "B22", "name": "顺岸22号", "state": "closed", "length_m": 190, "note": "夜班可靠"},
    {"code": "B23", "name": "顺岸23号", "state": "repair", "length_m": 195, "note": "夜班可靠"},
    {"code": "B24", "name": "顺岸24号", "state": "active", "length_m": 200, "note": "夜班可靠"},
]


def by_state(state):
    """按状态筛选，保持底账顺序。"""
    found = []
    for row in BERTHS:
        if row["state"] == state:
            found.append(dict(row))
    return found
