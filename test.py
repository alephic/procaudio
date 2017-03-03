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

class TestGen(AudioGenerator):
  def amp(self, t):
    return math.sin(2*math.pi*440*t)

if __name__ == '__main__':
  play.play(Scaled(0.5, TestGen()))
