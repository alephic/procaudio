
from fractions import Fraction as F

class Note:
    def __init__(self, key, sus):
        self.key = key
        self.sus = sus
    def __repr__(self):
        return f'Note({self.key}, {self.sus})'

class TimedNote(Note):
    def __init__(self, key, sus, time):
        super().__init__(key, sus)
        self.time = time
    @classmethod
    def from_note(cls, note, time):
        return cls(note.key, note.sus, time)
    def __repr__(self):
        return f'TimedNote({self.key}, {self.sus}, {self.time})'

class TimeTracker:
    def __init__(self, time=0):
        self.time = time

class Span:
    def __init__(self, length, children):
        self.length = length
        self.children = children
    def unroll(self, time_tracker=None):
        time_tracker = time_tracker or TimeTracker()
        for child in self.children:
            if isinstance(child, Note):
                yield TimedNote.from_note(child, time_tracker.time)
            else:
                yield from child.unroll(time_tracker)
        time_tracker.time += self.length

class Position:
    def __init__(self, time, meter_level):
        self.time = time
        self.meter_level = meter_level
    def __hash__(self):
        return hash(self.time) ^ hash(self.meter_level)
    def __eq__(self, other):
        return self.time == other.time and self.meter_level == other.meter_level