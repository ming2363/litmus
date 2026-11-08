"""导入即登记。顺序不影响优先级。"""

from tidekit.plugins.legacy_tide import TideLegacyPlugin
from tidekit.plugins.peek_tide import TidePeekPlugin
from tidekit.plugins.quick_tide import TideQuickPlugin
from tidekit.plugins.fold_tide import TideFoldPlugin
from tidekit.plugins.box_tide import TideBoxPlugin

__all__ = [
    "TideLegacyPlugin",
    "TidePeekPlugin",
    "TideQuickPlugin",
    "TideFoldPlugin",
    "TideBoxPlugin",
]
