"""展示链路，不写库。"""

from badgedesk.pipelines.sinks import PipelineFactory


def preview_names():
    """展示用的步骤名。"""
    return PipelineFactory.for_sink("badge_display")
