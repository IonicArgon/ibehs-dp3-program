if __name__ == "__main__":
    print("Hello World!")



from gpiozero import Buzzer
import sys 
import logging
import threading
import time

#boundaries 
move_forward = #need to test to find these values 
move_backward =
move_right =
move_left =
move_stop = 

class US_Al: 
    def user_alert:
        logging.info()
        while True:
            if head_position == move_forward:
                vibration_motor.off()
            elif head_position == move_backward:
                vibration_motor.off()
            elif head_position == move_right:
                vibration_motor.off()
            elif head_position == move_left:
                vibration_motor.off()
            elif head_position == move_stop:
                vibration_motor.off()
            else: 
                vibration_motor.on()
                    
alert = threading.Thread(target = user_alert, args=(1,))
alert.start()
