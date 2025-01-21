# main.py
import copy
import random
from dataclasses import dataclass
import esper
import pyray as pr
from redux_toolkit import create_store
from actions import Actions

# Game Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_SIZE = 20
STICK_SIZE = 10
COLLECTION_RADIUS = 20
PLAYER_START_X = WINDOW_WIDTH // 2
PLAYER_START_Y = WINDOW_HEIGHT // 2
STICK_SPAWN_MARGIN = 50


# Components
@dataclass
class Position:
    x: int = PLAYER_START_X
    y: int = PLAYER_START_Y


@dataclass
class Velocity:
    x: float = 0.0
    y: float = 0.0


@dataclass
class PlayerControlled:
    speed: float = 200.0


@dataclass
class Collectible:
    active: bool = True


@dataclass
class Score:
    value: int = 0


# State Management
initial_state = {
    "player": {
        "position": {"x": PLAYER_START_X, "y": PLAYER_START_Y},
        "velocity": {"x": 0, "y": 0},
        "score": 0,
    },
    "sticks": [{"position": {"x": 100, "y": 100}, "collectible": True}],
}


def constrain_position(x, y, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
    """Constrain position within window bounds"""
    return {"x": max(0, min(x, width)), "y": max(0, min(y, height))}


def root_reducer(state, action):
    match action["type"]:
        case "GENERATE_POSITION":
            return {
                "x": random.randint(
                    STICK_SPAWN_MARGIN, WINDOW_WIDTH - STICK_SPAWN_MARGIN
                ),
                "y": random.randint(
                    STICK_SPAWN_MARGIN, WINDOW_HEIGHT - STICK_SPAWN_MARGIN
                ),
            }
        case "SET_PLAYER_POSITION":
            state["player"]["position"] = action["payload"]
        case "SET_PLAYER_VELOCITY":
            state["player"]["velocity"] = action["payload"]
        case "COLLECT_STICK":
            stick_index = action["payload"]
            if stick_index < len(state["sticks"]):
                state["sticks"][stick_index]["collectible"] = False
                state["player"]["score"] += 1
                store.dispatch(Actions.respawnStick(stick_index))
        case "RESPAWN_STICK":
            stick_index = action["payload"]
            if stick_index < len(state["sticks"]):
                new_position = root_reducer(state, Actions.generatePosition())
                state["sticks"][stick_index].update(
                    {"position": new_position, "collectible": True}
                )
        case "SET_STICK_POSITION":
            index = action["payload"]["index"]
            if index < len(state["sticks"]):
                state["sticks"][index].update(
                    {"position": action["payload"]["position"], "collectible": True}
                )
        case "RESET_STICK":
            index = action["payload"]
            if index < len(state["sticks"]):
                state["sticks"][index]["collectible"] = True
        case "RESET_GAME":
            state.clear()
            state.update(copy.deepcopy(initial_state))
        case "MOVE_PLAYER":
            player = state["player"]
            dt = action["delta_time"]
            vel = player.get("velocity", {"x": 0, "y": 0})
            pos = constrain_position(
                player["position"]["x"] + vel["x"] * dt,
                player["position"]["y"] + vel["y"] * dt,
            )
            player["position"] = pos
        case "COLLECT_STICKS":
            player_pos = state["player"]["position"]
            for i, stick in enumerate(state["sticks"]):
                if stick.get("collectible", False):
                    dx = stick["position"]["x"] - player_pos["x"]
                    dy = stick["position"]["y"] - player_pos["y"]
                    if (dx * dx + dy * dy) ** 0.5 <= COLLECTION_RADIUS:
                        store.dispatch(Actions.collectStick(i))
                        break
        case "ADD_STICK":
            state["sticks"].append(action["payload"])
        case "REMOVE_PLAYER_PROPERTY" | "REMOVE_STICK_PROPERTY":
            target = (
                state["player"]
                if action["type"].startswith("REMOVE_PLAYER")
                else state["sticks"][action["payload"]["index"]]
            )
            prop = (
                action["payload"]
                if action["type"].startswith("REMOVE_PLAYER")
                else action["payload"]["property"]
            )
            if prop in target:
                del target[prop]

    return state


store = create_store(root_reducer, initial_state)


def sync_ecs_with_store():
    state = store.get_state()

    # Sync player position
    for _, (pos, _) in esper.get_components(Position, PlayerControlled):
        player_pos = state["player"]["position"]
        pos.x, pos.y = player_pos["x"], player_pos["y"]

    # Sync stick positions and states
    for i, (_, (pos, col)) in enumerate(esper.get_components(Position, Collectible)):
        if i < len(state["sticks"]):
            stick = state["sticks"][i]
            pos.x = stick["position"]["x"]
            pos.y = stick["position"]["y"]
            col.active = stick["collectible"]


store.subscribe(sync_ecs_with_store)


class MovementProcessor:
    def process(self, delta_time):
        for _, (vel, _, _) in esper.get_components(
            Velocity, Position, PlayerControlled
        ):
            store.dispatch(Actions.movePlayer(delta_time))


class CollectionProcessor:
    def process(self):
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        if state["player"]["score"] >= 2:
            print("You Win!")


class InputProcessor:
    def process(self, delta_time=None):  # Add delta_time parameter with default None
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


def main():
    pr.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Pickin' Sticks")
    pr.set_target_fps(60)

    esper.clear_cache()
    processors = [InputProcessor(), MovementProcessor(), CollectionProcessor()]

    # Create player entity
    player = esper.create_entity()
    esper.add_component(player, Position())
    esper.add_component(player, Velocity())
    esper.add_component(player, PlayerControlled())
    esper.add_component(player, Score())

    # Create stick entity
    stick = esper.create_entity()
    esper.add_component(stick, Position(x=100, y=100))
    esper.add_component(stick, Collectible())

    while not pr.window_should_close():
        delta_time = pr.get_frame_time()

        # Update
        for processor in processors[:2]:  # Input and Movement
            processor.process(delta_time)
        processors[2].process()  # Collection

        # Draw
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        # Draw player
        for _, (pos, _) in esper.get_components(Position, PlayerControlled):
            pr.draw_circle(int(pos.x), int(pos.y), PLAYER_SIZE, pr.BLUE)

        # Draw sticks
        for _, (pos, col) in esper.get_components(Position, Collectible):
            if col.active:
                pr.draw_circle(int(pos.x), int(pos.y), STICK_SIZE, pr.RED)

        # Draw score
        pr.draw_text(
            f"Score: {store.get_state()['player']['score']}", 10, 10, 20, pr.BLACK
        )

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()
