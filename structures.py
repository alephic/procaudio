
from fractions import Fraction
from typing import Any, Iterable

Derivation = Iterable['DerivationOperation']

Time = Fraction
Duration = Fraction

class DerivationContext:
    def __init__(self, start: Time, length: Duration):
        self.start = start
        self.length = length

class DerivationOperation:
    def apply(self, context: DerivationContext, continuation: Derivation):
        raise NotImplementedError