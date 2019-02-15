
import numpy as np

def osc(f, freq):
    return lambda t: f(t*freq)

def noise(t):
    return np.random.normal(size=t.shape)