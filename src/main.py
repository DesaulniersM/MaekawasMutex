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
import socket
import threading





if __name__ == "__main__":
    NUMBER_OF_PROCESSES_IN_TEST = 4
    BASE_PORT_NUMBER = 9000
   
    import pprint


    # Hear we create the entire list of host_id's 
    this_test_bed_id = socket.gethostbyname(socket.gethostname())
    entire_host_id_list = [None]*NUMBER_OF_PROCESSES_IN_TEST

    for i in range(0,NUMBER_OF_PROCESSES_IN_TEST):
        entire_host_id_list[i] = (this_test_bed_id, BASE_PORT_NUMBER + i)

    print(entire_host_id_list)

    # Run global init

    # Distributed Mutex object
    dist_mutex = CDistributedMutex()
    

    dist_mutex.GlobalInitialize(0, entire_host_id_list)

    pprint.pprint(dist_mutex.__dict__)

    dist_mutex.run(event=threading.Event())  # run some number of times

    # dist_mutex.QuitAndCleanup()
