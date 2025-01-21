class Actions:
    @staticmethod
    def resetGame():
        """
        Resets the game state to its initial values.
        """
        return {"type": "RESET_GAME"}

    @staticmethod
    def setPlayerPosition(payload):
        """
        Updates the player's position.
        payload: dict containing x and y positions, e.g., {"x": 400, "y": 300}
        """
        return {"type": "SET_PLAYER_POSITION", "payload": payload}

    @staticmethod
    def setPlayerVelocity(payload):
        """
        Updates the player's velocity.
        payload: dict containing x and y velocity, e.g., {"x": 0.0, "y": 0.0}
        """
        return {"type": "SET_PLAYER_VELOCITY", "payload": payload}

    @staticmethod
    def movePlayer(delta_time):
        """
        Moves the player based on their velocity and delta_time.
        delta_time: float representing the time since the last frame.
        """
        return {"type": "MOVE_PLAYER", "delta_time": delta_time}

    @staticmethod
    def collectStick(stick_index):
        """
        Collects a stick by marking it inactive and incrementing the score.
        stick_index: int representing the index of the stick to collect.
        """
        return {"type": "COLLECT_STICK", "payload": stick_index}

    @staticmethod
    def collectSticks():
        """
        Handles collection logic for all collectible sticks near the player.
        """
        return {"type": "COLLECT_STICKS"}

    @staticmethod
    def resetStick(index):
        """
        Re-enables a stick without changing its position.
        index: int representing the index of the stick to reset.
        """
        return {"type": "RESET_STICK", "payload": index}

    @staticmethod
    def setStickPosition(index, position):
        """
        Updates the position of a specific stick and marks it as collectible.
        index: int representing the stick's index.
        position: dict containing x and y coordinates, e.g., {"x": 200, "y": 150}.
        """
        return {
            "type": "SET_STICK_POSITION",
            "payload": {"index": index, "position": position},
        }

    @staticmethod
    def addStick(stick):
        """
        Adds a new stick to the state.
        stick: dict containing stick data, e.g., {"position": {"x": 100, "y": 100}, "collectible": True}.
        """
        return {"type": "ADD_STICK", "payload": stick}

    @staticmethod
    def removePlayerProperty(prop):
        """
        Removes a property from the player.
        prop: str representing the property to remove, e.g., "velocity".
        """
        return {"type": "REMOVE_PLAYER_PROPERTY", "payload": prop}

    @staticmethod
    def removeStickProperty(index, prop):
        """
        Removes a property from a specific stick.
        index: int representing the stick's index.
        prop: str representing the property to remove from the stick.
        """
        return {
            "type": "REMOVE_STICK_PROPERTY",
            "payload": {"index": index, "property": prop},
        }
