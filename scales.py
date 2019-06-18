

class Scale:
    def key_to_freq(self, index):
        raise NotImplementedError

class EqualTemperament(Scale):
    def __init__(self, base_frequency, base_key, keys_per_octave):
        self.base_frequency = base_frequency
        self.base_key = base_key
        self.keys_per_octave = keys_per_octave
    
    def key_to_freq(self, index):
        return self.base_frequency * 2.0**((index - self.base_key)/self.keys_per_octave)

TTET = EqualTemperament(440, 9, 12)