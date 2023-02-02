from hardware.orientation import Orientation
from hardware.steppers import Steppers 
from hardware.vibration import Vibration

# for testing
from lib.ema import EMA
import random as rd
import matplotlib.pyplot as plt
import numpy as np

def random_walk(p_steps, p_step_size):
    walk = []
    y = 0.0
    for _ in range(p_steps):
        walk.append(y)
        y += np.random.normal(0.0, p_step_size)
    return np.array(walk)

if __name__ == "__main__":
    test_list = random_walk(100, 0.25)
    ema = EMA(0.9, 10, 2)
    ema_list = []

    for i in test_list:
        ema.update(i)
        ema_list.append(ema.get())
    
    plt.plot(test_list)
    plt.plot(ema_list)
    plt.show()


