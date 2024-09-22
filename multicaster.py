"""
Simple multicast server/client

Contains all functionality needed to:
    - Set up UDP server socket
    - Multicast to a particular group
    - Listen on muticast address
    - Listen on UDP server socket
    - Send directly to peer
    - Pack and unpack messages
    - Defines message structures
"""
import struct, socket, queue, select
import numpy as np
from src.mutual_exclusion.vectorclock import *

HOSTS = [('',5551), ('',5552), ('',5553)] # These will obviously not all be localhost upon creation

QUORA = {
    "a": '226.0.0.51',
    "b": '226.0.0.52',
    "c": '226.0.0.53'
}
HOST_MEMBER_QUORA = {
    0: ["b", "c"],
    1: ["a", "c"],
    2: ["a", "b"]
}
HOST_TARGET_QUORUM = {
    0: "a",
    1: "b",
    2: "c"
}

TARGET_QUORUM_HOST = {v:k for k,v in HOST_TARGET_QUORUM.items()}

# MESSAGE LEN IS ALWAYS 2 bytes + vector clock size: 1 byte node id (0-255), 8 byte (0,2**64-1) x N-element vector clock, 1 byte enum
MESSAGE_FIXED_SIZE = 2 + 8*len(HOSTS)

def pack_message(node, reqtype):
    message = struct.pack('Q', (node.name, node.vc, reqtype))
    return message

def unpack_message(message):
    return struct.unpack('Q', message)

# Borrowing this helper class for single machine multi-threaded testing from my project: https://github.com/jmaggio14/imagepypelines/blob/develop/imagepypelines/core/util.py
import threading
# class BaseCommThread(threading.Thread):
#     '''
#     Parent Class to all thread manager classes.
#     '''
#     def __init__(self):
#         super().__init__(name=self.__class__.__name__)
#         self.daemon = False # Changed from True to see if that helps my current use case

#     def __enter__(self):
#         '''
#         Starts the thread in its own context manager block.
#         Note: If the running thread is meant to be run indefinitely it is not
#               recommended to use it as a context manager as once you exit the
#               context manager, the thread will safely shut down via the
#               __exit__() method.
#         '''
#         self.run()

#     def __exit__(self, exc_type, exc_value, traceback):
#         '''
#         Is called once the context leaves the manager, safely signals the
#         running thread to shutdown.
#         '''
#         self.stop_thread()

#     # ____ Overload Function _________________________________________________
#     def _execute(self):
#         """Overload me!!!"""
#         pass

#     # ____ Run Function ______________________________________________________
#     def run(self):
#         '''
#         This function is to be overloaded in the child class. If the thread is
#         to be run indefinitely (as in not for a fixed duration), you MUST
#         structure this function as follows:

#         --[START]--------------------------------------------------------------
#         self.t = threading.current_thread()  # Grab current threading context
#         ...
#         while getattr(self.t, 'running', True):
#             ...
#         ...
#         --[END]--------------------------------------------------------------

#         This is necessary as the classes stop_thread() method can safely shut
#         down the running thread by changing self.running to False, thus
#         invalidating the while loop's condition.
#         '''
#         self.t = threading.current_thread()
#         while getattr(self.t, 'running', True):
#             self._execute()

#     # ____ Thread Killer _____________________________(Kills with kindness)___
#     def stop_thread(self):
#         '''
#         This is a convenience function used to safely end the running thread.
#         Note: This will only end the running thread if the run() function
#               checks for the classes 'running' attribute (as demonstrated in
#               the docstring of the run() function above).
#               This only works if the running thread is not hanging, this will
#               prevent the while loop from re-evaluating its condition
#         '''
#         print("Closing Thread " + self.name)
#         self.running = False
#         self.join()
#         print(f"{self.name} has stopped")


# class P2PNode(BaseCommThread):
class P2PNode:
    def __init__(self, hostid):
        # super().__init__()
        self.id = hostid

        # Set up request state tracker (at most one request at a time)
        self.request_state = [False] * len(HOSTS) # May need this to be thread safe...
        self.reset = False

        # Set up multicast node socket. Other nodes can respond given the address which comes in with the multicasted message
        self.msock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        self.multicast_group = HOST_TARGET_QUORUM[self.id]

        # Set up general use send/recv socket. I think we'll need this for 1:1 comms between specific nodes for INQUIRE messages
        self.listeners = []
        self.p2psock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # THIS IS THE MAIN COMMS CHANNEL!!! KNOWN TO ALL HOSTS!!!
        self.p2psock.setblocking(0)
        self.p2psock.bind(HOSTS[hostid])
        self.listeners.append(self.p2psock)

        # Set up multicast listener socket(s) - potentially one per multicast member group
        for qk in HOST_MEMBER_QUORA[self.id]:
            # Create multicast client socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setblocking(0)
            s.bind(HOSTS[TARGET_QUORUM_HOST[qk]]) # This needs to be the server which we're listening for in the quorum we're part of
            addmeplz = struct.pack('4sL', socket.inet_aton(QUORA[qk]), socket.INADDR_ANY)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, addmeplz)

            # Append to listeners list
            self.listeners.append(s)

        # init vector clock
        self.vc = VectorClock(hostid, len(HOSTS))

        # Priority Queue for managing requests (eventually from maekawa)
        self.request_queue = queue.PriorityQueue() # items will be (self.id, self.vc) since VCs are comparable!

    def __str__(self):
        return f"{HOSTS[self.id]}: {self.vc}"

    def critical_section(self):
        print(self)

    def _message_handler(self):
        # This effectively executes the Maekawa state-machine
        # Likely we'll just pass in multicast send and send callbacks to Maekawa so it can send stuff in the proper case?
        while True:
            # select readable socket
            r, _, err = select.select(self.listeners, [], self.listeners)

            for sock in r:
                locked = np.all(self.request_state)
                # Maekawa_StateMachine(send, read, sock, self) # This will execute any sends and receives needed given the incoming message from a certain host

            for s in err:
                print(s, s.error)

    def _critical_section_guard(self):
        while True:
            self.reset = False
            # Maekawa_AcquireLock(multicast_send, sock) # sends REQUEST messages to target quorum
            
            while True:
                # Check whether we have the lock
                if np.all(self.request_state):
                    self.critical_section()
                    # Maekawa_ReleaseLock(multicast_send, sock) # sends RELEASE messages to target quorum

                elif self.reset:
                    break

    def run(self):
        # MAIN THREAD
        # Do any setup required, begin both of the worker threads (each running indefinitely), and handle cleanup elegantly

        # THREAD 1 - Message handler via select loop. Get message from selected socket (either multicast or p2p) and forward message to Maekawa library to decide what to do next
        # Makawa returns the message or action to be taken
        # If a message needs to be sent we can handle it here
        # Otherwise we just do updates to this node's variables or state and recv the next message

        # THREAD 2 - REQUEST and RELEASE sender + Critical section trigger
        # 0) self.reset = False
        # 1) send REQUEST
        # 2) Wait with while loop for executing the critical section if the state is ever all True or self.reset is True
        # 3)    if self.reset: reset state vector and resend a request to TARGET_QUORUM via break
        # 4) send RELEASE
        

        ############################
        print("Hi we've entered the execution function")
        def test_func():
            for i in range(5):
                print(f"[{i}] Howdy, I'm " + threading.current_thread().name)

        t1 = threading.Thread(target=test_func)
        t2 = threading.Thread(target=test_func)

        print(t1,t2)
        t1.start()
        t2.start()

        t1.join()
        t2.join()

if __name__=="__main__":
    n = P2PNode(0)
    n.run()