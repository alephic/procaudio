
from collections import OrderedDict
import numpy as np

class Module:
    def __init__(self, input_sources, buffer_size=1024):
        self._input_sources = input_sources
        self.out_buffer = np.zeros(buffer_size)
        self.buffer_size = buffer_size
        self._t = 0
    def update_output(self):
        raise NotImplementedError()
    def _set_buffer_size(self, buffer_size):
        if buffer_size != self.buffer_size:
            self.out_buffer = np.zeros(buffer_size)
            self.buffer_size = buffer_size
    def _get_output(self, t):
        if self._t < t:
            self.update_output()
            self._t += self.buffer_size
        return self.out_buffer
    def __getattr__(self, name):
        if name in self.input_sources:
            return self.input_sources[name]._get_output(self._t)
        else:
            raise AttributeError(f'No attribute or input named "{name}"')
    def __setattr__(self, name, source):
        if name in self.input_sources:
            self.input_sources[name] = source
            source._set_buffer_size(self.buffer_size)
        else:
            raise AttributeError(f'No attribute or input named "{name}"')

class Noise(Module):
    def __init__(self):
        super().__init__({})
    def update_output(self):
        self.out_buffer = np.random.uniform(-1.0, 1.0, size=self.buffer_size)

class Oscillator(Module):
    base_period = 1.0
    def __init__(self, frequency, sample_rate=44100):
        super().__init__({'frequency': frequency})
        self.phase = 0
        self.sample_rate = sample_rate
    def update_output(self):
        self.frequency.copyto(self.out_buffer)
        self.out_buffer *= self.base_period / self.sample_rate
        self.out_buffer[0] += self.phase
        np.cumsum(self.out_buffer, out=self.out_buffer)
        self.phase = self.out_buffer[-1] % self.base_period
        self.apply_oscillator_fn()
    def apply_oscillator_fn(self):
        raise NotImplementedError()

class Saw(Oscillator):
    def apply_oscillator_fn(self):
        np.mod(self.out_buffer, 1.0, out=self.out_buffer)
        np.multiply(self.out_buffer, 2.0, out=self.out_buffer)
        np.subtract(self.out_buffer, 1.0, out=self.out_buffer)

class Sine(Oscillator):
    base_period = 2.0*np.pi
    def apply_oscillator_fn(self):
        np.sin(self.out_buffer, out=self.out_buffer)

class Square(Oscillator):
    def apply_oscillator_fn(self):
        np.mod(self.out_buffer, 1.0, out=self.out_buffer)
        np.greater(self.out_buffer, 0.5, out=self.out_buffer)
        np.multiply(self.out_buffer, 2.0, out=self.out_buffer)
        np.subtract(self.out_buffer, 1.0, out=self.out_buffer)

class Filter:
    def __init__(self, cutoff, resonance, source):
        super().__init__({'cutoff': cutoff, 'source': source})
        self.buf0 = 0
        self.buf1 = 0
        self.buf2 = 0
        self.buf3 = 0
    def update_output(self, t):
        source = self.source
        cutoff = self.cutoff
        for i in range(self.buffer.shape[0]):
            self.buf0 += cutoff[i]*(source[i] - self.buf0)
            self.buf1 += cutoff[i]*(self.buf0 - self.buf1)
            self.buf2 += cutoff[i]*(self.buf1 - self.buf2)
            self.buf3 += cutoff[i]*(self.buf2 - self.buf3)
            self.write_out_sample(source[i], i)
    def write_out_sample(self, source_value, i):
        raise NotImplementedError('Filter mode must be specified by using a subclass of Filter')

class HighPassFilter(Filter):
    def write_out_sample(self, source_value, i):
        self.out_buffer[i] = source_value - self.buf3

class LowPassFilter(Filter):
    def write_out_sample(self, source_value, i):
        self.out_buffer[i] = self.buf3

class BandPassFilter(Filter):
    def write_out_sample(self, source_value, i):
        self.out_buffer[i] = self.buf0 - self.buf3


