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
        self._v = np.maximum(self._v, other.timestamp) # updates clock with maximum value for each peer

    def inc(self):
        self._v[self._si] += 1

    # currently expects VectorClock type, and then gets its timestamp, but should allow passing raw vector too
    def causal(self, other):
        return VectorClock.check_causality(self.timestamp, other.timestamp)

    # Setters/Getters
    @property
    def timestamp(self):
        return self._v

    @staticmethod
    def check_causality(before, after):
        # TODO: RH - add type hints and allow either vectors of same length or VectorClock types to be compared
        # Return True if VC_before <= VC_after for all processes (elements)
        return np.all(before <= after)
    
if __name__=="__main__":
    vc1 = VectorClock(8, 0)
    vc2 = VectorClock(8, 1)

    vc1.inc()
    vc2.inc()
    vc2.inc()
    vc2.inc()

    print("VC1:", vc1.timestamp)
    print("VC2:",vc2.timestamp)

    vc1.update(vc2)
    print("VC1:", vc1.timestamp)
    print("VC2:",vc2.timestamp)

    print("Did VC1 happen before VC2? :", vc1.causal(vc2))
