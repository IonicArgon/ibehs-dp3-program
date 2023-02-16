# space for imports later
from gpiozero import Buzzer
from lib.gestures import Head_Position
import time
import threading


#Creating a vibration class 

class Vibration():
    def __init__(self, p_buzzer_pin):
        self.m_buzzer = Buzzer(p_buzzer_pin)
        self.m_head_position = Head_Position.MOVE_STOP
        
        self.thread_user_alert = threading.Thread(target=self.user_alert) #creating a new thread for the user_alert function so that it can run concurrently with other ones 
        self.thread_user_alert.daemon = True
        self.thread_user_alert.start()

    def __del__(self):
        self.m_buzzer.off()

    def set_head_position(self, p_head_position):
        self.m_head_position = p_head_position

#This function below is linked to the vibration class created above.
#It evaluates whether the person's head position is equal to the set head positions.
#If it doesn't match any of those it will activate the vibration motor
        
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
    
