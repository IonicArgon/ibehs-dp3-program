from hardware.orientation import Orientation
from hardware.steppers import Steppers 
from hardware.vibration import Vibration

# for testing
from lib.ema import EMA
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

def test():
    ema = EMA(0.9, 10, 2)

    y = 0.0
    y_list = deque(maxlen=100)
    ema_list = deque(maxlen=100)

    while True:
        try:
            y_list.append(y)
            ema.update(y)
            ema_list.append(ema.get())
            y += np.random.normal(0.0, 0.25)

            plt.plot(y_list, label="y")
            plt.plot(ema_list, label="ema")
            plt.scatter(range(len(y_list)), y_list)
            plt.scatter(range(len(ema_list)), ema_list)
            plt.legend()

            plt.draw()
            plt.pause(0.001)
            plt.clf()
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    raise NotImplementedError