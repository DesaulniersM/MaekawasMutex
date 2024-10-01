from mutual_exclusion import IDistributedMutex
from networking import multicastmultithreadcomms

import queue

######################### Constants ####################################

MAJORITY_QUORUM_VOTES = N - 1 #Probably will have to be an initialized class variable

########################### TYPES ######################################

# we can change these to const dicts or whatever to be consistent with eachother later. I'm just used to making enums for C++
class States(enum):
    Holding = 0
    Requesting = 1
    Listening = 2





######################### Class Definition ###############################


class Maekawa():
    def __init__(self, quorum_socket) -> None:
        self.current_state = States.Listening   # Start in listening state by default

        self.votes = 0      #Number of votes in favor of this node accessing CS
        self.voted = False  # If this variable is true, This node has not sent/received a Release message it is waiting on
        
        # self.quorum_socket =         # represents multicast

        self.request_queue = queue.Queue()          # queue for tracking votes
        
        

    # # This function runs the node processes, calling the maekawa and networking modules as needed
    # def run(self, sock):

    #         new_state = sock.recvfrom()
    #         # STATE CHANGES SHOULD ONLY BE CHANGED WHEN SENDING OR RECEVING MESSAGES.
    #         # IN OTHER WORDS, THIS WHILE LOOP SHOULD ONLY LOOP WHEN  ANEW MESSAGE COMES IN.
            
    #         match self.current_state:
    #             case States.Holding:
                    
    #                 # IF the new message is another request. Queue it and listen for release
    #                 if new_message == Messages.Requesting:
    #                     self.request_queue.put( new_host)

    #                 # if the new message is a release, pop the node from the queue and change your state from held
    #                 elif new_message == Messages.Release:
    #                     self.request_queue.get()
    #                     # self.current_state =            # Go back to waiting for either a request from another node or a decision to access again
                        
                        
    #             case States.Request:
    #                 # This node has d
    #                 if new_message == Messages.Requesting:
    #                 # IF the new message is another request, queue it and continue listening for releases

    #                     self.request_queue.put( new_host)
    #                 elif new_message == Messages.Reply:
    #                     # Increment vote counter (or whatever data structure check)
    #                     self.votes += 1
                        
    #                     if self.votes >= MAJORITY_QUORUM_VOTES:
    #                         # access_critical_section()
    #                         # self.current_state = States.
    #                         pass
                        
    #             case States.Listening:

    #                 # Listener hears a release
    #                 if new_message == Messages.Release:
                        
    #                     # Set voted flag to false
    #                     self.voted = False
    #                     if not self.request_queue.Empty():
    #                         # Queue is not empty. Send another vote (pops queue) and set flag
    #                         self.quorum_socket.send_to(self.request_queue.get(), Messages.Vote)
    #                         self.voted = True
                            
    #                 elif new_message  == Messages.Request:

    #                     # Put new requestor in queue and pop them if you vote. otherwise wait for release
    #                     self.request_queue.put(new_host_from_message)
    #                     if self.voted == False:
    #                         self.voted = True
    #                         self.quorum_socket.send_to(self.request_queue.get(), Messages.Vote)
                            
    #             case _:
    #                 # default code block




# Throw some tests here

if __name__=="__main__":
    
   

