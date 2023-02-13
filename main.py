from hardware.orientation import Orientation
from hardware.steppers import Steppers 
from hardware.vibration import Vibration
from hardware.vibration import Head_Position

# important imports
import threading
import time

def main():
    orientation = Orientation(0.9, 10, 2)
    vibration = Vibration(17)

if __name__ == "__main__":
    main()