
import numpy as np

DEFAULT_BUFFER_SIZE = 1024

NO_VALUE = -1.0

class Source:
    def set_buffer_size(self, buffer_size):
        raise NotImplementedError()
    def get_output(self, t):
        raise NotImplementedError()

class Constant(Source):
    def __init__(self, value):
        self.value = value
        self.out_buffer = np.full(DEFAULT_BUFFER_SIZE, value, dtype=np.float)
    def get_output(self, t):
        return self.out_buffer
    def set_buffer_size(self, buffer_size):
        if buffer_size != self.out_buffer.shape[0]:
            self.out_buffer = np.full(buffer_size, self.value, dtype=np.float)

class SourceBundle:
    def __init__(self, parent, sources):
        self._dict = {k: (v if isinstance(v, Source) else Constant(v)) for k, v in sources.items()}
        self._parent = parent
    def __getattr__(self, name):
        return self._dict[name].get_output(self._parent._t)

class Module(Source):
    def __init__(self, **sources):
        self.sources = SourceBundle(self, sources)
        self.buffer_size = DEFAULT_BUFFER_SIZE
        self.out_buffer = np.zeros(self.buffer_size)
        self._t = -1
    def update_output(self):
        raise NotImplementedError()
    def set_buffer_size(self, buffer_size):
        if buffer_size != self.buffer_size:
            for source in self.sources._dict.values():
                source.set_buffer_size(buffer_size)
            self.out_buffer = np.zeros(buffer_size)
            self.buffer_size = buffer_size
    def get_output(self, t):
        if self._t != t:
            self._t = t
            self.update_output()
        return self.out_buffer

class SourceList(Source):
    def __init__(self, sources):
        self._list = sources
        self._t = -1
    def get_output(self, t):
        self._t = t
        return self
    def set_buffer_size(self, buffer_size):
        for source in self._list:
            source.set_buffer_size(buffer_size)
    def __getitem__(self, i):
        return self._list[i].get_output(self._t)
    def __iter__(self):
        for source in self._list:
            yield source.get_output(self._t)
    def __len__(self):
        return len(self._list)

class Noise(Module):
    def __init__(self):
        super().__init__()
    def update_output(self):
        self.out_buffer = np.random.uniform(-1.0, 1.0, size=self.buffer_size)

class Oscillator(Module):
    base_period = 1.0
    def __init__(self, frequency, sample_rate=44100):
        super().__init__(frequency=frequency)
        self.phase = 0
        self.sample_rate = sample_rate
    def update_output(self):
        np.copyto(self.out_buffer, self.sources.frequency)
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
    def __init__(self, base, envelope):
        super().__init__(base=base, envelope=envelope)
    def update_output(self):
        np.multiply(self.sources.envelope, self.sources.base, out=self.out_buffer)

class Mix(Module):
    def __init__(self, sources):
        super().__init__(source_list=SourceList(sources))
    def update_output(self):
        np.copyto(self.out_buffer, self.sources.source_list[0])
        for i in range(1, len(self.sources.source_list)):
            np.add(self.sources.source_list[i], self.out_buffer, out=self.out_buffer)

class Filter(Module):
    def __init__(self, cutoff, base):
        super().__init__(cutoff=cutoff, base=base)
        self.buf0 = 0
        self.buf1 = 0
        self.buf2 = 0
        self.buf3 = 0
    def update_output(self):
        base = self.sources.base
        cutoff = self.sources.cutoff
        for i in range(self.buffer.shape[0]):
            self.buf0 += cutoff[i]*(base[i] - self.buf0)
            self.buf1 += cutoff[i]*(self.buf0 - self.buf1)
            self.buf2 += cutoff[i]*(self.buf1 - self.buf2)
            self.buf3 += cutoff[i]*(self.buf2 - self.buf3)
            self.write_out_sample(base[i], i)
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
    def __init__(self, event_times, sample_rate=44100):
        self.sample_rate = sample_rate
        self.last_event = None
        self.curr_event = None
        self.event_iter = iter(event_times)
        self._t = -1
        self.out_buffer = np.zeros(DEFAULT_BUFFER_SIZE)
        self.update_events()
    def set_buffer_size(self, size):
        if size != self.out_buffer.shape[0]:
            self.out_buffer = np.zeros(size)
    def get_output(self, t):
        if self._t != t:
            self._t = t
            self.update_output()
        return self.out_buffer
    def update_events(self):
        self.last_event = self.curr_event
        self.curr_event = None
        try:
            evt = next(self.event_iter)
        except StopIteration:
            return
        self.curr_event = evt
    def update_output(self):
        self.out_buffer.fill(NO_VALUE)
        for i in range(self.out_buffer.shape[0]):
            time = (i + self._t)/self.sample_rate
            while self.curr_event is not None and time >= self.curr_event:
                self.update_events()
            if self.last_event is not None:
                self.out_buffer[i] = time - self.last_event
            
class ADSR(Module):
    def __init__(self, press: Trigger, a, d, release: Trigger = None, s = 0, r = 0):
        if release is not None:
            super().__init__(press=press, release=release)
        else:
            super().__init__(press=press)
        self.a = a
        self.d = d
        self.s = s
        self.r = r
        self.has_sustain = release is not None
    def update_output(self):
        press = self.sources.press
        self.out_buffer.fill(1)
        if self.a > 0.0:
            np.subtract(self.out_buffer, (self.a-press)/self.a,
                out=self.out_buffer,
                where=np.logical_and(press < self.a, press != NO_VALUE)
            )
        np.subtract(self.out_buffer, np.minimum(press-self.a, self.d)*((1.0-self.s)/self.d),
            out=self.out_buffer,
            where=press >= self.a
        )
        zero_condition = press == NO_VALUE
        if self.has_sustain:
            release = self.sources.release
            np.subtract(self.out_buffer, release * (self.s/self.r),
                out=self.out_buffer,
                where=np.logical_and(release != NO_VALUE, release < self.r)
            )
            np.logical_or(zero_condition, release > self.r, out=zero_condition)
        np.copyto(self.out_buffer, 0, where=zero_condition)
        
class NoteFreq(Source):
    def __init__(self, notes, scale, sample_rate=44100):
        self.note_iter = iter(notes)
        self.scale = scale
        self.sample_rate = sample_rate
        self.curr_freq = 0
        self._t = -1
        self.next_note = None
        self.update_next_note()
        self.out_buffer = np.zeros(DEFAULT_BUFFER_SIZE)
    def update_next_note(self):
        if self.next_note is not None:
            self.curr_freq = self.scale.key_to_freq(self.next_note.key)
        self.next_note = None
        try:
            self.next_note = next(self.note_iter)
        except StopIteration:
            pass
    def set_buffer_size(self, size):
        if size != self.out_buffer.shape[0]:
            self.out_buffer = np.zeros(size)
    def get_output(self, t):
        if self._t != t:
            self._t = t
            self.update_output()
        return self.out_buffer
    def update_output(self):
        for i in range(self.out_buffer.shape[0]):
            time = (i + self._t)/self.sample_rate
            while self.next_note is not None and time >= self.next_note.time:
                self.update_next_note()
            self.out_buffer[i] = self.curr_freq