# by:           Marco Tan, Emily Attai
# last updated: 2023-02-25
# description:  main file for the project

# package imports
import threading
import time

# local imports
from hardware.orientation import Orientation
from hardware.steppers import Stepper_Driver, Stepper_Gesture
from hardware.vibration import Vibration
from lib.gestures import Gestures

# ----------------------------------------------------------------------------- #

# global objects b/c of threading
orientation = Orientation(p_alpha=0.9, p_window_size=10, p_round=2)
gestures = Gestures(p_config_file="config.json", p_gesture_window_time=1.0)

stepper_x = Stepper_Driver(p_pins=[25, 8, 7, 1], p_step_time=0.001, p_reversed=True)
stepper_z = Stepper_Driver(p_pins=[0, 5, 6, 13], p_step_time=0.001, p_reversed=True)
stepper_ctrl = Stepper_Gesture(p_stepper_drive1=stepper_x, p_stepper_drive2=stepper_z, p_update_speed=0.1)

vibration = Vibration(p_buzzer_pin=14, p_loop_delay=5.0)

# ----------------------------------------------------------------------------- #

# fn to print statuses to console
def console_output_fn():
    # constants
    COLUMN_WIDTH = 18
    COLUMN_DOUBLE = int((COLUMN_WIDTH) * 2)
    COLUMN_THIRD = int((COLUMN_WIDTH) / 3)
    COLUMN_NUM = COLUMN_THIRD - 1

    # header layout
    header = f'{"Timestamp":^{COLUMN_WIDTH}}|{"Orientation":^{COLUMN_DOUBLE}}|' + \
             f'{"Gestures":^{COLUMN_WIDTH}}|{"Steppers":^{COLUMN_WIDTH}}|' + \
             f'{"Vibration":^{COLUMN_WIDTH}}|'
    subheader = f'{" ":^{COLUMN_WIDTH}}|' + \
                f'{"X raw":^{COLUMN_THIRD}}{"Y raw":^{COLUMN_THIRD}}{"Z raw":^{COLUMN_THIRD}}|' + \
                f'{"X EMA":^{COLUMN_THIRD}}{"Y EMA":^{COLUMN_THIRD}}{"Z EMA":^{COLUMN_THIRD}}' + \
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

        xyz_now = orientation.get_ema()
        xyz_raw = orientation.get_raw()

        # quick helper lambda because we don't need a whole function for this
        xyz_list_parse = lambda xyz: [0, 0, 0] if xyz == [None, None, None] else \
            [round(xyz[0], 1), round(xyz[1], 1), round(xyz[2], 1)]

        xyz_now = xyz_list_parse(xyz_now)
        xyz_raw = xyz_list_parse(xyz_raw)

        gestures_now = gestures.get_status()
        stepper_now = stepper_ctrl.get_status()
        stepper_now = [0, 0] if stepper_now == [None, None] else stepper_now
        vibration_now = vibration.get_status()

        # format data to output string and print
        outputString = f'{time_now:^{COLUMN_WIDTH}}|' + \
                       f'{xyz_now[0]:^{COLUMN_NUM}}|' + \
                       f'{xyz_now[1]:^{COLUMN_THIRD}}|' + \
                       f'{xyz_now[2]:^{COLUMN_NUM}}|' + \
                       f'{xyz_raw[0]:^{COLUMN_NUM}}|' + \
                       f'{xyz_raw[1]:^{COLUMN_THIRD}}|' + \
                       f'{xyz_raw[2]:^{COLUMN_NUM}}|' + \
                       f'{gestures_now:^{COLUMN_WIDTH}}|' + \
                       f'{int(stepper_now[0]):^{COLUMN_THIRD}}|' + \
                       f'{int(stepper_now[1]):^{COLUMN_THIRD}}|' + \
                       f'{"":^{COLUMN_THIRD}}|' + \
                       f'{vibration_now:^{COLUMN_WIDTH}}|'
        print(outputString)
        header_counter += 1
        time.sleep(1)

# ----------------------------------------------------------------------------- #

# main function
def main():
    # start console output thread
    console_output_thread = threading.Thread(target=console_output_fn)
    console_output_thread.daemon = True
    console_output_thread.start()

    global orientation
    global gestures
    global stepper_ctrl
    global vibration

    # get gesturefrom orientation sensor data, send to stepper and vibration
    while True:
        gestures.set_xyz(p_xyz=orientation.get())
        stepper_ctrl.set_head_position(p_head_position=gestures.get())
        vibration.set_head_position(p_head_position=gestures.get())
        time.sleep(0.1)

if __name__ == "__main__":
    main()
