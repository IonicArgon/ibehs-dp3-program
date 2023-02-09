from hardware.orientation import Orientation
from hardware.steppers import Steppers 
from hardware.vibration import Vibration

# important imports
import asyncio

# imports for testing
import matplotlib.pyplot as plt
from collections import deque 

async def main():
    orientation = Orientation(0.9, 10, 2)
    ema_out_x = deque(maxlen=100)
    ema_out_y = deque(maxlen=100)
    ema_out_z = deque(maxlen=100)

    print("starting orientation update task")

    loop = asyncio.get_running_loop()
    loop.create_task(orientation.update(orientation))
    
    print("orientation update task started")

    while True:
        ema_out = await orientation.get()
        ema_out_x.append(ema_out[0])
        ema_out_y.append(ema_out[1])
        ema_out_z.append(ema_out[2])
        print("x: ", ema_out[0], "y: ", ema_out[1], "z: ", ema_out[2])

        plt.plot(ema_out_x, label="x")
        plt.plot(ema_out_y, label="y")
        plt.plot(ema_out_z, label="z")
        plt.scatter(range(len(ema_out_x)), ema_out_x)
        plt.scatter(range(len(ema_out_y)), ema_out_y)
        plt.scatter(range(len(ema_out_z)), ema_out_z)
        plt.legend(loc="upper left")

        plt.draw()
        plt.pause(0.1)
        plt.clf()
        print("plot updated")

if __name__ == "__main__":
    asyncio.run(main())
