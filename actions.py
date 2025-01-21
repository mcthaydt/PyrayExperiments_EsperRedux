# actions.py
class Actions:
    @staticmethod
    def generatePosition():
        """Generate a random position within game bounds"""
        return {"type": "GENERATE_POSITION"}

    @staticmethod
    def resetGame():
        """Reset the game state to initial values"""
        return {"type": "RESET_GAME"}

    @staticmethod
    def setPlayerPosition(payload):
        """Update player position
        payload: dict with x, y coordinates"""
        return {"type": "SET_PLAYER_POSITION", "payload": payload}

    @staticmethod
    def setPlayerVelocity(payload):
        """Update player velocity
        payload: dict with x, y velocities"""
        return {"type": "SET_PLAYER_VELOCITY", "payload": payload}

    @staticmethod
    def movePlayer(delta_time):
        """Move player based on current velocity
        delta_time: time since last frame"""
        return {"type": "MOVE_PLAYER", "delta_time": delta_time}

    @staticmethod
    def collectStick(stick_index):
        """Collect a specific stick and update score
        stick_index: index of stick to collect"""
        return {"type": "COLLECT_STICK", "payload": stick_index}

    @staticmethod
    def collectSticks():
        """Check and collect any sticks within range"""
        return {"type": "COLLECT_STICKS"}

    @staticmethod
    def resetStick(index):
        """Reset a stick's collectible state
        index: index of stick to reset"""
        return {"type": "RESET_STICK", "payload": index}

    @staticmethod
    def respawnStick(index):
        """Respawn a stick at a random position
        index: index of stick to respawn"""
        return {"type": "RESPAWN_STICK", "payload": index}

    @staticmethod
    def setStickPosition(index, position):
        """Set position of a specific stick
        index: stick index
        position: dict with x, y coordinates"""
        return {
            "type": "SET_STICK_POSITION",
            "payload": {"index": index, "position": position},
        }

    @staticmethod
    def addStick(stick):
        """Add a new stick to the game
        stick: dict with stick properties"""
        return {"type": "ADD_STICK", "payload": stick}

    @staticmethod
    def removePlayerProperty(prop):
        """Remove a property from player state
        prop: name of property to remove"""
        return {"type": "REMOVE_PLAYER_PROPERTY", "payload": prop}

    @staticmethod
    def removeStickProperty(index, prop):
        """Remove a property from a stick
        index: stick index
        prop: name of property to remove"""
        return {
            "type": "REMOVE_STICK_PROPERTY",
            "payload": {"index": index, "property": prop},
        }
