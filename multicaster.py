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
import threading
import sys
import numpy as np
from src.mutual_exclusion.vectorclock import *
from src.networking import *
from enum import Enum



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

# Three types of messages that can be sent by a node
class Messages(Enum):
    Request = 0         # Request to enter CS. Sent to subset quorum members
    Reply = 1           # Reply to Request. This will ALWAYS be a "You may enter CS" reply.
    Release = 2         # Release message communicates that the CS is exited and quorum members may reply to next queue members


TARGET_QUORUM_HOST = {v:k for k,v in HOST_TARGET_QUORUM.items()}

NUMBER_NODES_IN_TARGET_QUORUM = 10

# MESSAGE LEN IS ALWAYS 2 bytes + vector clock size: 1 byte node id (0-255), 8 byte (0,2**64-1) x N-element vector clock, 1 byte enum
MESSAGE_FIXED_SIZE = 2 + 8*len(HOSTS)


def structure_message(hostid, vector_clock, message_enum):
    return str(hostid).encode('utf-8') + vector_clock.tobytes() + str(message_enum).encode('utf-8') # Maybe we should actually use a struct for packing/unpacking???

def parse_message(bmessage):
    hostid = unpack_message(bmessage[0]) # first byte
    vector_clock = VectorClock.frombytes(hostid, bmessage[1:-1]) # middle bytes are vector clock timestamp converted to bytes
    message_enum = unpack_message(bmessage[-1]) # final byte
    return hostid, vector_clock, message_enum

def unpack_message(bmessage):
    return bmessage.decode('utf-8')

class P2PNode:
    def __init__(self, hostid):
        # super().__init__()
        self.id = hostid
        self.active_threads = []
        self.listeners = []

        # Set up request state tracker (at most one request at a time)
        self.request_state = [False] * NUMBER_NODES_IN_TARGET_QUORUM # The number of nodes in the quorum will likely need to be grabbed from maekawa's subset information
        self.reset = False

        # Set up multicast node socket. Other nodes can respond given the address which comes in with the multicasted message
        self.target_multicast_group = QUORA[HOST_TARGET_QUORUM[self.id]] # This is the multicast address of the target quorum
        self._setup_multicast_send_socket()

        # Set up multicast listener socket(s) - potentially one per multicast member group
        for qk in HOST_MEMBER_QUORA[self.id]:
            self._setup_multicast_receive_socket(QUORA[qk])

        # init vector clock
        self.vc = VectorClock(hostid, len(HOSTS)) # RH: ADD A THREAD LOCK OBJECT AS ATTRIBUTE ON CLASS
        # thread lock
        self.vc_lock = threading.Lock()


        # Priority Queue for managing requests (eventually from maekawa)
        self.request_queue = queue.PriorityQueue() # items will be (self.id, self.vc) since VCs are comparable!

    # socket setup - multicast send
    def _setup_multicast_send_socket(self):
        # Create sender socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Need to ensure all sockets are "reuse address" since we connect to same address with multiple sockets
        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)
        sock.settimeout(0)

        # This specifies how many "hops" across the network the multicasted message will travel
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        self.msock = sock
        self.listeners.append(sock)

    # socket setup - p2p send/receive
    def _setup_multicast_receive_socket(self, quorum_multicast_group):
        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)

        sock.setblocking(0)
        sock.bind(('', None)) # Just bind to localhost and a random port number!

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(quorum_multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.listeners.append(sock)

    def __str__(self):
        return f"{HOSTS[self.id]}: {self.vc}"

    def critical_section(self):
        print(self)

    def send_request_to_quorum(self):
        # Protect vector clock increment via lock
        with self.vc_lock:
            self.vc.inc()

        # Multicast needs to be sent over a port which all nodes in the quorum will be listening on (bound to)
        self.msock.sendto(structure_message(self.id, self.vc, Messages.REQUEST), (self.target_multicast_group,HOSTS[self.id][1]))

    def send_release_to_quorum(self):
        # Protect vector clock increment via lock
        with self.vc_lock:
            self.vc.inc()

        # Multicast needs to be sent over a port which all nodes in the quorum will be listening on (bound to)
        self.msock.sendto(structure_message(self.id, self.vc, Messages.RELEASE), (self.target_multicast_group,HOSTS[self.id][1]))


    def _message_handler(self, event):
        # This effectively executes the Maekawa state-machine
        # Likely we'll just pass in multicast send and send callbacks to Maekawa so it can send stuff in the proper case?
        while not event.is_set():

           

            # select readable socket
            r, _, err = select.select(self.listeners, [], self.listeners, 0.1)
            
            
            for sock in r:
                
                new_message = self._process_message(sock)

                # match new_message:
                #     case Messages.Release:
                #         pass
                #     case Messages.Reply:
                #         pass
                #     case Messages.Release:
                #         pass

            # for s in err:
            #     print(s, s.error)

            if event.is_set():
                break
        print("Keyboard Interrupt... Exiting thread ", threading.current_thread().name)

    def _critical_section_guard(self, event):
        while not event.is_set():
            self.reset = False
            # sends REQUEST messages to target quorum
            self.send_request_to_quorum()

            while not event.is_set():
                # Check whether we have permission to access the critical section
                if np.all(self.request_state):
                    self.critical_section()
                    # sends RELEASE messages to target quorum
                    self.send_release_to_quorum()

                elif self.reset:
                    self.request_state[:] = False
                    break

                if event.is_set():
                    break

            if event.is_set():
                break
        print("Keyboard Interrupt... Exiting thread ", threading.current_thread().name)

    def run(self, event=None):
        # MAIN THREAD
        # Do any setup required, begin both of the worker threads (each running indefinitely), and handle cleanup elegantly

        # THREAD 1 - Message handler via select loop. Get message from selected socket (either multicast or p2p) and forward message to Maekawa library to decide what to do next
        # Makawa returns the message or action to be taken
        # If a message needs to be sent we can handle it here
        # Otherwise we just do updates to this node's variables or state and recv the next message

        # Based on approach found here: https://stackoverflow.com/questions/4136632/how-to-kill-a-child-thread-with-ctrlc

        # if not event:
        #     event = threading.Event()

        # try:
        t1 = threading.Thread(target=self._message_handler, args=(event,))
        t1.daemon = True

        t2 = threading.Thread(target=self._critical_section_guard, args=(event,))
        t2.daemon = True

        t1.start()
        t2.start()

        self.active_threads.append(t1)
        self.active_threads.append(t2)

        print("Handling incoming P2P messages with       : ", t1)
        print("Handling outgoing multicast messages with : ", t2)

if __name__=="__main__":
    print("Press CTRL-C a few times to exit.")
    n = P2PNode(0)
    event = threading.Event()
    n.run(event)

    try:
        while n.active_threads: 
            try:
                n.active_threads[-1].join(1)
            except KeyboardInterrupt:
                event.set()
                tmp = n.active_threads.pop()
                print("Removed dead thread: ", tmp)

    except Exception:
        print("Exiting...")
        sys.exit()