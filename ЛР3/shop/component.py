import weakref


class Component:
    def __init__(self):
        self._mediator = None

    def set_mediator(self, mediator):
        self._mediator = weakref.ref(mediator)

    def get_mediator(self):
        if self._mediator is None:
            return None
        return self._mediator()
