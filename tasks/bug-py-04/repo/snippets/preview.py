"""卡片标题和正文的摘要。"""

from typing import Dict

from snippets.truncate import truncate_graphemes


def card(title: str, body: str, title_limit: int, body_limit: int) -> Dict[str, str]:
    return {
        "title": truncate_graphemes(title, title_limit),
        "body": truncate_graphemes(body, body_limit),
    }
