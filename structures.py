
from fractions import Fraction
from typing import Any, Iterable

Time = Fraction
Duration = Fraction

Derivation = Iterable['DerivationOperation']

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

class DerivationContext:
    def __init__(self, start: Time, length: Duration, prominence: int):
        self.start = start
        self.length = length
        self.prominence = prominence

class DerivationOperation:
    def run(self, context: DerivationContext, continuation: Derivation) -> Track:
        raise NotImplementedError
