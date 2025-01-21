from functools import partial
from copy import deepcopy


class ReduxToolkit:
    def __init__(self, reducer, initial_state):
        self.reducer = reducer
        self.state = deepcopy(initial_state)
        self.listeners = []

    def get_state(self):
        return deepcopy(self.state)

    def dispatch(self, action):
        self.state = self.reducer(self.state, action)
        for listener in self.listeners:
            listener()

    def subscribe(self, listener):
        self.listeners.append(listener)
        return partial(self.unsubscribe, listener)

    def unsubscribe(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)


def create_store(reducer, initial_state):
    return ReduxToolkit(reducer, initial_state)
