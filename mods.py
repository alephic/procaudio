
from collections import OrderedDict
import numpy as np

class Source:
    def set_buffer_size(self, buffer_size):
        raise NotImplementedError()
    def get_output(self, t):
        raise NotImplementedError()

class Module(Source):
    def __init__(self, input_sources, buffer_size=1024):
        self._input_sources = input_sources
        for source in self._input_sources.values():
            source.set_buffer_size(buffer_size)
        self.out_buffer = np.zeros(buffer_size)
        self.buffer_size = buffer_size
        self._t = 0
    def update_output(self):
        raise NotImplementedError()
    def set_buffer_size(self, buffer_size):
        if buffer_size != self.buffer_size:
            for source in self._input_sources.values():
                source.set_buffer_size(buffer_size)
            self.out_buffer = np.zeros(buffer_size)
            self.buffer_size = buffer_size
    def get_output(self, t):
        if self._t < t:
            self.update_output()
            self._t += self.buffer_size
        return self.out_buffer
    def __getattr__(self, name):
        if name in self.input_sources:
            return self.input_sources[name].get_output(self._t)
        else:
            raise AttributeError(f'No attribute or input named "{name}"')
    def __setattr__(self, name, source):
        if name in self.input_sources:
            self.input_sources[name] = source
            source.set_buffer_size(self.buffer_size)
        else:
            super().__setattr__(name, source)

class SourceList(Source):
    def __init__(self, sources):
        self._sources = sources
        self._t = 0
    def get_output(self, t):
        self._t = t
        return self
    def set_buffer_size(self, buffer_size):
        for source in self._sources:
            source.set_buffer_size(buffer_size)
    def __getitem__(self, i):
        return self._sources[i].get_output(self._t)
    def __iter__(self):
        for source in self._sources:
            yield source.get_output(self._t)
    def __len__(self):
        return len(self._sources)

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
        self.apply_wave_fn()
    def apply_wave_fn(self):
        raise NotImplementedError()

class Saw(Oscillator):
    def apply_wave_fn(self):
        np.mod(self.out_buffer, 1.0, out=self.out_buffer)
        np.multiply(self.out_buffer, 2.0, out=self.out_buffer)
        np.subtract(self.out_buffer, 1.0, out=self.out_buffer)

class Sine(Oscillator):
    base_period = 2.0*np.pi
    def apply_wave_fn(self):
        np.sin(self.out_buffer, out=self.out_buffer)

class Square(Oscillator):
    def apply_wave_fn(self):
        np.mod(self.out_buffer, 1.0, out=self.out_buffer)
        np.greater(self.out_buffer, 0.5, out=self.out_buffer)
        np.multiply(self.out_buffer, 2.0, out=self.out_buffer)
        np.subtract(self.out_buffer, 1.0, out=self.out_buffer)

class Amp(Module):
    def __init__(self, source, envelope):
        super().__init__({'source': source, 'envelope': envelope})
    def update_output(self):
        self.envelope.multiply(self.source, out=self.out_buffer)

class Mix(Module):
    def __init__(self, sources):
        super().__init__({'sources': SourceList(sources)})
    def update_output(self):
        self.sources[0].copyto(self.out_buffer)
        for i in range(1, len(self.sources)):
            np.add(self.sources[i], self.out_buffer, out=self.out_buffer)

class Constant(Source):
    def __init__(self, value):
        self.value = value
        self.out_buffer.fill(value)
    def get_output(self, t):
        return self.out_buffer
    def set_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size
        self.out_buffer = np.full(buffer_size, self.value)

class Filter(Module):
    def __init__(self, cutoff, source):
        super().__init__({'cutoff': cutoff, 'source': source})
        self.buf0 = 0
        self.buf1 = 0
        self.buf2 = 0
        self.buf3 = 0
    def update_output(self):
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

class Trigger(Source):
    def __init__(self, track, sample_rate=44100, buffer_size=1024):
        self.track = track
        self.sample_rate = sample_rate
        self.last_event = None
        self.curr_event = None
        self.track_iter = iter(track)
        self._t = 0
        self.out_buffer = np.zeros(buffer_size)
        self.update_events()
    def set_buffer_size(self, size):
        self.out_buffer = np.zeros(buffer_size)
    def get_output(self, t):
        if self._t < t:
            self.update_output()
            self._t += self.buffer_size
        return self.out_buffer
    def update_events(self):
        self.last_event = self.curr_event
        self.curr_event = None
        try:
            evt = next(self.track_iter)
        except StopIteration:
            return
        self.curr_event = evt
    def update_output(self):
        self.out_buffer.fill(0)
        for i in range(self.out_buffer.shape[0]):
            time = (i + self._t)/self.sample_rate
            while self.curr_event is not None and time >= self.curr_event:
                self.update_events()
            if self.last_event is not None:
                self.out_buffer[i] = time - self.last_event
            else:
                self.out_buffer[i] = -1.0
            

