from mutual_exclusion.vectorclock import VectorClock
from time import sleep
from random import uniform
import threading
from enum import IntEnum
import time

from quorum_generator.quorum_generator import generate_quorums


import socket, queue, select, struct

IP_MULTICAST_GROUP_PREFIX = (
    "224.0.2."
)  # Prefix for Ad-Hoc multicast group. Each quorum will have one of this and its suffix will just be id number

# Three types of messages that can be sent by a node
class Messages(IntEnum):
    Request = 0         # Request to enter CS. Sent to subset quorum members
    Reply = 1           # Reply to Request. This will ALWAYS be a "You may enter CS" reply.
    Release = 2         # Release message communicates that the CS is exited and quorum members may reply to next queue members
    Begin = 3           # This message is used to signal that process 0 has reached it's Minitialize



def structure_message(hostid, vector_clock, message_enum):
    return str(hostid).encode('utf-8') + vector_clock.tobytes + str(message_enum).encode('utf-8') # Maybe we should actually use a struct for packing/unpacking???

def parse_message(bmessage):
    hostid = int(unpack_message(bmessage[0:1])) # first byte
    vector_clock = VectorClock.frombytes(hostid, bmessage[1:-1]) # middle bytes are vector clock timestamp converted to bytes
    message_enum = unpack_message(bmessage[-1:]) # final byte
    return hostid, vector_clock, message_enum

def unpack_message(bmessage):
    return bmessage.decode('utf-8')

