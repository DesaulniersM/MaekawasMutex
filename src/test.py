
import sys, struct, socket

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

    send(structure_message(sys.argv[1],VectorClock(sys.argv[1],4),int(Messages.Reply)), (sys.argv[2], int(sys.argv[3])))

    # if len(args) < 2:
    #     raise ValueError("You must specify at least one argument")

    # if args[1]=="RECV":
    #     begin_receiving()

    # elif args[1]=="REPLY":
    #     msg = ' '.join(sys.argv[2:]).encode()
    #     send(msg)

    # else:
    #     print("bruh... RECV or SEND......... which is it? Try again bitch.")