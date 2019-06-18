
from fractions import Fraction
from typing import Any, Set, Iterable, Tuple, Mapping

Time = Fraction
Duration = Fraction

class Note:
    def __init__(self, key: int):
        self.key = key

class HeldNote(Note):
    def __init__(self, key: int, length: Duration):
        super().__init__(key)
        self.length = length

Track = Mapping[Time, Note]

# composition procedure:
# start with a base position (time 0, metric level 0)