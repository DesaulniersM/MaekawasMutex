# Sourced from: https://pymotw.com/2/socket/multicast.html
# Mild edits, plus we'll want these to be non-blocking since we're using select

import socket
import struct
import sys


# MSG MANIPULATION
######################
def pack_msg(msg_str):
    return msg_str.encode('utf-8')

def unpack_msg(msg_bytes):
    return msg_bytes.decode('utf-8')

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

def begin_receiving():
    # receiver
    multicast_group = '224.3.29.71'
    server_address = ('', 10000) # PORT MUST MATCH THE PORT OVER WHICH THE MULTICAST IS BEING SENT!!!

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1)

    # RH: Not sure we actually need this bind here?    
    # Bind to the server address
    sock.bind(server_address)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receive/respond loop
    while True:
        print('Waiting to receive messages...')
        data, address = sock.recvfrom(1024)
        
        print(f"received {len(data)} bytes from {address}")
        print(data)

        print('sending acknowledgement to', address)
        sock.sendto(b'ack', address)



if __name__=="__main__":

    # IP_MULTICAST_GROUP_PREFIX = (
    # "224.0.2.1, 9001",
    # "224.0.2.1, 900"
# )  # Prefix for Ad-Hoc multicast group. Each quorum will have one of this and its suffix will just be id number
    
    args = sys.argv

    def structure_message(hostid, vector_clock, message_enum):
        return str(hostid).encode('utf-8') + vector_clock.tobytes + str(message_enum).encode('utf-8') # Maybe we should actually use a struct for packing/unpacking???

    from ..mutual_exclusion.vectorclock import VectorClock

    send(structure_message(sys.argv[1],VectorClock(sys.argv[1],4),Messages.Reply), (sys.argv[2], sys.argv[3]))

    # if len(args) < 2:
    #     raise ValueError("You must specify at least one argument")

    # if args[1]=="RECV":
    #     begin_receiving()

    # elif args[1]=="REPLY":
    #     msg = ' '.join(sys.argv[2:]).encode()
    #     send(msg)

    # else:
    #     print("bruh... RECV or SEND......... which is it? Try again bitch.")