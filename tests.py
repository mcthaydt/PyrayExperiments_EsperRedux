import unittest
from actions import Actions
from state import store  # Import store from state.py instead of main.py


class PickinSticksReduxTests(unittest.TestCase):
    def setUp(self):
        store.dispatch(Actions.resetGame())

    def test_player_initial_position(self):
        state = store.get_state()
        player = state["player"]
        self.assertEqual(player["position"]["x"], 400)
        self.assertEqual(player["position"]["y"], 300)

    def test_player_movement_bounds(self):
        # Upper bound
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 0}))
        store.dispatch(Actions.setPlayerVelocity({"x": 0, "y": -100}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["y"], 0)

        # Lower bound
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 600}))
        store.dispatch(Actions.setPlayerVelocity({"x": 0, "y": 100}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["y"], 600)

        # Left bound
        store.dispatch(Actions.setPlayerPosition({"x": 0, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": -100, "y": 0}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 0)

        # Right bound
        store.dispatch(Actions.setPlayerPosition({"x": 800, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": 100, "y": 0}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        self.assertEqual(state["player"]["position"]["x"], 800)

    def test_diagonal_movement(self):
        store.dispatch(Actions.setPlayerPosition({"x": 400, "y": 300}))
        store.dispatch(Actions.setPlayerVelocity({"x": 100, "y": 100}))
        store.dispatch(Actions.movePlayer(1.0))
        state = store.get_state()
        pos = state["player"]["position"]
        self.assertEqual(pos["x"], 500)
        self.assertEqual(pos["y"], 400)

    def test_zero_velocity(self):
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
        state = store.get_state()
        original_stick = state["sticks"][0]
        original_position = original_stick["position"].copy()
        original_score = state["player"]["score"]

        # At threshold
        store.dispatch(
            Actions.setPlayerPosition(
                {"x": original_position["x"] + 20, "y": original_position["y"]}
            )
        )
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        self.assertEqual(state["player"]["score"], original_score + 1)
        self.assertNotEqual(state["sticks"][0]["position"], original_position)

        # Inside threshold
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

        # Outside threshold
        store.dispatch(Actions.resetStick(0))
        state = store.get_state()
        stick_pos = state["sticks"][0]["position"].copy()
        original_score = state["player"]["score"]
        store.dispatch(
            Actions.setPlayerPosition({"x": stick_pos["x"] + 21, "y": stick_pos["y"]})
        )
        store.dispatch(Actions.collectSticks())
        state = store.get_state()
        self.assertEqual(state["player"]["score"], original_score)
        self.assertEqual(state["sticks"][0]["position"], stick_pos)

    def test_stick_respawn_bounds(self):
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
            self.assertTrue(50 <= new_pos["x"] <= 750 and 50 <= new_pos["y"] <= 550)

    def test_score_update(self):
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
