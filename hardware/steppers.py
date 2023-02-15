# space for imports
from lib.gestures import Head_Position
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time
import threading
import board

class Steppers():
    def __init__(self):
        self.m_kit = MotorKit(i2c=board.I2C())
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_x = 0
        self.m_y = 0

        self.thread_steppers = threading.Thread(target=self.update)
        self.thread_steppers.daemon = True
        self.thread_steppers.start()

    def __del__(self):
        self.m_kit.stepper1.release()
        self.m_kit.stepper2.release()

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

    def update(self):
        raise NotImplementedError

    
