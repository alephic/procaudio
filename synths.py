
import numpy as np

def sin(freq):
    return lambda t: np.sin(2*np.pi*freq*t)

def noise(t):
    return np.random.normal(scale=0.5, size=t.shape)