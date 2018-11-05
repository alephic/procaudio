
from fractions import Fraction
from typing import Any, Iterable

Time = Fraction
Duration = Fraction

class TrackItem:
    pass

Track = Iterable[TrackItem]

class Note(TrackItem):
    def __init__(self, key: int, velocity: float):
        self.key = key
        self.velocity = velocity

class Rest(TrackItem):
    def __init__(self, duration: Duration):
        self.duration = duration

