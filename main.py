from hardware.orientation import Orientation
from hardware.steppers import Steppers 
from hardware.vibration import Vibration

from lib.sensor_library import Orientation_Sensor

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
    ema_raw_x = deque(maxlen=25)
    ema_raw_y = deque(maxlen=25)
    ema_raw_z = deque(maxlen=25)

    fig, ax = plt.subplots(3)
    fig.suptitle("Orientation Data")

    plt.ion()

    while True:
        ema_out = orientation.get()
        ema_out_x.append(ema_out[0])
        ema_out_y.append(ema_out[1])
        ema_out_z.append(ema_out[2])

        ema_raw = orientation.get_raw()
        ema_raw_x.append(ema_raw[0])
        ema_raw_y.append(ema_raw[1])
        ema_raw_z.append(ema_raw[2])

        ax[0].plot(ema_out_x, label="EMA")
        ax[0].plot(ema_raw_x, label="Raw")
        ax[0].set_title("X")
        ax[0].legend()

        ax[1].plot(ema_out_y, label="EMA")
        ax[1].plot(ema_raw_y, label="Raw")
        ax[1].set_title("Y")

        ax[2].plot(ema_out_z, label="EMA")
        ax[2].plot(ema_raw_z, label="Raw")
        ax[2].set_title("Z")

        plt.pause(0.01)

if __name__ == "__main__":
    main()
