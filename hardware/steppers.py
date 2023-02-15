fr# space for imports later




import time
import sys
import threading
import RPi.GPIO as GPIO


stepper_x = #add pin later (this is to move joystick in x direction) 
stepper_y = #add pin later (this is to move joystick in y direction) 
CW = 1 #clockwise rotation (in this case, this one will move it forward and to the right)
CCW = 0 # counterclockwise rotation (in this case, this will move it backwards and to the left) 
SPR = 48 #steps per revolution (360/7.5)
step_count = SPR #can be changed to adjust speed 

GPIO.setmode(GPIO.BCM)
GPIO.setup(stepper_x, GPIO.OUT)
GPIO.setup(stepper_y, GPIO.OUT)


#this one below sets the direction of the stepper
#GPIO.output( #stepper, direction) 

class Steppers():
    def __init__(self):
        self.thread_joystick_control = threading.Thread (target=self.joystick_control)
        self.thread_joystick_control.daemon = True
        self.thread_joystick_control.start()


def joystick_control(self):
    while True:
        if self.m_head_position == Head_Position.MOVE_FORWARD:
            for i in range (step_count):
                GPIO.output(stepper_y,CW)
                GPIO.output(stepper_y, GPIO.HIGH)
                
        elif self.m_head_position == Head_Position.MOVE_BACKWARD:
            for i in range (step_count):
                GPIO.output(stepper_y,CCW)
                GPIO.output(stepper_y, GPIO.HIGH) 
                
        elif self.m_head_position == Head_Position.MOVE_RIGHT:
            for i in range (step_count):
                GPIO.output(stepper_x,CW)
                GPIO.output(stepper_y, GPIO.HIGH) 
                
        elif self.m_head_position == Head_Position.MOVE_LEFT:
            for i in range (step_count):
                GPIO.output(stepper_x,CCW)
                GPIO.output(stepper_y, GPIO.HIGH) 
                
        elif self.m_head_position == Head_Position.MOVE_STOP:
            GPIO.output(stepper_x, False) #idk if this is the right command
            GPIO.output(stepper_y, False) 
                

        time.sleep(0.01) 
