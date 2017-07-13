# -*- coding: utf-8 -*-
import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('127.0.0.1', 8888)
message = 'This is the message.  It will be repeated.'

try:

    # Send data
    print >>sys.stderr, 'sending "%s"' % message
    sent = sock.sendto(message, server_address)
    sent = sock.sendto(message +"2", server_address)


    # Receive response
    print >>sys.stderr, 'waiting to receive'
    data, server = sock.recvfrom(1024)
    print >>sys.stderr, 'received "%s"' % data
    data, server = sock.recvfrom(1024)
    print >>sys.stderr, 'received "%s"' % data

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
