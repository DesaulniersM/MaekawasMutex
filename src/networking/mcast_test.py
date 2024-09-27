# Sourced from: https://pymotw.com/2/socket/multicast.html
# Mild edits, plus we'll want these to be non-blocking since we're using select

import socket
import struct
import sys

def send(message):
    # multicast group and port
    multicast_group = ('224.3.29.71', 10000)

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

        # Handle acks. This closes immediately upon receiving all acks
        while True:
            print('waiting to receive')
            try:
                data, server = sock.recvfrom(16) # just receives acks, that's all
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print(f"received {data} from {server}")

    finally:
        print('closing socket')
        sock.close()

def begin_receiving():
    # receiver
    multicast_group = '224.3.29.71'
    server_address = ('', 10000)

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
    args = sys.argv

    if len(args) < 2:
        raise ValueError("You must specify at least one argument")

    if args[1]=="RECV":
        begin_receiving()

    elif args[1]=="SEND":
        msg = ' '.join(sys.argv[2:]).encode()
        send(msg)

    else:
        print("bruh... RECV or SEND......... which is it? Try again bitch.")