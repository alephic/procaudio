

class Scale:
    def index_to_freq(self, index):
        raise NotImplementedError

class EqualTemperament(Scale):
    def __init__(self, base_frequency: int, tones_per_octave: int):
        self.base_frequency = base_frequency
        self.tones_per_octave = tones_per_octave
    
    def index_to_freq(self, index):
        return self.base_frequency * 2.0**(index/self.tones_per_octave)