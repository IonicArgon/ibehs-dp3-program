# ----------------------------------------------------------------------------- #
# by:           Marco Tan (tanm27, 400433483)
#               Emily Attai (attaie, 400452653)
# last updated: 2023-02-25
# description:  reusable code for exponential moving average

# package imports
import threading
import time
import json
import math
import RPi.GPIO as GPIO # type: ignore[import]
from sensor_library import Orientation_Sensor
from enum import IntEnum
from gpiozero import Buzzer
from collections import deque
import matplotlib.pyplot as plt

# note from the programmers:
# 
# we think that putting all the code in one file defeats the purpose of object
# oriented programming, but since it is a requirement for the project, we have
# decided to put all the code in one file. we have tried to make the code as
# readable as possible, and have added comments to explain what each part does,
# but we think this could've been avoided if we were allowed to use multiple
# files. we hope you understand.
# 
# p.s.1: b/c of the nature of the design, we made extensive use of threading to
#        make the code run concurrently. this is why there are so many classes
#        for organization purposes
#
# p.s.2: you will have to run the code in console; IDLE does not support
#        multithreading and will not work. we have tested the code on a raspberry
#        pi 4 and it works fine. use python version 3.9.x or higher.
#
# required packages:
#   - matplotlib
#   - gpiozero

# ----------------------------------------------------------------------------- #
# by:           Marco Tan (tanm27, 400433483)
#               Emily Attai (attaie, 400452653)
# last updated: 2023-02-25
# description:  reusable code for exponential moving average
class EMA:
    def __init__(self, p_alpha, p_window_size, p_round):
        self.m_alpha = p_alpha
        self.m_out = 0.0
        self.m_last_out = 0.0
        self.m_window = []
        self.m_window_size = p_window_size
        self.m_round = p_round

    # set alpha value (the alpha value is the weight given to the most recent
    # data point. the higher the alpha value, the more weight is given to the
    # most recent data point.)
    def set_alpha(self, p_alpha):
        self.m_alpha = p_alpha

    # set window size (the window size is the number of data points used to
    # calculate the average)
    def set_window_size(self, p_window_size):
        self.m_window_size = p_window_size

    def get(self):
        return self.m_out

    # update the EMA with a new data point
    def update(self, p_in):
        # make sure our number is always a float
        self.m_window.append(float(p_in or 0.0))

        # if we have not reached the window size yet, return None
        if len(self.m_window) < self.m_window_size:
            self.m_out = None
            return
        else:
            self.m_window.pop(0)
        #calculating the average of the window 
        window_avg = round(sum(self.m_window) / self.m_window_size, self.m_round)
        self.m_out = self.m_alpha * window_avg + (1 - self.m_alpha) * self.m_last_out
        self.m_last_out = self.m_out

# ----------------------------------------------------------------------------- #
# by:           Marco Tan (tanm27, 400433483)
#               Emily Attai (attaie, 400452653)
# last updated: 2023-02-25
# description:  reading orientation sensor and outputting smoothed data

# class to read orientation sensor and output smoothed data
class Orientation():
    def __init__(self, p_alpha, p_window_size, p_round):
        self.m_sensor = Orientation_Sensor()
        self.m_ema_xyz = [
            EMA(p_alpha, p_window_size, p_round),
            EMA(p_alpha, p_window_size, p_round),
            EMA(p_alpha, p_window_size, p_round)
        ]
        self.m_raw = [None, None, None]
        self.m_ema_out = [None, None, None]

        # for threading of internal values (because we want concurrent updating)
        self.thread_ema_update = threading.Thread(target=self.update)
        self.thread_ema_update.daemon = True
        self.thread_ema_update.start()

    def __del__(self):
        ...

    def get_ema(self):
        return self.m_ema_out

    def get_raw(self):
        return self.m_raw

    def update(self):
        while True:
            # sometimes the i2c bus gets stuck so we need to try again
            try:
                self.m_raw = self.m_sensor.euler_angles()
            # if we get an OSError, try again
            except OSError as e:
                print(f'[Orientation] OSError {e}, trying again...')
                time.sleep(0.1)
                continue

            # stepping through each axes' EMA and updating it
            for i in range(3):
                self.m_ema_xyz[i].update(self.m_raw[i])
                self.m_ema_out = [self.m_ema_xyz[0].get(), 
                                  self.m_ema_xyz[1].get(), 
                                  self.m_ema_xyz[2].get()]
            time.sleep(0.1)

