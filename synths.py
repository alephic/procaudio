
import numpy as np

def sin(freq):
    return lambda t: np.sin(2*np.pi*freq*t)

def noise(t):
    return np.random.normal(scale=0.5, size=t.shape)

def linear_decay(length):
    def f(t):
        x = 1.0 - t/length
        return np.clip(x, 0.0, 1.0, out=x)
    return f

