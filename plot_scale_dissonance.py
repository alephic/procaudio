
from tone import dissonance, EqualTemperament
import numpy as np
import matplotlib.pyplot as plt

def plot_dissonance(scale=EqualTemperament(440, 12), show=True):
    base_freq = scale.key_to_freq(0)
    plt.plot(
        np.arange(scale.keys_per_octave+1),
        np.array([dissonance(base_freq, scale.key_to_freq(i)) for i in range(scale.keys_per_octave+1)])
    )
    if show:
        plt.show()