# space for imports
from enum import IntEnum
import threading
import time
import json

class Head_Position(IntEnum):
    MOVE_FORWARD    = 0
    MOVE_BACKWARD   = 1
    MOVE_LEFT       = 2
    MOVE_RIGHT      = 3 
    MOVE_STOP       = 4

class Gestures():
    def __init__(self, p_config_file, p_gesture_window_time):
        # configerations
        self.m_gestures = {}
        self.m_gesture_window_len = p_gesture_window_time

        with open(p_config_file, "r") as f:
            gestures = (json.load(f))["gestures"]
            for i in gestures:
                gestureEnum = Head_Position(gestures[i]["__enum__"])
                self.m_gestures[gestureEnum] = gestures[i]
                del self.m_gestures[gestureEnum]["__enum__"]

        # internal values
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_internal_orientation = None

        # for threading
        self.m_update_internal_thread = threading.Thread(target=self.update_internal_values)
        self.m_update_internal_thread.daemon = True
        self.m_update_internal_thread_running = False
        self.m_update_internal_thread.start()

        self.m_update_gesture_thread = threading.Thread(target=self.update_gesture_output)
        self.m_update_gesture_thread.daemon = True
        self.m_update_gesture_thread_running = True
        self.m_update_gesture_thread.start()

    def __del__(self):
        self.m_update_internal_thread_running = False
        self.m_update_gesture_thread_running = False

    def get(self):
        return self.m_head_position

    def update_internal_values(self):
        while True:
            if self.m_update_internal_thread_running == False:
                self.m_internal_orientation = None
                pass
            else:
                raise NotImplementedError("update_internal_values() not implemented")
            time.sleep(0.1)

    def update_gesture_output(self):
        while self.m_update_gesture_thread_running:
            # update internal values
            self.m_update_internal_thread_running = True
            time.sleep(self.m_gesture_window_len)
            self.m_update_internal_thread_running = False

            # set the default position
            self.m_head_position = Head_Position.MOVE_STOP

            for i in self.m_gestures:
                if self.m_internal_orientation == None:
                    break

                gesture = self.m_gestures[i]
                direction_test = (gesture["direction"] == self.m_internal_orientation["direction"])
                count_test = (gesture["count"] == self.m_internal_orientation["count"])

                if direction_test and count_test:
                    self.m_head_position = Head_Position(i)
                    break
            time.sleep(0.1)

if __name__ == "__main__":
    gestures = Gestures('config.json', 5.0)
    time.sleep(10)
