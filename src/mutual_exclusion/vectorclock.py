"""Simple class for Vector Clock functionality
        - TODO: RH - will adjust to match variable naming conventions for Maekawa
"""
import numpy as np # Could do without numpy, but I've included it for ease of use

class VectorClock:
    def __init__(self, num_peers, self_index) -> None:
        self._v = np.zeros(num_peers, dtype=int)
        self._si = self_index # This is how we know where to increment

    def update(self, other):
        self.inc()
        self._v = np.maximum(self._v, other) # updates clock with maximum value for each peer

    def inc(self):
        self._v[self._si] += 1

    # Setters/Getters
    @property
    def vc(self):
        return self._v

    @staticmethod
    def check_causality(before, after):
        # Return True if VC_before <= VC_after for all processes (elements)
        return np.all(before <= after)