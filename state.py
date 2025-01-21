import copy
import random
from constants import (
    COLLECTION_RADIUS,
    PLAYER_START_X,
    PLAYER_START_Y,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    STICK_SPAWN_MARGIN,
)
from actions import Actions
from redux_toolkit import create_store

initial_state = {
    "player": {
        "position": {"x": PLAYER_START_X, "y": PLAYER_START_Y},
        "velocity": {"x": 0, "y": 0},
        "score": 0,
    },
    "sticks": [{"position": {"x": 100, "y": 100}, "collectible": True}],
}


def constrain_position(x, y, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
    """Constrain position within window bounds."""
    return {"x": max(0, min(x, width)), "y": max(0, min(y, height))}


def root_reducer(state, action):
    """Handle state changes based on actions."""
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
