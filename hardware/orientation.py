# by:           Marco Tan, Emily Attai
# last updated: 2023-02-25
# description:  reading orientation sensor and outputting smoothed data

# package imports
import threading
import time
from lib.sensor_library import Orientation_Sensor

# local imports
from lib.ema import EMA

# ----------------------------------------------------------------------------- #

# class to read orientation sensor and output smoothed data
class Orientation():
    def __init__(self, p_alpha, p_window_size, p_round):
        self.m_sensor = Orientation_Sensor()
        self.m_ema_xyz = [
            EMA(p_alpha, p_window_size, p_round),
            EMA(p_alpha, p_window_size, p_round),
            EMA(p_alpha, p_window_size, p_round)
        ]
        self.m_raw = [None, None, None]
        self.m_ema_out = [None, None, None]

        self.thread_ema_update = threading.Thread(target=self.update)
        self.thread_ema_update.daemon = True
        self.thread_ema_update.start()

    def __del__(self):
        ...

    def get_ema(self):
        return self.m_ema_out

    def get_raw(self):
        return self.m_raw

    def update(self):
        while True:
            # sometimes the i2c bus gets stuck so we need to try again
            try:
                self.m_raw = self.m_sensor.euler_angles()
            except OSError as e:
                print(f'[Orientation] OSError {e}, trying again...')
                time.sleep(0.1)
                continue

            # stepping through each axes' EMA and updating it
            for i in range(3):
                self.m_ema_xyz[i].update(self.m_raw[i])
                self.m_ema_out = [self.m_ema_xyz[0].get(), 
                                  self.m_ema_xyz[1].get(), 
                                  self.m_ema_xyz[2].get()]
            time.sleep(0.1)

