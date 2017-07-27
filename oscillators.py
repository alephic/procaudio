#!/usr/local/bin/python3
import math
import play

class AudioGenerator:
  # Return amplitude of this generator's waveform at time t (in sec)
  def amp(self, t):
    return 0

class Offset(AudioGenerator):
  def __init__(self, base, offset):
    self.base = base
    self.offset = offset
  def amp(self, t):
    return self.base.amp(t - self.offset)

class Sum(AudioGenerator):
  def __init__(self, *bases):
    self.bases = bases
  def amp(self, t):
    return sum(base.amp(t) for base in self.bases)

class Sine(AudioGenerator):
  def __init__(self, freq, phase=0):
    self.freq = freq
    self.phase = phase
  def amp(self, t):
    return math.sin(2*math.pi*(self.freq*t + self.phase))

class Scaled(AudioGenerator):
  def __init__(self, coef, base):
    self.coef = coef
    self.base = base
  def amp(self, t):
    return self.coef*self.base.amp(t)

class Product(AudioGenerator):
  def __init__(self, *bases):
    self.bases = bases
  def amp(self, t):
    r = 1
    for base in self.bases:
      r *= base.amp(t)
    return r

class TimeScaled(AudioGenerator):
  def __init__(self, scale, base):
    self.scale = scale
    self.base = base
  def amp(self, t):
    return self.base.amp(t*self.scale)

# Attack-Sustain-Decay envelope using sinusoidal curves
class SineASD:
  def __init__(self, attack, sustain, decay):
    self.attack = attack
    self.sustain = sustain
    self.decay = decay
  def amp(self, t):
    if t < 0:
      return 0
    elif t < self.attack and self.attack > 0:
      return math.sin(((t/self.attack) - 0.5)*math.pi)*0.5 + 0.5
    elif self.sustain is None or t < self.attack+self.sustain:
      return 1
    elif t < self.attack+self.sustain+self.decay:
      return math.sin((((t-self.attack-self.sustain)/self.decay) + 0.5)*math.pi)*0.5 + 0.5
    return 0

# Attack-Sustain-Decay envelope using logistic curves
class ExpASD:
  def __init__(self, attack, sustain, decay, tail_cutoff=2.5):
    self.attack = attack
    self.sustain = sustain
    self.decay = decay
    self.tail_cutoff = tail_cutoff
    self.cutoff_amp = math.exp(-self.tail_cutoff**2)
  def amp(self, t):
    if t < 0:
      return 0
    elif t < self.attack:
      return (math.exp(-((t/self.attack - 1.0)*self.tail_cutoff)**2) - self.cutoff_amp)/(1.0-self.cutoff_amp)
    elif t < self.attack+self.sustain:
      return 1.0
    elif t < self.attack+self.sustain+self.decay:
      return (math.exp(-(((t-self.attack-self.sustain)/self.decay)*self.tail_cutoff)**2) - self.cutoff_amp)/(1.0-self.cutoff_amp)
    return 0

class Loop(AudioGenerator):
  def __init__(self, period, base):
    self.period = period
    self.base = base
  def amp(self, t):
    return self.base.amp(t % self.period)

if __name__ == '__main__':
  play.play(Scaled(0.5, Loop(1, Product(ExpASD(0.05, 0, 0.25, tail_cutoff=2.5), Sine(80)))))
