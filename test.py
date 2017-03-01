#!/usr/local/bin/python3
import math
import play

class AudioGenerator:
  # t will always be greater than all previous values of t
  # that this generator has been given
  # Return amplitude of this generator's waveform at time t (in sec)
  def amp(self, t):
    return 0

class Sequencer(AudioGenerator):
  def __init__(self, note_times):
    self.note_times = note_times
  
  def amp(self, t):
    pass

class TestGenerator(AudioGenerator):
  def amp(self, t):
    return math.sin(t*440*2*math.pi)*0.5

if __name__ == '__main__':
  play.play(TestGenerator())
