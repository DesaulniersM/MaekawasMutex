"""Program flow:
    - create node with unique 'name' (int ID)
        a) instantiate comms (in either maekawa or vector mode)
        b) begin comms loop
            * CS control (blocks thread)
                - request mutex
                - block until mutex acquired
                - do CS work (append to network shared text file?)
                - release mutex
            * Clock management (dedicated listening thread? discuss with @Matt)
"""

from mutual_exclusion.IDistributedMutex import CDistributedMutex
from quorum_generator.quorum_generator import generate_quorums

IP_MULTICAST_GROUP_PREFIX = (
    "224.0.2."
)  # Prefix for Ad-Hoc multicast group. Each quorum will have one of this and its suffix will just be id number

IP_ADDRESS_LIST = ["138.67.127.173"]


if __name__ == "__main__":

    print(generate_quorums(5))

    # Run global init

    # Distributed Mutex object
    dist_mutex = CDistributedMutex()

    dist_mutex.GlobalInitialize()

    dist_mutex.run(number_of_cs_requests, number_of_runs)  # run some number of times

    dist_mutex.QuitAndCleanup()