# ----------------------------------------------------------------------------- #
# by:           Marco Tan (tanm27, 400433483)
#               Emily Attai (attaie, 400452653)
# last updated: 2023-02-25
# description:  code to detect gestures from orientation xyz data

# enum class for gestures make code more readable (vs. using numbers)
class Head_Position(IntEnum):
    MOVE_FORWARD    = 0
    MOVE_BACKWARD   = 1
    MOVE_RIGHT      = 2
    MOVE_LEFT       = 3 
    MOVE_STOP       = 4

# class to detect gestures from orientation xyz data
class Gestures():
    def __init__(self, p_config_file, p_gesture_window_time):
        # configurations
        self.m_gestures = {}
        self.m_gesture_window_len = p_gesture_window_time

        # load gestures from json config file.
        # it loads the json as a dictionary and then we can index it
        # to get the values
        with open(p_config_file, "r") as f:
            gestures = (json.load(f))["gestures"]
            for i in gestures:
                gestureEnum = Head_Position(gestures[i]["__enum__"])
                self.m_gestures[gestureEnum] = gestures[i]
                del self.m_gestures[gestureEnum]["__enum__"]

        # internal values (default/placeholder  values)
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_internal_orientation = {}
        self.m_internal_xyz = [0, 0, 0]
        self.m_largest_direction_xyz = [0, 0, 0]
        self.m_prev_vector = 0
        self.m_count = 0

        # for threading of internal values (because we want concurrent updating)
        self.m_update_internal_thread = threading.Thread(target=self.update_internal_values)
        self.m_update_internal_thread.daemon = True
        self.m_update_internal_thread_running = False
        self.m_update_internal_thread.start()

        # for threading of gesture output
        self.m_update_gesture_thread = threading.Thread(target=self.update_gesture_output)
        self.m_update_gesture_thread.daemon = True
        self.m_update_gesture_thread_running = True
        self.m_update_gesture_thread.start()

    # we pause the threads if the object is about to be cleaned up b/c we don't
    # want to run the threads after the object is deleted
    def __del__(self):
        self.m_update_internal_thread_running = False
        self.m_update_gesture_thread_running = False

    def get(self):
        return self.m_head_position
    
    # must convert to strings for output to console because python 
    # print enums as numbers, not strings
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

    def set_xyz(self, p_xyz):
        self.m_internal_xyz = p_xyz

    def update_internal_values(self):
        while True:
            if self.m_update_internal_thread_running == False:
                # reset internal values when not updating
                self.m_largest_direction_xyz = [0, 0, 0]
                self.m_prev_vector = 0
                self.m_count = 0
            else:
                # find largest direction between Y and Z (X is not used)
                for i in range(1, 3):
                    vector = self.m_internal_xyz[i]
                    vector = vector if vector is not None else 0

                    if abs(vector) > abs(self.m_prev_vector):
                        self.m_largest_direction_xyz = [0, 0, 0]
                        self.m_largest_direction_xyz[i] = math.copysign(1, vector)
                        self.m_prev_vector = vector

                # scan through possible gestures and see if any changes in the head position are detected
                for i in self.m_gestures:
                    gesture = self.m_gestures[i]

                    # check if direction is the same
                    direction_test = (gesture["direction"] == self.m_largest_direction_xyz)

                    # get index of 1 or -1 in gesture
                    vector_index = gesture["direction"].index(1) if 1 in gesture["direction"] \
                                   else gesture["direction"].index(-1)
                    vector = self.m_internal_xyz[vector_index]
                    vector = vector if vector is not None else 0

                    # check if threshold is crossed
                    threshold_test = None
                    if gesture["direction"][vector_index] == 1:
                        threshold_test = (vector > gesture["threshold"])
                    else:
                        threshold_test = (vector < gesture["threshold"])
                    
                    # if both tests pass, then gesture is detected and processed
                    if direction_test and threshold_test:
                        # increment once on new falling edge
                        if self.m_count == 0:
                            self.m_count += 1
                        break

                # output internal values using a dictionary for easier reading
                self.m_internal_orientation = {
                    "direction": self.m_largest_direction_xyz,
                    "count": self.m_count
                }

            time.sleep(0.1)

    def update_gesture_output(self):
        while self.m_update_gesture_thread_running:
            # update internal values every gesture window length
            self.m_update_internal_thread_running = True
            time.sleep(self.m_gesture_window_len)
            self.m_update_internal_thread_running = False

            # set the default position in case no gesture is detected
            self.m_head_position = Head_Position.MOVE_STOP

            # scan through possible gestures that we set to see which one is detected
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

