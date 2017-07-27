from oscillators import Offset, TimeScaled, AudioGenerator, SineASD
import math

SEMITONE_CONSTANT = 2**(1/12)

class Note(AudioGenerator):
    def __init__(self, base, t0, attack, decay):
        self.base = base
        self.t0 = t0
        self.asd = SineASD(attack, None, decay)
        self.killtime = None
    def amp(self, t):
        return self.asd.amp(t - self.t0)*self.base.amp(t - self.t0)
    def envelope(self, t):
        return self.asd.amp(t - self.t0)
    def kill(self, t):
        self.asd.sustain = t - (self.t0 + self.asd.attack)
        self.killtime = t + self.asd.decay
    def is_dead(self, t):
        return (self.killtime is not None) and t >= self.killtime

def noclip_positive(x):
  return -1/(x+1) + 1

class NoteGen(AudioGenerator):
    def __init__(self, base, attack, decay):
        self.base = base
        self.attack = attack
        self.decay = decay
        self.t = 0
        self.notes = {}
        self.notes2 = set()
        self.new_notes = {}
        self.new_notes2 = {}
        self.kill_notes = set()
        self.kill_notes2 = set()
    def amp(self, t):
        self.t = t
        nn = self.new_notes
        self.new_notes = self.new_notes2
        self.notes.update(nn)
        self.new_notes2 = nn
        self.new_notes2.clear()
        kn = self.kill_notes
        self.kill_notes = self.kill_notes2
        for n in kn:
            self.notes[n].kill(t)
            self.notes2.add(self.notes[n])
            del self.notes[n]
        self.kill_notes2 = kn
        self.kill_notes2.clear()
        for note in list(self.notes2):
            if note.is_dead(t):
                self.notes2.remove(note)
        total = (sum(n.amp(t) for n in self.notes.values()) + sum(n.amp(t) for n in self.notes2)) \
            / (1 + math.log1p(sum(n.envelope(t) for n in self.notes.values()) + sum(n.envelope(t) for n in self.notes2)))
        return total
    def play_note(self, idx):
        self.new_notes[idx] = Note(
            TimeScaled(SEMITONE_CONSTANT ** (idx - 60), self.base),
            self.t, self.attack, self.decay
        )
    def kill_note(self, idx):
        self.kill_notes.add(idx)