
import numpy as np

# ENVELOPES

# d/dx e**(-x) - e**(-a*x) = 0
# when
# x = -log(1/a)/(a-1)

def bulge(t, peak_pos):
    return 0 # TODO write bulge function