# space for imports later
from lib.sensor_library import Orientation_Sensor
from lib.ema import EMA
import threading
import time

class Orientation():
    def __init__(self, p_alpha, p_window_size, p_round):
        self.m_sensor = Orientation_Sensor()
        self.m_ema_xyz = [
            EMA(p_alpha, p_window_size, p_round),
            EMA(p_alpha, p_window_size, p_round),
            EMA(p_alpha, p_window_size, p_round)
        ]
        self.m_raw = (None, None, None)
        self.m_ema_out = (None, None, None)

        self.thread_ema_update = threading.Thread(target=self.update)
        self.thread_ema_update.daemon = True
        self.thread_ema_update.start()

    def __del__(self):
        ...

    def get(self):
        return self.m_ema_out

    def update(self):
        while True:
            self.m_raw = self.m_sensor.euler_angles()
            for i in range(3):
                self.m_ema_xyz[i].update(self.m_raw[i])
                self.m_ema_out = (self.m_ema_xyz[0].get(), self.m_ema_xyz[1].get(), self.m_ema_xyz[2].get())
            time.sleep(0.01)

