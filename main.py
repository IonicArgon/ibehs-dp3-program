from hardware.orientation import Orientation
# from hardware.steppers import Steppers 
# from hardware.vibration import Vibration
from hardware.vibration import Head_Position

# important imports
import threading
import time
import sys

def main():
    orientation = Orientation(0.9, 10, 2)

    while True:
        print(orientation.get())
        time.sleep(0.1)

if __name__ == "__main__":
    main()