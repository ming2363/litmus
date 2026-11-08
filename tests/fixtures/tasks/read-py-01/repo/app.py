class Dispatcher:
    def dispatch(self, ev):
        return self._route(ev)

    def _route(self, ev):
        return self._handle(ev)

    def _handle(self, ev):
        return ev
