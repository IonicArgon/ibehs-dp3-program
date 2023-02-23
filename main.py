from hardware.orientation import Orientation
# from hardware.steppers import Steppers 
# from hardware.vibration import Vibration
from lib.gestures import Gestures

# important imports
import threading
import time
import sys

def main():
    orientation = Orientation(0.9, 10, 2)
    gestures = Gestures("config.json", 5.0)

    while True:
        orientation_xyz = orientation.get()
        gestures.set_xyz(orientation_xyz)
        print(orientation_xyz)
        print(gestures.get())
        time.sleep(0.5)

if __name__ == "__main__":
    main()