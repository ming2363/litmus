"""胸卡落库。"""

from badgedesk.pipelines.sinks import PipelineFactory
from badgedesk.transforms.checksum import TailStep
from badgedesk.transforms.persist import WidthStep


class BadgeWriter(object):
    """写 guest_badge 表。"""

    def __init__(self):
        self.rows = []
        self.logs = []

    def write_guest(self, raw):
        """raw 含 badge_raw。只把列 badge_code 的结果放进 rows。"""
        steps = PipelineFactory.for_sink("badge_code")
        steps.append(TailStep())
        steps.append(WidthStep())
        value = raw["badge_raw"]
        for step in steps:
            value = step.apply(value)
        log_steps = PipelineFactory.for_sink("badge_log")
        logged = raw["badge_raw"]
        for step in log_steps:
            logged = step.apply(logged)
        self.logs.append(logged)
        self.rows.append({"badge_code": value})
        return value
