# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'
import socket
import sys
import traceback
from chat_interface import IChatClient

class IChatClient(object):
    def send(self):
        raise Exception("IChatClient interface not implemented")

    def close(self):
        raise Exception("IChatClient interface not implemented")

    def bind_packet_handler(self, IPacketEvent_impl):
        raise Exception("IChatClient interface not implemented")

    def bind_connection_event_handler(self, IConnectionEvent_impl):
        raise Exception("IChatClient interface not implemented")
        pass

    def get_id(self):
        raise Exception("IChatClient interface not implemented")

class TCPChatClient(IChatClient):
    def __init__(self, sock, address):
        self.is_connected = True
        self.sock = sock
        self.id = ":".join(str(x) for x in address)
        self.packet_handler = None
        self.conn_event_handler = None

    def send(self, data):
        self.sock.sendall(data)
    
    def close(self):
        self.is_connected = False
        self.sock.close()
        self.conn_event_handler.on_disconnect(self)
    
    def bind_packet_handler(self, IPacketEvent_impl):
        self.packet_handler = IPacketEvent_impl

    def bind_connection_event_handler(self, IConnectionEvent_impl):
        self.conn_event_handler = IConnectionEvent_impl

    def get_id(self):
        return self.id

    def update(self):
        try:
            while self.is_connected:
                data = self.sock.recv(16) #!!
                if data:
                    print 'received "%s"' % data
                    response = self.packet_handler.on_packet(data)
                    if response:
                        self.send(data)
                else:
                    print 'no more data from', self.get_id()
                    break
        except:
            print "[TCPChatClient]update error!", traceback.format_exc()

        finally:
            self.close()
