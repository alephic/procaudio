#!/usr/local/bin/python3
import math
import play

class AudioGenerator:
  # Return amplitude of this generator's waveform at time t (in sec)
  def amp(self, t):
    return 0

class Sequencer(AudioGenerator):
  # notes: [(onset_time, gen)]
  def __init__(self, notes):
    self.notes = notes
  
  def amp(self, t):
    return sum(gen.amp(t - onset_time) for (onset_time, gen) in self.notes)

class TestGenerator(AudioGenerator):
  def amp(self, t):
    return math.sin(t*440*2*math.pi+220*math.sin(t*2*math.pi))*0.5

if __name__ == '__main__':
  play.play(TestGenerator())
