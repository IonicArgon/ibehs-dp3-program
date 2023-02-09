## reusable expomential moving average class
class EMA:
    def __init__(self, p_alpha, p_window_size, p_round) -> None:
        self.m_alpha = p_alpha
        self.m_out = 0.0
        self.m_last_out = 0.0
        self.m_window = []
        self.m_window_size = p_window_size
        self.m_round = p_round

    def set_alpha(self, p_alpha):
        self.m_alpha = p_alpha

    def set_window_size(self, p_window_size):
        self.m_window_size = p_window_size

    def get(self):
        return self.m_out

    def update(self, p_in):
        self.m_window.append(p_in)
        if len(self.m_window) < self.m_window_size:
            self.m_out = None
            return
        else:
            self.m_window.pop(0)

        window_avg = round(sum(self.m_window) / self.m_window_size, self.m_round)
        self.m_out = self.m_alpha * window_avg + (1 - self.m_alpha) * self.m_last_out
        self.m_last_out = self.m_out
        