# ----------------------------------------------------------------------------- #
# by:           Marco Tan (tanm27, 400433483)
#               Emily Attai (attaie, 400452653)
# last updated: 2023-02-25
# description:  code for stepper motors and stepper activation

# class to control stepper motors using a ULN2003 stepper motor driver
class Stepper_Driver():
    def __init__(self, p_pins: list, p_step_time, p_reversed = False):
        self.m_pins = p_pins
        self.m_step_time = p_step_time
        self.m_steps = 0
        self.m_sequence = 0
        self.m_reverse = p_reversed

        GPIO.setmode(GPIO.BCM)
        for pin in self.m_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # constants for controlling stepper motor driver
        self.m_c_STEPPER_MAX_STEPS = 1024
        self.m_c_STEPPER_STEP_SEQUENCE = [
            [1, 0, 0, 1],
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1]
        ]

    def __del__(self):
        for pin in self.m_pins:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup(self.m_pins)

    def get_steps(self):
        return self.m_steps
    #p_steps represents a parameter for the amount of steps we want executed
    def step(self, p_steps):
        default_reverse = self.m_reverse

        # check to see if the next command will reverse the motor
        if p_steps < 0:
            self.m_reverse = not self.m_reverse
        elif p_steps >= 0:
            pass
        else:
            raise Exception(f'[Stepper_Driver] Invalid step value: {p_steps}')
            
        # check to see if the next command will exceed the max steps
        if abs(self.m_steps + p_steps) > self.m_c_STEPPER_MAX_STEPS:
            print(f'[Stepper_Driver] Max steps exceeded: {self.m_steps + p_steps} > {self.m_c_STEPPER_MAX_STEPS}')
            self.m_reverse = default_reverse
            return

        # step the motor the specified number of steps in the specified direction
        for _ in range(abs(p_steps)):
            for pin in range(4):
                GPIO.output(self.m_pins[pin], self.m_c_STEPPER_STEP_SEQUENCE[self.m_sequence][pin])
            if self.m_reverse:
                self.m_sequence = (self.m_sequence - 1) % 8
            elif not self.m_reverse:
                self.m_sequence = (self.m_sequence + 1) % 8
            else:
                raise Exception(f'[Stepper_Driver] Invalid reverse value: {self.m_reverse}]')
            
            self.m_steps += math.copysign(1, p_steps)
            time.sleep(self.m_step_time)

        self.m_reverse = default_reverse

# class to signal stepper drivers based on gesture commands
class Stepper_Gesture():
    def __init__(self, p_stepper_drive1, p_stepper_drive2, p_update_speed):
        self.m_current_head_position = Head_Position.MOVE_STOP
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_stepper_drive1 = p_stepper_drive1
        self.m_stepper_drive2 = p_stepper_drive2
        self.m_update_speed = p_update_speed
        self.m_x_steps = 0 #initial value
        self.m_z_steps = 0 #initial value

        # constants
        self.m_c_STEPPER_MAX_STEPS = 1024
        self.m_c_STEPPER_X_CNTR_TO_FRONT = -1.0
        self.m_c_STEPPER_Z_CNTR_TO_LEFT = 1.0
        self.m_c_STEPPER_Z_CNTR_TO_RIGHT = -1.0
        self.m_c_STEPPER_X_CNTR_TO_BACK = 1.0

        # start thread to update stepper motor positions
        self.m_thread_stepper_gesture = threading.Thread(target=self.update)
        self.m_thread_stepper_gesture.daemon = True
        self.m_thread_stepper_gesture.start()

    def __del__(self):
        pass

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

    # we're returning the amount of steps taken for x and z
    def get_status(self):
        return [self.m_x_steps, self.m_z_steps]

    # thread to update stepper motor positions
    def update(self):
        while True:
            self.m_x_steps = self.m_stepper_drive1.get_steps()
            self.m_z_steps = self.m_stepper_drive2.get_steps()

            target_x_steps = 0
            target_z_steps = 0

            if self.m_head_position == Head_Position.MOVE_LEFT:
                target_z_steps = self.m_c_STEPPER_Z_CNTR_TO_LEFT * self.m_c_STEPPER_MAX_STEPS
            elif self.m_head_position == Head_Position.MOVE_RIGHT:
                target_z_steps = self.m_c_STEPPER_Z_CNTR_TO_RIGHT * self.m_c_STEPPER_MAX_STEPS
            elif self.m_head_position == Head_Position.MOVE_FORWARD:
                target_x_steps = self.m_c_STEPPER_X_CNTR_TO_FRONT * self.m_c_STEPPER_MAX_STEPS
            elif self.m_head_position == Head_Position.MOVE_BACKWARD:
                target_x_steps = self.m_c_STEPPER_X_CNTR_TO_BACK * self.m_c_STEPPER_MAX_STEPS
            elif self.m_head_position == Head_Position.MOVE_STOP:
                pass

            x_steps = target_x_steps - self.m_x_steps
            z_steps = target_z_steps - self.m_z_steps

            self.m_stepper_drive1.step(int(x_steps))
            self.m_stepper_drive2.step(int(z_steps))

            time.sleep(self.m_update_speed)

