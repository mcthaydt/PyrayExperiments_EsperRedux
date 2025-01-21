import esper
from components import Collectible, PlayerControlled, Position
from state import store


class ECSStoreSynchronizer:
    def __init__(self):
        store.subscribe(self.sync_ecs_with_store)

    def sync_ecs_with_store(self):
        """Sync ECS components with the store state."""
        state = store.get_state()

        # Sync player position
        for _, (pos, _) in esper.get_components(Position, PlayerControlled):
            player_pos = state["player"]["position"]
            pos.x, pos.y = player_pos["x"], player_pos["y"]

        # Sync stick positions and states
        for i, (_, (pos, col)) in enumerate(
            esper.get_components(Position, Collectible)
        ):
            if i < len(state["sticks"]):
                stick = state["sticks"][i]
                pos.x = stick["position"]["x"]
                pos.y = stick["position"]["y"]
                col.active = stick["collectible"]
