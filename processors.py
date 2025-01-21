import esper
import pyray as pr
from actions import Actions
from components import PlayerControlled, Position, Velocity
from state import store


class MovementProcessor:
    def process(self, delta_time):
        """Process player movement based on velocity."""
        for _, (vel, _, _) in esper.get_components(
            Velocity, Position, PlayerControlled
        ):
            store.dispatch(Actions.movePlayer(delta_time))


class CollectionProcessor:
    def process(self):
        """Process stick collection and check for win condition."""
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        if state["player"]["score"] >= 2:
            print("You Win!")


class InputProcessor:
    def process(self, delta_time=None):
        """Process player input to update velocity."""
        for _, (vel, player) in esper.get_components(Velocity, PlayerControlled):
            vel.x = vel.y = 0
            if pr.is_key_down(pr.KEY_W):
                vel.y = -player.speed
            if pr.is_key_down(pr.KEY_S):
                vel.y = player.speed
            if pr.is_key_down(pr.KEY_A):
                vel.x = -player.speed
            if pr.is_key_down(pr.KEY_D):
                vel.x = player.speed
            store.dispatch(Actions.setPlayerVelocity({"x": vel.x, "y": vel.y}))
