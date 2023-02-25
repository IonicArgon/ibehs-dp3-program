# space for imports later
from gpiozero import Buzzer
from lib.gestures import Head_Position
import time
import threading

class Buzzer_Wrapper():
    def __init__(self, p_buzzer_pin):
        self.m_buzzer = Buzzer(p_buzzer_pin)
        
        # constants
        self.m_c_BUZZER_PATTERNS = {
            ".": 0.1,
            "-": 0.3,
            " ": 0.1
        }
        self.m_c_BUZZER_DELAY = 0.1
        self.m_buzzer.off()

    def __del__(self):
        self.m_buzzer.off()

    def play_pattern(self, p_pattern):
        for char in p_pattern:
            if char in ".-":
                self.m_buzzer.on()
                time.sleep(self.m_c_BUZZER_PATTERNS[char])
                self.m_buzzer.off()
                time.sleep(self.m_c_BUZZER_DELAY)
            elif char == " ":
                time.sleep(self.m_c_BUZZER_PATTERNS[char])
            else:
                raise Exception(f'[Buzzer_Wrapper] Invalid pattern: {p_pattern}]')

class Vibration():
    def __init__(self, p_buzzer_pin, p_loop_delay):
        self.m_buzzer = Buzzer_Wrapper(p_buzzer_pin)
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_loop_delay = p_loop_delay
        
        self.thread_user_alert = threading.Thread(target=self.user_alert)
        self.thread_user_alert.daemon = True
        self.thread_user_alert.start()

    def __del__(self):
        pass

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

    def get_status(self):
        if self.m_head_position == Head_Position.MOVE_FORWARD:
            return "FORWARD"
        elif self.m_head_position == Head_Position.MOVE_BACKWARD:
            return "BACKWARD"
        elif self.m_head_position == Head_Position.MOVE_RIGHT:
            return "RIGHT"
        elif self.m_head_position == Head_Position.MOVE_LEFT:
            return "LEFT"
        elif self.m_head_position == Head_Position.MOVE_STOP:
            return "STOP"

    def user_alert(self):
        while True:
            if self.m_head_position == Head_Position.MOVE_FORWARD:
                self.m_buzzer.play_pattern("-")
            elif self.m_head_position == Head_Position.MOVE_BACKWARD:
                self.m_buzzer.play_pattern("--")
            elif self.m_head_position == Head_Position.MOVE_RIGHT:
                self.m_buzzer.play_pattern(".")
            elif self.m_head_position == Head_Position.MOVE_LEFT:
                self.m_buzzer.play_pattern("..")
            elif self.m_head_position == Head_Position.MOVE_STOP:
                self.m_buzzer.play_pattern("...")

            time.sleep(self.m_loop_delay)
