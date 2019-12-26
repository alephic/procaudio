
from tone import dissonance, TTET
import numpy as np
import matplotlib.pyplot as plt

def plot_dissonance(scale=TTET, show=True):
    base_freq = scale.key_to_freq(0)
    plt.plot(
        np.arange(scale.keys_per_octave+1),
        np.array([dissonance(base_freq, scale.key_to_freq(i)) for i in range(scale.keys_per_octave+1)])
    )
    if show:
        plt.show()

if __name__ == "__main__":
    plot_dissonance()