from functools import partial
from copy import deepcopy


class ReduxToolkit:
    def __init__(self, reducer, initial_state):
        self.reducer = reducer
        self.state = deepcopy(initial_state)
        self.listeners = []

    def get_state(self):
        """Return the current state."""
        return deepcopy(self.state)

    def dispatch(self, action):
        """Dispatch an action to update the state."""
        self.state = self.reducer(self.state, action)
        for listener in self.listeners:
            listener()

    def subscribe(self, listener):
        """Subscribe a listener to state changes."""
        self.listeners.append(listener)
        return partial(self.unsubscribe, listener)

    def unsubscribe(self, listener):
        """Unsubscribe a listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)


def create_store(reducer, initial_state):
    """Factory function to create a ReduxToolkit store."""
    return ReduxToolkit(reducer, initial_state)


# # Example usage
# if __name__ == "__main__":
#     # Define an example reducer
#     def example_reducer(state, action):
#         if action["type"] == "INCREMENT":
#             state["count"] += 1
#         elif action["type"] == "DECREMENT":
#             state["count"] -= 1
#         elif action["type"] == "RESET":
#             state["count"] = 0
#         return state

#     # Initial state
#     initial_state = {"count": 0}

#     # Create the store
#     store = create_store(example_reducer, initial_state)

#     # Subscribe to state changes
#     def print_state():
#         print("State updated:", store.get_state())

#     unsubscribe = store.subscribe(print_state)

#     # Dispatch actions
#     store.dispatch({"type": "INCREMENT"})
#     store.dispatch({"type": "INCREMENT"})
#     store.dispatch({"type": "DECREMENT"})
#     store.dispatch({"type": "RESET"})

#     # Unsubscribe and dispatch another action
#     unsubscribe()
#     store.dispatch({"type": "INCREMENT"})
