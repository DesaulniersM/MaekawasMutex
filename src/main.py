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

if __name__=="__main__":
    pass