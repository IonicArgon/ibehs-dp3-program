# space for imports
from enum import IntEnum
import threading
import time
import json
import math

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
        self.m_internal_orientation = {}
        self.m_internal_xyz = [0, 0, 0]
        self.m_largest_direction_xyz = [0, 0, 0]
        self.m_prev_vector = 0
        self.m_count = 0

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

    def set_xyz(self, p_xyz):
        self.m_internal_xyz = p_xyz

    def update_internal_values(self):
        while True:
            if self.m_update_internal_thread_running == False:
                self.m_largest_direction_xyz = [0, 0, 0]
                self.m_prev_vector = 0
                self.m_count = 0
                print("[GEST] Internal values reset")
            else:
                for i in range(1, 3):
                    vector = self.m_internal_xyz[i]
                    vector = vector if vector is not None else 0

                    if abs(vector) > abs(self.m_prev_vector):
                        self.m_largest_direction_xyz = [0, 0, 0]
                        self.m_largest_direction_xyz[i] = 1
                        self.m_prev_vector = vector
                        print(f'[GEST] Largest direction: {self.m_largest_direction_xyz}')

                for i in self.m_gestures:
                    gesture = self.m_gestures[i]
                    direction_test = (gesture["direction"] == self.m_largest_direction_xyz)

                    vector = self.m_internal_xyz[gesture["direction"].index(1)]
                    vector = vector if vector is not None else 0
                    threshold_test = (abs(vector) > abs(gesture["threshold"]))
                    
                    if direction_test and threshold_test:
                        # only increment on rising edge case of threshold test
                        if self.m_prev_vector < gesture["threshold"]:
                            self.m_count += 1
                            print(f'[GEST] New increment for {gesture["direction"]}: {self.m_count}')
                        break

                self.m_internal_orientation = {
                    "direction": self.m_largest_direction_xyz,
                    "count": self.m_count
                }

                print(f'[GEST] Internal orientation: {self.m_internal_orientation}')
            time.sleep(0.1)

    def update_gesture_output(self):
        while self.m_update_gesture_thread_running:
            # update internal values
            print("[GEST] Updating internal values")
            self.m_update_internal_thread_running = True
            time.sleep(self.m_gesture_window_len)
            self.m_update_internal_thread_running = False
            print(f'[GEST] Internal values: {self.m_internal_orientation}')

            # set the default position
            self.m_head_position = Head_Position.MOVE_STOP

            for i in self.m_gestures:
                if self.m_internal_orientation == None:
                    print("[GEST] No internal orientation found")
                    break

                gesture = self.m_gestures[i]
                direction_test = (gesture["direction"] == self.m_internal_orientation["direction"])
                count_test = (gesture["count"] == self.m_internal_orientation["count"])

                if direction_test and count_test:
                    self.m_head_position = Head_Position(i)
                    print(f'[GEST] New head position: {self.m_head_position}')
                    break
            time.sleep(0.1)