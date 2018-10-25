

class Scale:
    def index_to_freq(self, index):
        raise NotImplementedError

class ET(Scale):
    def __init__(self, tones_per_octave: int):
        self.tones_per_octave = tones_per_octave
    
    def index_to_freq(self, index):
        return 440 * 2.0**(index/self.tones_per_octave)