class CDistributedMutex:
    def __init__(self) -> None:

        self.locked = False  # This flag is set when any node is known to have the lock

        # thread lock
        self.vc_lock = threading.Lock()

    # • GlobalInitialize() will be called once when the process is started, and it will not be called
    # again. The array hosts will contain information for all of the participants in the system
    # (host, and port). These hosts will be ordered in terms of priority, with lower index having
    # higher priority. This means that the process at the first position hosts[0] will have the highest
    # priority. Assume that this array will be identical and sorted the same at each process. thisHost
    # contains the position (index) of the current host in the hosts array.
    #
    # Input: hosts : a 2D array of (host, port)
    #        this_host : index of this objects personal host:port on hosts list
    def GlobalInitialize(self, this_host, hosts):
        self.entire_host_id_list = hosts
        self.this_host_index = this_host
        self.this_process_host_id = hosts[this_host]
        self.vector_clock = VectorClock(
            self_index=this_host, num_peers=len(hosts)
        )  # Current vector clock view of subset

        # MESSAGE LEN IS ALWAYS 2 bytes + vector clock size: 1 byte node id (0-255), 8 byte (0,2**64-1) x N-element vector clock, 1 byte enum
        self.message_fixed_size = 2 + 8*len(hosts)

        self.generate_quorum_and_multicast_groups()

        self.majority_quorum_votes = len(self.this_process_quorum) 

        self.listeners = []

    def generate_quorum_and_multicast_groups(self):
        self.entire_quorum_list = generate_quorums(len(self.entire_host_id_list))
        self.this_process_quorum = self.entire_quorum_list[self.this_host_index]
        #TODO Added the length of enitre hose id list to the multicast port numbers, because i was seeing incoming direct messages on these multicast addresses. Probably only an issue when running on localhost
        self.multicast_group_list = [(IP_MULTICAST_GROUP_PREFIX+str(i), self.entire_host_id_list[i][1] + len(self.entire_host_id_list)) for i in range(len(self.entire_host_id_list))]
        self.target_multicast_group = self.multicast_group_list[self.this_host_index]

    #   QuitAndCleanup() will be called once when you are done testing your code.
    def QuitAndCleanup(self):
        # Close threads
        pass

    def MCleanup(self):
        self.vector_clock = VectorClock(
            self_index=self.this_host_index, num_peers=len(self.entire_host_id_list)
        )  # Current vector clock view of subset

        

    #   MInitialize() will be called once when starting to test Maekawa’s. May be recalled multiple
    # times, as long as the corresponding cleanup algorithm, MCleanup(), is done after each
    # initialization. The votingGroupHosts array contains an index (to the hosts array) for each
    # host in the voting set/group of the current host.
    #   Input: voting_group_hosts : array of host ids in the set of the current host
    def MInitialize(self, voting_group_hosts = None):
       
        self.votes = 0      #Number of votes in favor of this node accessing CS
        self.voted = False  # If this variable is true, This node has not sent/received a Release message it is waiting on
        
        # Set up multicast node socket. Other nodes can respond given the address which comes in with the multicasted message
        self._setup_multicast_send_socket()

        # Set up multicast listener socket(s) - potentially one per multicast member group
        for i,qk in enumerate(self.entire_quorum_list):
            if (self.this_host_index in qk) and (i != self.this_host_index):
                self._setup_multicast_receive_socket(self.multicast_group_list[i])

        # Send a Messages.Begin message if this is process 0, to signal that other processes can proceed to execute initialize
        if self.this_host_index == 0:
            self.send_begin()
        else:
            self.wait_for_begin()
            print("Received Begin")
        
        # Priority Queue for managing requests
        self.request_queue = queue.PriorityQueue() # items will be (self.vc) since VCs are comparable and also hold ID!

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
        sock.bind(('', quorum_multicast_group[1])) # Just bind to localhost and a random port number!

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(quorum_multicast_group[0])
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.listeners.append(sock)

    def send_begin(self):
        print("Sending Begin signal")

        for host_and_port in self.multicast_group_list:
            # Protect vector clock increment via lock
            if host_and_port != self.multicast_group_list:
                self.msock.sendto(structure_message(self.this_host_index, self.vector_clock, 3), host_and_port)
            # sleep(.2)

    def wait_for_begin(self):
        print("Waiting for Begin signal.")
        ready = False
        while True:
        # select readable socket
            r, _, err = select.select(self.listeners, [], self.listeners, 0.1)
            
            
            for sock in r:
                
                sender_hostid, message_enum, sender_vector_clock, sender_address = self._process_message(sock)
                if int(message_enum) == int(Messages.Begin):
                    ready = True
            if ready == True:
                break



    def send_reply_to_host(self, recipient_address_and_port):
        # print(f"Sending reply to {recipient_address_and_port}")
        # Protect vector clock increment via lock
        with self.vc_lock:
            self.vector_clock.inc()

            self.msock.sendto(structure_message(self.this_host_index, self.vector_clock, int(Messages.Reply)), recipient_address_and_port)

    def send_request_to_quorum(self):
        # Protect vector clock increment via lock
        with self.vc_lock:
            self.vector_clock.inc()

            # Multicast needs to be sent over a port which all nodes in the quorum will be listening on (bound to)
            self.msock.sendto(structure_message(self.this_host_index, self.vector_clock, int(Messages.Request)), self.target_multicast_group)

    def send_release_to_quorum(self):
        # Protect vector clock increment via lock
        with self.vc_lock:
            self.vector_clock.inc()

            # Multicast needs to be sent over a port which all nodes in the quorum will be listening on (bound to)
            self.msock.sendto(structure_message(self.this_host_index, self.vector_clock, int(Messages.Release)), self.target_multicast_group)


    #   MLockMutex() initiates a BLOCKING request for the critical section.
    #
    #   Returns: value on obtaining lock.
    def MLockMutex(self):
        # print(f"Process {self.this_process_host_id} accessing CS with vector clock: {self.vector_clock.timestamp}")
        print(f"{self.entire_host_id_list[self.this_host_index]},{self.this_host_index}:{self.vector_clock.timestamp}")
        sleep(self.access_duration)# ^^^^ Should this be 10?


    #   MReleaseMutex() exits the critical section once it is obtained
    def MReleaseMutex(self):
        # Pop from queue and reset votes
        self.request_queue.get()

        self.votes = 0
        self.voted = False
        self.send_release_to_quorum()
        if not self.request_queue.empty():
            self.voted = True
            # We must send our reply to the next person in the queue. This could be a vote for itself.
            next_host = self.request_queue.get()
            self.request_queue.put((next_host[0], next_host[1]))
            self.send_reply_to_host(self.entire_host_id_list[next_host[1]])

    

    # This function checks if the cs is accesssible yet
    def _cs_accessible(self):
        accessible = False
        if (self.voted == True) and (self.votes >= self.majority_quorum_votes):
            accessible = True
        return accessible
    
    # This function is called when an access is requested. It blocks until it can access cs
    def _MRequest(self, timeout):
        self.request_queue.put((self.vector_clock, self.this_host_index))
        self.votes = 1                  # TODO This line may conflict with the case where this process reply's to itself after receiving a release message
        self.voted = True
        self.send_request_to_quorum()
        timeout_time = time.perf_counter() + timeout
        while time.perf_counter() < timeout_time:
            if self._cs_accessible():
                self.MLockMutex()
                break
        self.MReleaseMutex()
        

    def _process_message(self, sock):
                new_message, host_address = sock.recvfrom(self.message_fixed_size)
                hostid, vector_clock, message_enum = parse_message(new_message)

                with self.vc_lock:
                    self.vector_clock.update(vector_clock)
    
                return hostid, message_enum, vector_clock, host_address


    def _message_handler(self, event):
        # This effectively executes the Maekawa state-machine
        # Likely we'll just pass in multicast send and send callbacks to Maekawa so it can send stuff in the proper case?
        while not event.is_set():

           

            # select readable socket
            r, _, err = select.select(self.listeners, [], self.listeners, 0.1)
            
            
            for sock in r:
                
                sender_hostid, message_enum, sender_vector_clock, sender_address = self._process_message(sock)


                match int(message_enum):
                    case int(Messages.Release):
                        self.voted = False
                        self.request_queue.get()
                        if self.request_queue.not_empty:
                            self.voted = True
                            # We must send our reply to the next person in the queue. This could be a vote for itself.
                            next_host = self.request_queue.get()
                            self.request_queue.put((next_host[0], next_host[1]))
                            self.send_reply_to_host(sender_address)

                    case int(Messages.Reply):
                        self.votes += 1
                    case int(Messages.Request):
                        self.request_queue.put((sender_vector_clock, sender_vector_clock._si))

                        if self.voted == False:
                            self.voted == True
                            self.send_reply_to_host(sender_address)
                    case _:
                        # print(f"Message does not match expected messages: {message_enum}.")
                        pass



            if event.is_set():
                break
        print("Keyboard Interrupt... Exiting thread ", threading.current_thread().name)
    
    # this function packs messages and incrememnts the vecotr clock
    def send_message():
        pass

    def run(self, number_of_cs_requests = 10, number_of_runs = 1, event=None):

        # The access frequency and duration will simulate computer needing to randomly access some cs. 
        # Since we'll be a using a print as the cs, We wil also have the computers wait for some time 
        # while inside to test the request while process is holding mechanism.

        # Put these somewhere better
        self.access_frequency = uniform(1, 3)  # [seconds] how often guard will be called
        self.access_duration = uniform(.0001, .001)  # [seconds] how long lock will be held once inside guard

        # Run maekawas algorithm this many times
        for run in range(number_of_runs):

            self.MInitialize()  # Initialize the maekawa algorithm

            t1 = threading.Thread(target=self._message_handler, args=(event,))
            t1.daemon = True
            t1.start()

            for requests in range(number_of_cs_requests):
                sleep(self.access_frequency)
                self._MRequest(.1)
            # print("Good Night Moon 🌜")
            while True:
                pass
            self.MCleanup()  # clean up the maekawa algorithm, next_host.host_id)