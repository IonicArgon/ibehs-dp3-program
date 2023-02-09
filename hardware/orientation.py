# space for imports later
import asyncio
from lib.sensor_library import Orientation_Sensor
from lib.ema import EMA

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
        self.m_lock = asyncio.Lock()

    async def get(self):
        print("getting orientation")
        async with self.m_lock:
            print("orientation locked")
            return self.m_ema_out

    async def update(self):
        while True:
            print("updating orientation")
            async with self.m_lock:
                print("orientation locked")
                self.m_raw = self.m_sensor.euler_angles()
                for i in range(3):
                    self.m_ema_xyz[i].update(self.m_raw[i])
                    self.m_ema_out = (self.m_ema_xyz[0].get(), self.m_ema_xyz[1].get(), self.m_ema_xyz[2].get())
            print("orientation unlocked")
            await asyncio.sleep(0.1)
