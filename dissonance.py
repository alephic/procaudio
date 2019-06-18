import fractions
import math

def dissonance(f1, f2):
    r = fractions.Fraction.from_float(f1 / f2).limit_denominator(100)
    return math.log(r.denominator+r.numerator)