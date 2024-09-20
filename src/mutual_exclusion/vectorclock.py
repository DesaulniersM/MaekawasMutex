"""Simple class for Vector Clock functionality
        - TODO: RH - will adjust to match variable naming conventions for Maekawa
"""
import numpy as np # Could do without numpy, but I've included it for ease of use
from functools import cmp_to_key

class VectorClock:
    def __init__(self, self_index, num_peers=5, timestamp=None) -> None:
        self._si = self_index # This is how we know where to increment
        if timestamp is not None:
            self._v = np.asarray(timestamp).astype(int)
        else:
            self._v = np.zeros(num_peers, dtype=int)

    def update(self, other):
        self.inc()
        self._v = np.maximum(self._v, other.timestamp) # updates clock with maximum value for each peer

    def inc(self):
        self._v[self._si] += 1

    # currently expects VectorClock type, and then gets its timestamp, but should allow passing raw vector too
    # def causal(self, other):
    #     return VectorClock.check_causality(self.timestamp, other.timestamp)

    # Setters/Getters
    @property
    def timestamp(self):
        return self._v
    
    # specials for direct comparison of VC to VC
    def __lt__(self, other): # actually checks less than or equal to across entire timestamp
        # standard "sorted" algorithm in python uses __lt__ as default comparator
        return VectorClock.check_causality(self.timestamp, other.timestamp)

    @staticmethod
    def check_causality(before, after):
        # TODO: RH - add type hints and allow either vectors of same length or VectorClock types to be compared
        # Return True if VC_before <= VC_after for all processes (elements)
        return np.all(before <= after)

    @staticmethod
    def argsort(vc_set):
        """Returns indices of ordered vector clock set (array of vector clocks)"""
        # return sorted(range(len(vc_set)), key=cmp_to_key(lambda a,b: -1 if VectorClock.check_causality(vc_set[a], vc_set[b]) else 1))
        return sorted(range(len(vc_set)), key=cmp_to_key(lambda a,b: -1 if vc_set[a] < vc_set[b] else 1))
    
if __name__=="__main__":
    vc1 = VectorClock(0, num_peers=8)
    vc2 = VectorClock(1, num_peers=8)

    vc1.inc()
    vc2.inc()
    vc2.inc()
    vc2.inc()

    print("VC1:", vc1.timestamp)
    print("VC2:",vc2.timestamp)

    vc1.update(vc2)
    print("VC1:", vc1.timestamp)
    print("VC2:",vc2.timestamp)

    print("Did VC1 happen before VC2? :", vc1 < vc2)

    # Verify sorting is working properly (inconsistent timestamp comparisons simply evaluate to 'happens after' during sorting, but these shouldn't be present in real vector timestamps)
    phony_vcs = [VectorClock(i,timestamp=ts) for i,ts in enumerate((np.random.rand(15).reshape(5,3) * 3 // 1).astype(int))]
    print("Original: \n", [vc.timestamp for vc in phony_vcs])
    print("Sorted  : \n", [vc.timestamp for vc in sorted(phony_vcs)])
    print("Partially Ordered: \n", [phony_vcs[i].timestamp for i in VectorClock.argsort(phony_vcs)])

    # Spot check - looks like things are working for point to point comparisons...
    for vc in phony_vcs:
        print(f"{phony_vcs[0].timestamp} happens before {vc.timestamp}? : ", phony_vcs[0] < vc)
