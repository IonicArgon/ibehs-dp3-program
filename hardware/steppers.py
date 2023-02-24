# space for imports
import threading
import time
import sys
import RPi.GPIO as GPIO # type: ignore[import]

sys.path.append('..')

from lib.gestures import Head_Position


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

        # constants
        self.m_c_STEPPER_STEPS_PER_ROTATION = 4096
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
    
    def step(self, p_steps):
        for i in range(p_steps):
            for pin in range(4):
                GPIO.output(self.m_pins[pin], self.m_c_STEPPER_STEP_SEQUENCE[self.m_sequence][pin])
            if self.m_reverse:
                self.m_sequence = (self.m_sequence - 1) % 8
            elif not self.m_reverse:
                self.m_sequence = (self.m_sequence + 1) % 8
            else:
                raise Exception(f'[Stepper_Driver] Invalid reverse value: {self.m_reverse}]')
            
            self.m_steps += 1
            time.sleep(self.m_step_time)

class Stepper_Gesture():
    def __init__(self, p_stepper_drive1, p_stepper_drive2, p_update_speed):
        self.m_current_head_position = Head_Position.MOVE_STOP
        self.m_head_position = Head_Position.MOVE_STOP
        self.m_stepper_drive1 = p_stepper_drive1
        self.m_stepper_drive2 = p_stepper_drive2
        self.m_update_speed = p_update_speed
        self.m_x_steps = 0
        self.m_z_steps = 0

        # constants
        self.m_c_STEPPER_STEPS_PER_ROTATION = 4096
        self.m_c_STEPPER_X__CNTR_TO_FRONT = -4.0
        self.m_c_STEPPER_Z_CNTR_TO_LEFT = 4.0
        self.m_c_STEPPER_Z_CNTR_TO_RIGHT = -4.0
        self.m_c_STEPPER_X_CNTR_TO_BACK = 4.0

        self.m_thread_stepper_gesture = threading.Thread(target=self.update)
        self.m_thread_stepper_gesture.daemon = True
        self.m_thread_stepper_gesture.start()

    def __del__(self):
        pass

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

    def get_status(self):
        return (self.m_x_steps, self.m_z_steps)

    def update(self):
        while True:
            self.m_x_steps = self.m_stepper_drive1.get_steps()
            self.m_z_steps = self.m_stepper_drive2.get_steps()

            target_x_steps = 0
            target_z_steps = 0

            if self.m_head_position == Head_Position.MOVE_LEFT:
                target_z_steps = self.m_c_STEPPER_Z_CNTR_TO_LEFT * self.m_c_STEPPER_STEPS_PER_ROTATION
            elif self.m_head_position == Head_Position.MOVE_RIGHT:
                target_z_steps = self.m_c_STEPPER_Z_CNTR_TO_RIGHT * self.m_c_STEPPER_STEPS_PER_ROTATION
            elif self.m_head_position == Head_Position.MOVE_FRONT:
                target_x_steps = self.m_c_STEPPER_X__CNTR_TO_FRONT * self.m_c_STEPPER_STEPS_PER_ROTATION
            elif self.m_head_position == Head_Position.MOVE_BACK:
                target_x_steps = self.m_c_STEPPER_X_CNTR_TO_BACK * self.m_c_STEPPER_STEPS_PER_ROTATION
            elif self.m_head_position == Head_Position.MOVE_STOP:
                pass

            x_steps = target_x_steps - self.m_x_steps
            z_steps = target_z_steps - self.m_z_steps

            self.m_stepper_drive1.step(x_steps)
            self.m_stepper_drive2.step(z_steps)

            time.sleep(self.m_update_speed)
            
# for testing purposes
if __name__ == '__main__':
    test_stepper = Stepper_Driver([0, 5, 6, 13], 0.002, False)
    test_stepper.step(4096 / 2)
    time.sleep(5)
    test_stepper.step(-(4096 / 2))
    time.sleep(5)