
from fractions import Fraction
from typing import Any, Set, Iterable, Tuple

Time = Fraction
Duration = Fraction

Track = Iterable[Tuple[Set[Node], Duration]]

class Note:
    def __init__(self, key: int, instrument):
        self.key = key
        self.instrument = instrument

class Span:
    def __init__(self, notes: Set[Note], length: Duration):
        self.notes = notes
        self.length = length
    def traverse(self) -> Track:
        yield (self.notes, self.duration)
    def get_length(self) -> Duration:
        return self.length

class Superspan(Span):
    def __init__(self, subspans: Iterable[Span]):
        self.length = sum(subspan.get_length() for subspan in subspans)
        self.subspans = subspans
    def traverse(self) -> Track:
        for subspan in self.subspans:
            yield from subspan.traverse()
    def get_length(self) -> Duration:
        return self.length

def compose(seed, levels: int):
    
