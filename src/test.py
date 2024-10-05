import sys, struct, socket, time, threading



def structure_message(hostid, vector_clock, message_enum):
    return str(hostid).encode('utf-8') + vector_clock.tobytes + str(message_enum).encode('utf-8') # Maybe we should actually use a struct for packing/unpacking???

def parse_message(bmessage):
    hostid = int(unpack_message(bmessage[0:1])) # first byte
    vector_clock = VectorClock.frombytes(hostid, bmessage[1:-1]) # middle bytes are vector clock timestamp converted to bytes
    message_enum = int(unpack_message(bmessage[-1:])) # final byte
    return hostid, vector_clock, message_enum

def unpack_message(bmessage):
    return bmessage.decode('utf-8')




# Multicast funcs
#################
def send(message, mcast_group):
    # multicast group and port
    multicast_group = mcast_group

    # Create sender socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Need to ensure all sockets are "reuse address" since we connect to same address with multiple sockets
    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1)
    sock.settimeout(0.2)

    # This specifies how many "hops" across the network the multicasted message will travel
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))


    try:
        print(f"Sending '{message}'...")
        sent = sock.sendto(message, multicast_group)
        print(f"Successfully sent {sent} bytes.")
    finally:
        print('closing socket')
        sock.close()



if __name__=="__main__":

    # IP_MULTICAST_GROUP_PREFIX = (
    # "224.0.2.1, 9001",
    # "224.0.2.1, 900"
# )  # Prefix for Ad-Hoc multicast group. Each quorum will have one of this and its suffix will just be id number
    
    args = sys.argv

    from mutual_exclusion.IDistributedMutex import *
    from mutual_exclusion.vectorclock import VectorClock

    mock_vector_clock = VectorClock(sys.argv[1],4)
    # mock_vector_clock.
    send(structure_message(sys.argv[1],mock_vector_clock,int(Messages.Reply)), (sys.argv[2], int(sys.argv[3])))

    # if len(args) < 2:
    #     raise ValueError("You must specify at least one argument")

    # if args[1]=="RECV":
    #     begin_receiving()

    # elif args[1]=="REPLY":
    #     msg = ' '.join(sys.argv[2:]).encode()
    #     send(msg)

    # else:
    #     print("bruh... RECV or SEND......... which is it? Try again bitch.")