# ----------------------------------------------------------------------------- #
# by:           Marco Tan (tanm27, 400433483)
#               Emily Attai (attaie, 400452653)
# last updated: 2023-02-25
# description:  code for vibration motor and vibration activation

# wrapper class to play buzzer patterns to alert user of positions that are out of bounds
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

    # wowee we can play morse code now, isn't that cool?
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

# class to control vibration motor from gestures
class Vibration():
    def __init__(self, p_buzzer_pin, p_loop_delay):
        self.m_buzzer = Buzzer_Wrapper(p_buzzer_pin)
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_loop_delay = p_loop_delay
        
        # for threading of user alert w/ vibration motor
        self.thread_user_alert = threading.Thread(target=self.user_alert)
        self.thread_user_alert.daemon = True
        self.thread_user_alert.start()

    def __del__(self):
        pass

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

    # format what pattern to play b/c we need strings for console output
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

    # thread to play buzzer patterns
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

# ----------------------------------------------------------------------------- #

# global objects b/c of threading so that these values can be accessed by all functions and  threads 
orientation = Orientation(p_alpha=0.9, p_window_size=10, p_round=2)
gestures = Gestures(p_config_file="config.json", p_gesture_window_time=1.0)

stepper_x = Stepper_Driver(p_pins=[25, 8, 7, 1], p_step_time=0.001, p_reversed=True)
stepper_z = Stepper_Driver(p_pins=[0, 5, 6, 13], p_step_time=0.001, p_reversed=True)
stepper_ctrl = Stepper_Gesture(p_stepper_drive1=stepper_x, p_stepper_drive2=stepper_z, p_update_speed=0.1)

vibration = Vibration(p_buzzer_pin=14, p_loop_delay=5.0)

# ----------------------------------------------------------------------------- #

# function to help with parsing xyz data (you will see)
def xyz_list_parse(p_xyz):
    return_val = [0.0, 0.0, 0.0]

    # check if all numbers
    if all(isinstance(n, (int, float)) for n in p_xyz):
        return_val = p_xyz
    
    # round to 1 decimal place
    return_val = [round(n, 1) for n in return_val]

    return return_val

