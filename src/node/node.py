from mutual_exclusion import IDistributedMutex
from networking import multicastmultithreadcomms

from enum import Enum
import queue

######################### Constants ####################################

MAJORITY_QUORUM_VOTES = N - 1 #Probably will have to be an initialized class variable

########################### TYPES ######################################

# we can change these to const dicts or whatever to be consistent with eachother later. I'm just used to making enums for C++
class States(enum):
    Holding = 0
    Requesting = 1
    Listening = 2


# Three types of messages that can be sent by a node
class Messages(enum):
    Request = 0         # Request to enter CS. Sent to subset quorum members
    Vote = 1           # Reply to Request. This will ALWAYS be a "You may enter CS" reply.
    Release = 2         # Release message communicates that the CS is exited and quorum members may reply to next queue members



######################### Class Definition ###############################

class Node():
    def __init__(self) -> None:
        self.current_state = States.Listening   # Start in listening state by default

        self.votes = 0      #Number of votes in favor of this node accessing CS
        self.voted = False  # If this variable is true, This node has not sent/received a Release message it is waiting on
        
        self.quorum_socket = multicastmultithreadcomms.MulticastingP2PNode()        # represents multicast

        self.request_queue = queue.Queue()          # queue for tracking votes
        
        
        pass


    # This function runs the node processes, calling the maekawa and networking modules as needed
    def run(self):

        while(True):

            # STATE CHANGES SHOULD ONLY BE CHANGED WHEN SENDING OR RECEVING MESSAGES.
            # IN OTHER WORDS, THIS WHILE LOOP SHOULD ONLY LOOP WHEN  ANEW MESSAGE COMES IN.
            
            match state:
                case States.Holding:
                    # This node is waiting for a release message from a node in their quorum, but not accessing the critical section
                    new_message = self.quorum_socket.listen()
                    
                    # IF the new message is another request. Queue it and listen for release
                    if new_message == Messages.Request:
                        self.request_queue.put( new_host)

                    # if the new message is a release, pop the node from the queue and change your state from held
                    elif new_message == Messages.Release:
                        self.request_queue.get()
                        self.current_state =            # Go back to waiting for either a request from another node or a decision to access again
                        
                        
                case States.Request:
                    # This node has decided it needs to access the critical section
                    new_message = self.quorum_socket.listen()

                    if new_message == Messages.Requesting:
                    # IF the new message is another request, queue it and continue listening for releases

                        self.request_queue.put( new_host)
                    elif new_message == Messages.Reply:
                        # Increment vote counter (or whatever data structure check)
                        self.votes += 1
                        
                        if self.votes >= MAJORITY_QUORUM_VOTES:
                            access_critical_section()
                            self.current_state = States.
                        


                case States.Listening:
                    new_message = self.quorum_socket.listen()

                    # Listener hears a release
                    if new_message == Messages.Release:
                        
                        # Set voted flag to false
                        self.voted = False
                        if not self.request_queue.Empty():
                            # Queue is not empty. Send another vote (pops queue) and set flag
                            self.quorum_socket.send_to(self.request_queue.get(), Messages.Vote)
                            self.voted = True
                            
                    elif new_message  == Messages.Request:

                        # Put new re    questor in queue and pop them if you vote. otherwise wait for release
                        self.request_queue.put(new_host_from_message)
                        if self.voted == False:
                            self.voted = True
                            self.quorum_socket.send_to(self.request_queue.get(), Messages.Vote)
                            
                case _:
                    # default code block




# Throw some tests here

if __name__=="__main__":
    
    # set up 
    test_node_1 = Node()
    test_node_2 = Node()

    # run in threads


