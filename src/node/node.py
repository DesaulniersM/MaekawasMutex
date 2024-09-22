from mutual_exclusion import IDistributedMutex
from networking import multicastmultithreadcomms

from enum import Enum
import queue

class States(enum):
    Reply = 0
    Request = 1
    Holding = 2


# Three types of messages that can be sent by a node
class Messages(enum):
    Request = 0         # Request to enter CS. Sent to subset quorum members
    Reply = 1           # Reply to Request. This will ALWAYS be a "You may enter CS" reply.
    Release = 2         # Release message communicates that the CS is exited and quorum members may reply to next queue members



class Node():
    def __init__(self) -> None:
        self.current_state = States.
        self.quorum_socket = multicastmultithreadcomms.MulticastingP2PNode()

        self.request_queue = queue.Queue()
        
        
        pass


    # This function runs the node processes, calling the maekawa and networking modules as needed
    def run(self):

        while(True):
            
            match state:
                case States.Holding:
                    # This node is waiting for a release message from a node in their quorum
                    new_message = self.quorum_socket.listen()
                    
                    # IF the new message is another request. Queue it and listen for release
                    if new_message == Messages.Request:
                        self.request_queue.put( new_host)

                    # if the new message is a release, pop the node from the queue and change your state from held
                    elif new_message == Messages.Release:
                        self.request_queue.get()
                        self.current_state = 
                        
                        
                case States.Request:
                    # code for pattern 2
                case States.Request:
                    # code for pattern N
                case _:
                    # default code block