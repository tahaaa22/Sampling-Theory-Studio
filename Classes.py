class Signal:
    def __init__(self, X_List, Y_list):
        self.X_Coordinates = X_List
        self.Y_Coordinates = Y_list
        self.noisy_Y_Coordinates = Y_list
        self.max_freq = 0
        self.sampling_rate = 0
        self.noise = 50


class Component:
    def __init__(self):
        self.frequency = 0
        self.magnitude = 0
