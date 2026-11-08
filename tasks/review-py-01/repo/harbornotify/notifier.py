"""传感器事件转成通知文本。"""

from harbornotify.lookup import BerthLookup


class IdleNotifier(object):
    """空闲与占用分开措辞。"""

    def __init__(self, lookup=None):
        self.lookup = lookup or BerthLookup()

    def render_occupied(self, berth):
        """占用通知。调用前已经确认 berth 不是 None。"""
        return "占用：" + berth["display_name"].strip()

    def on_sensor(self, event):
        """kind 为 occupied 或 idle。底账没有该泊位时 lookup 返回 None。"""
        berth = self.lookup.find(event["berth_id"])
        if event["kind"] == "occupied":
            if berth is None:
                return "未知泊位"
            return self.render_occupied(berth)
        minute = event.get("minute", 0)
        if isinstance(minute, bool) or not isinstance(minute, int):
            minute = 0
        label = berth["display_name"].strip()
        zone = berth["zone"]
        return "空闲：" + label + "@" + str(minute) + "（" + zone + "）"
