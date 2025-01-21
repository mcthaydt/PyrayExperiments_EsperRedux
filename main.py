import esper
import pyray as pr
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_SIZE, STICK_SIZE
from components import Position, Velocity, PlayerControlled, Collectible, Score
from state import store
from processors import InputProcessor, MovementProcessor, CollectionProcessor
from sync import ECSStoreSynchronizer


def main():
    """Main function to initialize and run the game."""
    pr.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Pyray Experiments - Esper x Redux")
    pr.set_target_fps(60)

    esper.clear_cache()
    processors = [InputProcessor(), MovementProcessor(), CollectionProcessor()]

    # Set up synchronization
    synchronizer = ECSStoreSynchronizer()

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
