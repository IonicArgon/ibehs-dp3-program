from hardware.orientation import Orientation
from hardware.steppers import Stepper_Driver, Stepper_Gesture
from hardware.vibration import Vibration
from lib.gestures import Gestures

# important imports
import threading
import time

# global objects b/c of threading
'''
orientation = Orientation(p_alpha=0.9, p_window_size=10, p_round=2)
gestures = Gestures(p_config_file="config.json", p_gesture_window_time=1.0)

stepper1 = Stepper_Driver(p_pins=[None, None, None, None], p_step_time=0.002, p_reversed=False)
stepper2 = Stepper_Driver(p_pins=[None, None, None, None], p_step_time=0.002, p_reversed=False)
stepper_ctrl = Stepper_Gesture(p_stepper_drive1=stepper1, p_stepper_drive2=stepper2, p_update_speed=0.1)

vibration = Vibration(p_buzzer_pin=None, p_loop_delay=0.1)


def console_output_fn():
    header = f'{"Timestamp":^15}|{"Orientation":^15}|{"Gestures":^15}|{"Steppers":^15}|{"Vibration":^15}'
    subheader = f'{" ":^15}|{"X":^5}{"Y":^5}{"Z":^5}|{" ":^15}|{"X":^5}{"Z":^5}{" ":^5}|{" ":^15}'
    header_counter = 0

    global orientation
    global gestures
    global stepper_ctrl
    global vibration

    while True:
        if header_counter % 10 == 0:
            for _ in range(len(header)):
                print("-", end="")
            print()
            print(header)
            print(subheader)
            for _ in range(len(header)):
                print("-", end="")
            print()

        time_now = time.strftime("%H:%M:%S", time.localtime())
        xyz_now = orientation.get_xyz()
        gestures_now = gestures.get_status()
        stepper_now = stepper_ctrl.get_status()
        vibration_now = vibration.get_status()

        outputString = f'{time_now:^15}|{xyz_now[0]:^5}{xyz_now[1]:^5}{xyz_now[2]:^5}|{gestures_now:^15}|{stepper_now[0]:^5}{stepper_now[1]:^5}{" ":^5}|{vibration_now:^15}'
        print(outputString)
        header_counter += 1
        time.sleep(1)

def main():
    console_output_thread = threading.Thread(target=console_output_fn)
    console_output_thread.daemon = True
    console_output_thread.start()

    global orientation
    global gestures
    global stepper_ctrl
    global vibration

    while True:
        gestures.set_xyz(p_xyz=orientation.get_xyz())
        stepper_ctrl.set_gesture(p_gesture=gestures.get())
        vibration.set_gesture(p_gesture=gestures.get())
        time.sleep(0.1)
'''

def main():
    test_stepper = Stepper_Driver([0, 5, 6, 13], 0.002, False)
    test_stepper.step(4096 / 2)
    time.sleep(5)
    test_stepper.step(-(4096 / 2))
    time.sleep(5)

if __name__ == "__main__":
    main()