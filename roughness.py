
import numpy as np

# Formula from http://www.acousticslab.org/learnmoresra/moremodel.html

def roughness(f1, a1, f2, a2):
    fmin = np.minimum(f1, f2)
    fmax = np.maximum(f1, f2)
    amin = np.minimum(a1, a2)
    amax = np.maximum(a1, a2)
    X = amin * amax
    Y = 2*amin / (amin + amax)
    s = 0.24/(0.0207*fmin + 18.96)
    s2 = s*(fmax - fmin)
    Z = np.exp(-3.5*s2) - np.exp(-5.75*s2)
    return X**0.1 * 0.5*(Y**3.11) * Z