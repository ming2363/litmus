"""不同落点的基础步骤。写库时还会再追加。"""

from badgedesk.transforms.casefold import UpperStep
from badgedesk.transforms.display import QuoteStep
from badgedesk.transforms.homoglyph import DigitStep
from badgedesk.transforms.redact import MaskStep
from badgedesk.transforms.separator import GapStep


SINKS = {
    "badge_code": [UpperStep, DigitStep, GapStep],
    "badge_display": [UpperStep, GapStep, QuoteStep],
    "badge_log": [UpperStep, MaskStep],
}


class PipelineFactory(object):
    """按落点复制基础步骤。"""

    @staticmethod
    def for_sink(name):
        if name not in SINKS:
            raise KeyError(name)
        return [step() for step in SINKS[name]]
