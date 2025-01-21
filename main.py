import random
from dataclasses import dataclass as component
import esper
import pyray as pr
from redux_toolkit import create_store
from actions import Actions


# Components
@component
class Position:
    x: int = 0
    y: int = 0


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class PlayerControlled:
    speed: float = 200.0


@component
class Collectible:
    active: bool = True


@component
class Score:
    value: int = 0


# Centralized State Management

initial_state = {
    "player": {
        "position": {"x": 400, "y": 300},
        "velocity": {"x": 0, "y": 0},
        "score": 0,
    },
    "sticks": [{"position": {"x": 100, "y": 100}, "collectible": True}],
}


def root_reducer(state, action):
    if action["type"] == "SET_PLAYER_POSITION":
        state["player"]["position"] = action["payload"]
    elif action["type"] == "SET_PLAYER_VELOCITY":
        state["player"]["velocity"] = action["payload"]
    elif action["type"] == "COLLECT_STICK":
        stick_index = action["payload"]
        state["sticks"][stick_index]["collectible"] = False
        state["player"]["score"] += 1
    elif action["type"] == "SET_STICK_POSITION":
        index = action["payload"]["index"]
        state["sticks"][index]["position"] = action["payload"]["position"]
        state["sticks"][index]["collectible"] = True
    elif action["type"] == "RESET_STICK":
        index = action["payload"]
        if index < len(state["sticks"]):
            state["sticks"][index]["collectible"] = True
    elif action["type"] == "RESET_GAME":
        state.clear()
        state.update(
            {
                "player": {
                    "position": {"x": 400, "y": 300},
                    "velocity": {"x": 0, "y": 0},
                    "score": 0,
                },
                "sticks": [{"position": {"x": 100, "y": 100}, "collectible": True}],
            }
        )
    elif action["type"] == "MOVE_PLAYER":
        dt = action["delta_time"]
        pos = state["player"]["position"]
        vel = state["player"].get("velocity", {"x": 0, "y": 0})
        new_x = pos["x"] + vel["x"] * dt
        new_y = pos["y"] + vel["y"] * dt
        new_x = max(0, min(new_x, 800))
        new_y = max(0, min(new_y, 600))
        state["player"]["position"] = {"x": new_x, "y": new_y}
    elif action["type"] == "COLLECT_STICKS":
        player_pos = state["player"]["position"]
        for i, stick in enumerate(state["sticks"]):
            if stick.get("collectible", False):
                dx = stick["position"]["x"] - player_pos["x"]
                dy = stick["position"]["y"] - player_pos["y"]
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= 20:
                    state["sticks"][i]["collectible"] = False
                    state["player"]["score"] += 1
                    break
    elif action["type"] == "ADD_STICK":
        state["sticks"].append(action["payload"])
    elif action["type"] == "REMOVE_PLAYER_PROPERTY":
        prop = action["payload"]
        if prop in state["player"]:
            del state["player"][prop]
    elif action["type"] == "REMOVE_STICK_PROPERTY":
        index = action["payload"]["index"]
        prop = action["payload"]["property"]
        if index < len(state["sticks"]) and prop in state["sticks"][index]:
            del state["sticks"][index][prop]

    return state


store = create_store(root_reducer, initial_state)
store.getState = store.get_state


# Processors
class MovementProcessor:
    def process(self, delta_time):
        for _, (vel, pos, _) in esper.get_components(
            Velocity, Position, PlayerControlled
        ):
            pos.x += vel.x * delta_time
            pos.y += vel.y * delta_time
            pos.x = max(0, min(pos.x, 800))
            pos.y = max(0, min(pos.y, 600))
            store.dispatch(Actions.setPlayerPosition({"x": pos.x, "y": pos.y}))


class CollectionProcessor:
    def process(self):
        state = store.get_state()
        player_pos = state["player"]["position"]

        for entity, (pos, col) in esper.get_components(Position, Collectible):
            if (
                col.active
                and self._distance(player_pos, {"x": pos.x, "y": pos.y}) <= 20
            ):
                col.active = False
                stick_index = 0  # Assume single stick for simplicity
                store.dispatch(Actions.collectStick(stick_index))
                self._respawn_stick(stick_index, pos, col)
                updated_state = store.get_state()
                if updated_state["player"]["score"] >= 2:
                    print("You Win!")
                break

    def _distance(self, pos1, pos2):
        return ((pos1["x"] - pos2["x"]) ** 2 + (pos1["y"] - pos2["y"]) ** 2) ** 0.5

    def _respawn_stick(self, stick_index, pos, col):
        new_position = {"x": random.randint(50, 750), "y": random.randint(50, 550)}
        store.dispatch(Actions.setStickPosition(stick_index, new_position))
        pos.x = new_position["x"]
        pos.y = new_position["y"]
        col.active = True
        print(f"Respawned stick {stick_index} at ({pos.x}, {pos.y})")


class InputProcessor:
    def process(self):
        for _, (vel, player) in esper.get_components(Velocity, PlayerControlled):
            vel.x = 0
            vel.y = 0
            if pr.is_key_down(pr.KEY_W):
                vel.y = -player.speed
            if pr.is_key_down(pr.KEY_S):
                vel.y = player.speed
            if pr.is_key_down(pr.KEY_A):
                vel.x = -player.speed
            if pr.is_key_down(pr.KEY_D):
                vel.x = player.speed
            store.dispatch(Actions.setPlayerVelocity({"x": vel.x, "y": vel.y}))


# Main Game Loop
def main():
    pr.init_window(800, 600, "Pickin' Sticks")
    pr.set_target_fps(60)

    esper.clear_cache()

    movement_processor = MovementProcessor()
    collection_processor = CollectionProcessor()
    input_processor = InputProcessor()

    player = esper.create_entity()
    esper.add_component(player, Position(x=400, y=300))
    esper.add_component(player, Velocity(x=0, y=0))
    esper.add_component(player, PlayerControlled())
    esper.add_component(player, Score())

    stick = esper.create_entity()
    esper.add_component(stick, Position(x=100, y=100))
    esper.add_component(stick, Collectible())

    while not pr.window_should_close():
        delta_time = pr.get_frame_time()

        input_processor.process()
        movement_processor.process(delta_time)
        collection_processor.process()

        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        for _, (pos, _) in esper.get_components(Position, PlayerControlled):
            pr.draw_circle(int(pos.x), int(pos.y), 20, pr.BLUE)

        for _, (pos, col) in esper.get_components(Position, Collectible):
            if col.active:
                pr.draw_circle(int(pos.x), int(pos.y), 10, pr.RED)

        state = store.get_state()
        pr.draw_text(f"Score: {state['player']['score']}", 10, 10, 20, pr.BLACK)

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()
