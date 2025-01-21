# tests.py
import unittest
from actions import Actions  # Import the Actions class
from main import store


class PickinSticksReduxTests(unittest.TestCase):
    def setUp(self):
        # Reset the state before each test.
        store.dispatch(Actions.resetGame())
        # For these tests, we assume that resetGame creates the player and a single stick.

    def test_player_initial_position(self):
        """Test player starts at correct position"""
        state = store.get_state()
        player = state["player"]
        self.assertEqual(player["position"]["x"], 400)  # Ensure this matches game logic
        self.assertEqual(player["position"]["y"], 300)

    def test_player_movement_bounds(self):
        """Test all screen boundary conditions"""
        # Upper bound: Set player at y=0 with upward velocity.
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 0}))
        store.dispatch(Actions.setPlayerVelocity({"x": 0, "y": -100}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["y"], 0)

        # Lower bound: y should not exceed 600.
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 600}))
        store.dispatch(Actions.setPlayerVelocity({"x": 0, "y": 100}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["y"], 600)

        # Left bound: x should not go below 0.
        store.dispatch(Actions.setPlayerPosition({"x": 0, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": -100, "y": 0}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 0)

        # Right bound: x should not exceed 800.
        store.dispatch(Actions.setPlayerPosition({"x": 800, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": 100, "y": 0}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 800)

    def test_diagonal_movement(self):
        """Test diagonal movement calculations"""
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": 100, "y": 100}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        pos = state["player"]["position"]
        self.assertEqual(pos["x"], 500)
        self.assertEqual(pos["y"], 400)

    def test_zero_velocity(self):
        """Test player with zero velocity stays still"""
        # Grab the initial position.
        state = store.get_state()
        init_x = state["player"]["position"]["x"]
        init_y = state["player"]["position"]["y"]
        store.dispatch(Actions.setPlayerVelocity({"x": 0, "y": 0}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        pos = state["player"]["position"]
        self.assertEqual(pos["x"], init_x)
        self.assertEqual(pos["y"], init_y)

    def test_stick_collection_edge_distance(self):
        """Test stick collection at exact threshold distances by checking score and respawn"""
        state = store.get_state()
        original_stick = state["sticks"][0]
        original_position = original_stick["position"].copy()
        original_score = state["player"]["score"]

        # At threshold (distance = COLLECTION_RADIUS, which is 20)
        store.dispatch(
            Actions.setPlayerPosition(
                {"x": original_position["x"] + 20, "y": original_position["y"]}
            )
        )
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        # The stick should have been collected, so the score increases...
        self.assertEqual(state["player"]["score"], original_score + 1)
        # ...and the stick should have respawned (i.e. have a new position)
        self.assertNotEqual(state["sticks"][0]["position"], original_position)

        # Slightly inside threshold (distance < 20)
        store.dispatch(Actions.resetStick(0))
        state = store.get_state()
        stick_pos = state["sticks"][0]["position"].copy()
        original_score = state["player"]["score"]
        store.dispatch(
            Actions.setPlayerPosition({"x": stick_pos["x"] + 19, "y": stick_pos["y"]})
        )
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        self.assertEqual(state["player"]["score"], original_score + 1)
        self.assertNotEqual(state["sticks"][0]["position"], stick_pos)

        # Slightly outside threshold (distance > 20)
        store.dispatch(Actions.resetStick(0))
        state = store.get_state()
        stick_pos = state["sticks"][0]["position"].copy()
        original_score = state["player"]["score"]
        store.dispatch(
            Actions.setPlayerPosition({"x": stick_pos["x"] + 21, "y": stick_pos["y"]})
        )
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        # No collection should occur so the score remains the same
        self.assertEqual(state["player"]["score"], original_score)
        # And the stick’s position is unchanged
        self.assertEqual(state["sticks"][0]["position"], stick_pos)

    def test_stick_respawn_bounds(self):
        """Test stick respawns within valid game bounds"""
        for _ in range(50):
            state = store.get_state()
            stick = state["sticks"][0]
            store.dispatch(
                Actions.setPlayerPosition(
                    {"x": stick["position"]["x"], "y": stick["position"]["y"]}
                )
            )
            store.dispatch(Actions.collectSticks())
            state = store.get_state()
            new_pos = state["sticks"][0]["position"]
            self.assertTrue(50 <= new_pos["x"] <= 750)
            self.assertTrue(50 <= new_pos["y"] <= 550)
            store.dispatch(Actions.resetStick(0))

    def test_rapid_collection(self):
        """Test rapid consecutive stick collections"""
        state = store.get_state()
        stick = state["sticks"][0]

        for _ in range(5):
            store.dispatch(
                Actions.setPlayerPosition(
                    {"x": stick["position"]["x"], "y": stick["position"]["y"]}
                )
            )
            store.dispatch(Actions.collectSticks())
            store.dispatch(Actions.resetStick(0))
            state = store.get_state()
            new_pos = state["sticks"][0]["position"]
            self.assertTrue(
                50 <= new_pos["x"] <= 750 and 50 <= new_pos["y"] <= 550,
                "Stick did not respawn within valid bounds.",
            )

    def test_score_update(self):
        """Test score increments correctly on stick collection"""
        state = store.get_state()
        initial_score = state["player"]["score"]
        stick = state["sticks"][0]
        store.dispatch(
            Actions.setPlayerPosition(
                {"x": stick["position"]["x"], "y": stick["position"]["y"]}
            )
        )
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        new_score = state["player"]["score"]
        self.assertEqual(new_score, initial_score + 1)

    def test_multiple_stick_collision(self):
        """Test collision detection with multiple sticks"""
        store.dispatch(
            Actions.addStick({"position": {"x": 200, "y": 200}, "collectible": True})
        )
        store.dispatch(
            Actions.addStick({"position": {"x": 300, "y": 300}, "collectible": True})
        )

        collected_count = 0

        state = store.get_state()
        for i, stick in enumerate(state["sticks"]):
            if stick.get("collectible", False):
                store.dispatch(
                    Actions.setPlayerPosition(
                        {"x": stick["position"]["x"], "y": stick["position"]["y"]}
                    )
                )
                store.dispatch(Actions.collectSticks())
                collected_count += 1
                store.dispatch(Actions.resetStick(i))

        state = store.get_state()
        final_score = state["player"]["score"]
        self.assertEqual(final_score, collected_count)

    def test_delta_time_scaling(self):
        """Test movement scaling with different delta times"""
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": 100, "y": 0}))

        store.dispatch(Actions.movePlayer(0.5))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 400 + 100 * 0.5)

        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 300}))
        store.dispatch(Actions.movePlayer(0.25))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 400 + 100 * 0.25)

        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 300}))
        store.dispatch(Actions.movePlayer(2.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 400 + 100 * 2.0)

    def test_component_removal(self):
        """Test behavior when components (state slices) are removed"""
        store.dispatch(Actions.removePlayerProperty("velocity"))
        try:
            store.dispatch(Actions.movePlayer(1.0))
        except Exception as e:
            self.fail(f"movePlayer failed after removing velocity: {e}")

        store.dispatch(Actions.removeStickProperty(0, "collectible"))
        try:
            store.dispatch(Actions.collectSticks())
        except Exception as e:
            self.fail(
                f"collectSticks failed after removing stick collectible property: {e}"
            )


if __name__ == "__main__":
    unittest.main()
