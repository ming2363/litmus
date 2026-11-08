"""把二元组折成登记键。"""


class KeyFold(object):
    """键的形状是 范围:动作。"""

    def fold(self, slug):
        """slug 必须是 (动作, 范围)。"""
        if not isinstance(slug, tuple) or len(slug) != 2:
            raise ValueError("slug")
        action, scope = slug
        return scope + ":" + action
