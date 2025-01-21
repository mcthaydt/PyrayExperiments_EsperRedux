class Actions:
    @staticmethod
    def generatePosition():
        return {"type": "GENERATE_POSITION"}

    @staticmethod
    def resetGame():
        return {"type": "RESET_GAME"}

    @staticmethod
    def setPlayerPosition(payload):
        return {"type": "SET_PLAYER_POSITION", "payload": payload}

    @staticmethod
    def setPlayerVelocity(payload):
        return {"type": "SET_PLAYER_VELOCITY", "payload": payload}

    @staticmethod
    def movePlayer(delta_time):
        return {"type": "MOVE_PLAYER", "delta_time": delta_time}

    @staticmethod
    def collectStick(stick_index):
        return {"type": "COLLECT_STICK", "payload": stick_index}

    @staticmethod
    def collectSticks():
        return {"type": "COLLECT_STICKS"}

    @staticmethod
    def resetStick(index):
        return {"type": "RESET_STICK", "payload": index}

    @staticmethod
    def respawnStick(index):
        return {"type": "RESPAWN_STICK", "payload": index}

    @staticmethod
    def setStickPosition(index, position):
        return {
            "type": "SET_STICK_POSITION",
            "payload": {"index": index, "position": position},
        }

    @staticmethod
    def addStick(stick):
        return {"type": "ADD_STICK", "payload": stick}

    @staticmethod
    def removePlayerProperty(prop):
        return {"type": "REMOVE_PLAYER_PROPERTY", "payload": prop}

    @staticmethod
    def removeStickProperty(index, prop):
        return {
            "type": "REMOVE_STICK_PROPERTY",
            "payload": {"index": index, "property": prop},
        }
