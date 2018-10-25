
from fractions import Fraction
from typing import Any

class Duration:
    def take(self, amount: Fraction) -> Duration:
        raise NotImplementedError

class Infinite(Duration):
    def __gt__(self, value):
        return True
    def __ge__(self, value):
        return True
    def __lt__(self, value):
        return False
    def __le__(self, value):
        return False
    def __eq__(self, value):
        return False
    def take(self, amount: Fraction) -> Duration:
        return Finite(amount)

class Finite(Duration):
    def __init__(self, length: Fraction):
        self.length = length
    def __gt__(self, value):
        return (not isinstance(other, Infinite)) and self.length > other.length
    def __ge__(self, value):
        return (not isinstance(other, Infinite)) and self.length >= other.length
    def __lt__(self, value):
        return isinstance(other, Infinite) or self.length < other.length
    def __le__(self, value):
        return isinstance(other, Infinite) or self.length <= other.length
    def __eq__(self, value):
        return isinstance(other, Finite) and self.length == other.length
    def take(self, amount: Fraction) -> Duration:
        if amount > self.length:
            raise ValueError
        else:
            self.length -= amount
            return Finite(amount)

