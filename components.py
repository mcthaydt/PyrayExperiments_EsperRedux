from dataclasses import dataclass

from constants import PLAYER_START_X, PLAYER_START_Y


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
