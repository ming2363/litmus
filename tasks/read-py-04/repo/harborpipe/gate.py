"""调度入口。"""

from typing import Any

from harborpipe.bind.stage import Stage
from harborpipe.config.stack import Stack
from harborpipe.plugins.load import load
from harborpipe.registry.book import Book
from harborpipe.verbs.book import VerbBook
import harborpipe.verbs.compat  # noqa: F401
import harborpipe.verbs.primary  # noqa: F401

load()


class Gate:
    def __init__(self) -> None:
        self.stack = Stack()
        self.book = Book(manual_open=False)
        self.verbs = VerbBook()
        self.stage = Stage("do")
        self.ctx = {"shift": "night"}

    def invoke(self, operation: str) -> Any:
        family = self.stack.family_for(operation)
        plugin_cls = self.book.select(family)
        verb = self.verbs.resolve(operation)
        call = self.stage.materialize(plugin_cls(), verb)
        return call(self.ctx)
