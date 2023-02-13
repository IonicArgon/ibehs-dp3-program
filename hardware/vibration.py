# space for imports later
from gpiozero import Buzzer
from enum import Enum
import time
import threading

class Head_Position(Enum):
    MOVE_FORWARD = 1
    MOVE_BACKWARD = 2
    MOVE_RIGHT = 3
    MOVE_LEFT = 4
    MOVE_STOP = 5

class Vibration():
    def __init__(self, p_buzzer_pin):
        self.m_buzzer = Buzzer(p_buzzer_pin)
        self.m_head_position = Head_Position.MOVE_STOP
        
        thread_user_alert = threading.Thread(target=self.user_alert)
        thread_user_alert.start()

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

    def user_alert(self):
        while True:
            if self.m_head_position == Head_Position.MOVE_FORWARD:
                self.m_buzzer.off()
            elif self.m_head_position == Head_Position.MOVE_BACKWARD:
                self.m_buzzer.off()
            elif self.m_head_position == Head_Position.MOVE_RIGHT:
                self.m_buzzer.off()
            elif self.m_head_position == Head_Position.MOVE_LEFT:
                self.m_buzzer.off()
            elif self.m_head_position == Head_Position.MOVE_STOP:
                self.m_buzzer.on()

            time.sleep(0.01)
    