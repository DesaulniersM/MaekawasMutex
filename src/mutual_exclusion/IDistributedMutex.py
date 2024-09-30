class CDistributedMutex:
    def __init__(self) -> None:
        self.entire_host_id_list = []  # List of Global hosts that subsets are made from
        self.this_node_host_id = ()  # host id for this instance of CDistributedMutex

        self.voting_group_hosts = (
            []
        )  # Set representing the subset of hosts this node will make requests to.
        self.current_vector_clock = []  # Current vector clock view of subset

        self.locked = False  # This flag is set when any node is known to have the lock

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
        # We now have length of voting groups and may create a vector clock
        self.current_vector_clock = [0] * len(voting_group_hosts)

    #   MLockMutex() initiates a BLOCKING request for the critical section.
    #
    #   Returns: value on obtaining lock.
    def MLockMutex(self):
        # self.
        print(self.current_vector_clock)
        pass

    #   MReleaseMutex() exits the critical section once it is obtained
    def MReleaseMutex(self):
        # Pop from
        pass

    def MCleanup(self):
        self.voting_group_hosts = (
            []
        )  # Set representing the subset of hosts this node will make requests to.
        self.current_vector_clock = []  # Current vector clock view of subset
