from mutual_exclusion.vectorclock import VectorClock
from time import sleep
from random import uniform
import threading
from enum import Enum


import queue

# Three types of messages that can be sent by a node
class Messages(Enum):
    Request = 0         # Request to enter CS. Sent to subset quorum members
    Reply = 1           # Reply to Request. This will ALWAYS be a "You may enter CS" reply.
    Release = 2         # Release message communicates that the CS is exited and quorum members may reply to next queue members



def structure_message(hostid, vector_clock, message_enum):
    return str(hostid).encode('utf-8') + vector_clock.tobytes() + str(message_enum).encode('utf-8') # Maybe we should actually use a struct for packing/unpacking???

def parse_message(bmessage):
    hostid = unpack_message(bmessage[0]) # first byte
    vector_clock = VectorClock.frombytes(hostid, bmessage[1:-1]) # middle bytes are vector clock timestamp converted to bytes
    message_enum = unpack_message(bmessage[-1]) # final byte
    return hostid, vector_clock, message_enum

def unpack_message(bmessage):
    return bmessage.decode('utf-8')

class CDistributedMutex:
    def __init__(self) -> None:
        self.voting_group_hosts = (
            []
        )  # Set representing the subset of hosts this node will make requests to.

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
        self.this_process_host_id = hosts[this_host]
        self.current_vector_clock = VectorClock(
            self_index=this_host, num_peers=len(hosts)
        )  # Current vector clock view of subset

        # MESSAGE LEN IS ALWAYS 2 bytes + vector clock size: 1 byte node id (0-255), 8 byte (0,2**64-1) x N-element vector clock, 1 byte enum
        self.message_fixed_size = 2 + 8*len(hosts)

        self.majority_quorum_votes = len(hosts) #


    #   QuitAndCleanup() will be called once when you are done testing your code.
    def QuitAndCleanup(self):
        # Close threads
        pass

    #   MInitialize() will be called once when starting to test Maekawa’s. May be recalled multiple
    # times, as long as the corresponding cleanup algorithm, MCleanup(), is done after each
    # initialization. The votingGroupHosts array contains an index (to the hosts array) for each
    # host in the voting set/group of the current host.
    #   Input: voting_group_hosts : array of host ids in the set of the current host
    def MInitialize(self, voting_group_hosts):
        self.voting_group_hosts = [
            self.entire_host_id_list[host] for host in voting_group_hosts
        ]
        self.votes = 0      #Number of votes in favor of this node accessing CS
        self.voted = False  # If this variable is true, This node has not sent/received a Release message it is waiting on

        # Priority Queue for managing requests
        self.request_queue = queue.PriorityQueue() # items will be (self.vc) since VCs are comparable and also hold ID!

        

    #   MLockMutex() initiates a BLOCKING request for the critical section.
    #
    #   Returns: value on obtaining lock.
    def MLockMutex(self):
        print(f"Process {self.this_process_host_id} accessing CS with vector clock: {self.current_vector_clock.timestamp}")
        sleep(self.access_duration)# ^^^^ Should this be 10?


    #   MReleaseMutex() exits the critical section once it is obtained
    def MReleaseMutex(self):
        # Pop from queue and reset votes
        self.request_queue.get()
        self.votes = 0
        self.voted = False
        self.send_release_to_quorum() #TODO
        if not self.request_queue.empty():
            self.voted = True
            # We must send our reply to the next person in the queue. This could be a vote for itself.
            next_host = self.request_queue.get()
            self.request_queue.put((next_host, next_host.host_id))
            send_Reply_(next_host, enum) #TODO

    def MCleanup(self):
        self.voting_group_hosts = (
            []
        )  # Set representing the subset of hosts this node will make requests to.
        self.current_vector_clock = VectorClock(
            self_index=self.this_host, num_peers=len(self.hosts)
        )  # Current vector clock view of subset


    # This function checks if the cs is accesssible yet
    def _cs_accessible(self):
        accessible = False
        if self.voted == True and self.votes >= self.majority_quorum_votes:
            accessible = True
        return accessible
    

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

    # This function is called when an access is requested. It blocks until it can access cs
    def _MRequest(self):
        self.votes = 1
        self.voted = True
        self.send_request_to_quorum()
        while True:
            if self._cs_accessible():
                self.MLockMutex()
                self.MReleaseMutex()

    def _process_message(self, sock):
                new_message, host_address = sock.recvfrom(self.message_fixed_size)
                hostid, vector_clock, message_enum = unpack_message(new_message)

                with self.vc_lock:
                    self.current_vector_clock.update(vector_clock)
    
                return hostid, message_enum, vector_clock, host_address


    def _message_handler(self, event):
        # This effectively executes the Maekawa state-machine
        # Likely we'll just pass in multicast send and send callbacks to Maekawa so it can send stuff in the proper case?
        while not event.is_set():

           

            # select readable socket
            r, _, err = select.select(self.listeners, [], self.listeners, 0.1)
            
            
            for sock in r:
                
                sender_hostid, message_enum, sender_vector_clock, sender_address = self._process_message(sock)

                match message_enum:
                    case Messages.Release:
                        self.voted = False
                        self.request_queue.get()
                        if self.request_queue.not_empty():
                            self.voted = True
                            # We must send our reply to the next person in the queue. This could be a vote for itself.
                            next_host = self.request_queue.get()
                            self.request_queue.put((next_host, next_host.host_id))
                            send_Reply_(next_host, enum) #TODO
                    case Messages.Reply:
                        self.votes += 1
                    case Messages.Request:
                        self.request_queue.put(sender_vector_clock, sender_vector_clock.host_id)
                        if self.voted == False:
                            self.voted == True
                            send_reply(sender_address, msg) #TODO
                            self.request_queue.put(())



            if event.is_set():
                break
        print("Keyboard Interrupt... Exiting thread ", threading.current_thread().name)
    
    # this function packs messages and incrememnts the vecotr clock
    def send_message():
        pass

    def run(self, number_of_cs_requests = 2, number_of_runs = 1):

        # The access frequency and duration will simulate computer needing to randomly access some cs. 
        # Since we'll be a using a print as the cs, We wil also have the computers wait for some time 
        # while inside to test the request while process is holding mechanism.

        # Put these somewhere better
        self.access_frequency = uniform(1.5, 3.5)  # [seconds] how often guard will be called
        self.access_duration = uniform(.5, 1.5)  # [seconds] how long lock will be held once inside guard

        # Run maekawas algorithm this many times
        for run in range(number_of_runs):

            self.MInitialize()  # Initialize the maekawa algorithm

            t1 = threading.Thread(target=self._message_handler, args=(event,))
            t1.daemon = True
            t1.start()

            for requests in number_of_cs_requests:
                sleep(self.access_frequency)
                self._MRequest()

            self.MCleanup()  # clean up the maekawa algorithm