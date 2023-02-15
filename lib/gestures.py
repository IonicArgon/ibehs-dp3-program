# space for imports
from enum import Enum
import threading
import time

class Head_Position(Enum):
    MOVE_FORWARD = 1
    MOVE_BACKWARD = 2
    MOVE_RIGHT = 3
    MOVE_LEFT = 4
    MOVE_STOP = 5

class Gestures():
    def __init__(self):
        raise NotImplementedError
        ##TODO: figure out what variables we need
        ##TODO: and what functions we need

    def __del__(self):
        raise NotImplementedError

    def set(self, p_head_position):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError