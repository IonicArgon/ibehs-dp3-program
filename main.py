from hardware.orientation import Orientation
from hardware.steppers import Steppers 
from hardware.vibration import Vibration

# important imports
import threading
import time

# imports for testing
import matplotlib.pyplot as plt
from collections import deque 

def main():
    orientation = Orientation(0.9, 10, 2)
    ema_out_x = deque(maxlen=25)
    ema_out_y = deque(maxlen=25)
    ema_out_z = deque(maxlen=25)

    while True:
        ema_out = orientation.get()
        ema_out_x.append(ema_out[0])
        ema_out_y.append(ema_out[1])
        ema_out_z.append(ema_out[2])

        plt.plot(ema_out_x, label="x")
        plt.plot(ema_out_y, label="y")
        plt.plot(ema_out_z, label="z")
        plt.legend()

        plt.draw()
        plt.pause(0.01)
        plt.clf()

if __name__ == "__main__":
<<<<<<< HEAD
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
=======
    main()
>>>>>>> 8ef79f82ef4acbb72fec9c33ef7e23718dbcc02c