# function to print statuses to console
def console_output_fn():
    # constants
    COLUMN_WIDTH = 18
    COLUMN_DOUBLE = int((COLUMN_WIDTH) * 2)
    COLUMN_THIRD = int((COLUMN_WIDTH) / 3)
    COLUMN_NUM = COLUMN_THIRD - 1
    PRINT_DELAY = 1.0

    # header layout
    header = f'{"Timestamp":^{COLUMN_WIDTH}}|{"Orientation":^{COLUMN_DOUBLE}} |' + \
             f'{"Gestures":^{COLUMN_WIDTH}}|{"Steppers":^{COLUMN_WIDTH}}|' + \
             f'{"Vibration":^{COLUMN_WIDTH}}|'
    subheader = f'{" ":^{COLUMN_WIDTH}}|' + \
                f'{"X raw":^{COLUMN_THIRD}}{"Y raw":^{COLUMN_THIRD}}{"Z raw":^{COLUMN_THIRD}}|' + \
                f'{"X EMA":^{COLUMN_THIRD}}{"Y EMA":^{COLUMN_THIRD}}{"Z EMA":^{COLUMN_THIRD}}|' + \
                f'{" ":^{COLUMN_WIDTH}}|' + \
                f'{"X":^{COLUMN_THIRD}}{"Z":^{COLUMN_THIRD}}{" ":^{COLUMN_THIRD}}|' + \
                f'{" ":^{COLUMN_WIDTH}}|'
    header_counter = 0

    global orientation
    global gestures
    global stepper_ctrl
    global vibration

    # main loop
    while True:
        # print header every 10 iterations
        if header_counter % 10 == 0:
            for _ in range(len(header)):
                print("-", end="")
            print()
            print(header)
            print(subheader)
            for _ in range(len(header)):
                print("-", end="")
            print()

        # get data
        time_now = time.strftime("%H:%M:%S", time.localtime())

        xyz_ema = orientation.get_ema()
        xyz_raw = orientation.get_raw()

        xyz_ema = xyz_list_parse(xyz_ema)
        xyz_raw = xyz_list_parse(xyz_raw)

        gestures_now = gestures.get_status()
        stepper_now = stepper_ctrl.get_status()
        stepper_now = [0, 0] if stepper_now == [None, None] else stepper_now
        vibration_now = vibration.get_status()

        # format data to output string and print
        outputString = f'{time_now:^{COLUMN_WIDTH}}|' + \
                       f'{xyz_raw[0]:^{COLUMN_NUM}}|' + \
                       f'{xyz_raw[1]:^{COLUMN_THIRD}}|' + \
                       f'{xyz_raw[2]:^{COLUMN_NUM}}|' + \
                       f'{xyz_ema[0]:^{COLUMN_NUM}}|' + \
                       f'{xyz_ema[1]:^{COLUMN_THIRD}}|' + \
                       f'{xyz_ema[2]:^{COLUMN_NUM}}|' + \
                       f'{gestures_now:^{COLUMN_WIDTH}}|' + \
                       f'{int(stepper_now[0]):^{COLUMN_NUM}}|' + \
                       f'{int(stepper_now[1]):^{COLUMN_THIRD}}|' + \
                       f'{"":^{COLUMN_NUM}}|' + \
                       f'{vibration_now:^{COLUMN_WIDTH}}|'
        print(outputString)
        header_counter += 1

        # pause to allow plot to update
        time.sleep(PRINT_DELAY)

# ----------------------------------------------------------------------------- #

# main function
def main():
    # constants
    MAIN_DELAY = 0.1
    
    # start console output thread
    console_output_thread = threading.Thread(target=console_output_fn)
    console_output_thread.daemon = True
    console_output_thread.start()

    global orientation
    global gestures
    global stepper_ctrl
    global vibration

    # matplotlib related variables because matplotlib looks so cool
    fig, ax = plt.subplots(nrows=3, ncols=1)
    # list of queues for raw data
    raw_xyz_queues = [
        deque(maxlen=100),
        deque(maxlen=100),
        deque(maxlen=100)
    ]
    # list of queues for ema data
    ema_xyz_queues = [
        deque(maxlen=100),
        deque(maxlen=100),
        deque(maxlen=100)
    ]



    # get gesture from orientation sensor data, send to stepper and vibration functions
    while True:
        gestures.set_xyz(p_xyz=orientation.get_ema())
        stepper_ctrl.set_head_position(p_head_position=gestures.get())
        vibration.set_head_position(p_head_position=gestures.get())

        # # this part here is extra because matplotlib just looks cool
        # # add data to queues
        # xyz_ema = orientation.get_ema()
        # xyz_raw = orientation.get_raw()

        # xyz_ema = xyz_list_parse(xyz_ema)
        # xyz_raw = xyz_list_parse(xyz_raw)

        # for i in range(3):
        #     raw_xyz_queues[i].append(xyz_raw[i])
        #     ema_xyz_queues[i].append(xyz_ema[i])

        # # now plot
        # for i in range(3):
        #     ax[i].plot(raw_xyz_queues, label="Raw")
        #     ax[i].plot(ema_xyz_queues, label="EMA")
        #     ax[i].scatter(range(len(raw_xyz_queues)), raw_xyz_queues)
        #     ax[i].scatter(range(len(ema_xyz_queues)), ema_xyz_queues)
        #     plt.draw()

        time.sleep(MAIN_DELAY)
        # plt.clf()

if __name__ == "__main__":
    print("We recommend setting your terminal to full screen to see the data better.")
    time.sleep(2)
    main()
