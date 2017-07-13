# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'

import gevent
from gevent import monkey; monkey.patch_all()
import socket
import sys
import traceback
from gevent import Greenlet
from gevent import socket
from gevent import sleep
from gevent.lock import BoundedSemaphore
from chat_client import TCPChatClient
from chat_service import ChatService
from chat_interface import IChatServer
import socket
import sys

'''
TODO: get socket address, or makeup something that can denote the uniqueness of each socket
make a socket keeper list <key,socket> so to add/remove them on connect/disconnect

'''



'''
Design Philosophy

In charge of creating connecton objects and bypassing client message to system services.
Who extracts message types ? Who cuts streaming data to packets? TCPXXX should take care of streaming ... TCPClient
Service sees no client, client sees no service. Use Server as intermediate proxy ... and service rely on server interface, server reply on event registration, decouple with services
clinet should also reply on callback to ineract with server 

we want message handling to be per-client-concurrent, so for udp clients server receive messages but forward to udp clinet message queue and let them handle it.
for tcp clients each receiving data coroutine handles message within itself, by calling back tcp server's packet handler, 
which then parses message systype and callbacks target service handlers, and return reponse data.
'''

'''
class IConnectionEvent(object): # implemented by server or any interested services
    def on_connect(self, chat_client):
        raise Exception("IConnectionEvent interface not implemented!")    

    def on_disconnect(self, chat_client):
        raise Exception("IConnectionEvent interface not implemented!")    

class IPacketEvent(object): # implemented by server
    def on_packet(self, packet):
        pass

class IMessageEvent(object): # implemented by services
    def on_message(self, message):
        raise Exception("IMessageEvent interface not implemented!")    

'''

class BaseChatServer(IChatServer):
    def __init__(self):
        self.clients = dict()
        self.connection_event_listeners = list() # multiple listeners
        self.message_handlers = dict() # only one handler for each sys_type

    def get_clients(self):
       return self.clients

    def subscribe_connection_event(self, IConnectionEvent_impl):
        if getattr(IConnectionEvent_impl, 'on_connect', None) is None or getattr(IConnectionEvent_impl, 'on_disconnect', None) is None:
            raise Exception("IConnectionEvent interface not implemented by {}".format(IConnectionEvent_impl))
        self.connection_event_listeners.append(IConnectionEvent_impl)
    
    def bind_message_handler(self, sys_type, IMessageEvent_impl):
        if getattr(IMessageEvent_impl, 'on_message', None) is None:
            raise Exception("IMessageEvent interface not implemented by {}".format(IMessageEvent_impl))
        if sys_type in self.message_handlers:
            raise Exception("sys type {} already registered by {}!".format(sys_type, IMessageEvent_impl))
        self.message_handlers[sys_type] = IMessageEvent_impl

    # implement IConnectionEvent
    def on_connect(self, client):
        k = client.get_id()
        if k in self.clients:
            print "[BaseChatServer]error!socket already exist!{}".foramt(k)
            pass
        
        print "[BaseChatServer]on_connect impl:", client.get_id(), " client cnt:", len(self.clients)
        self.clients[k] = client
    
    # implement IConnectionEvent
    def on_disconnect(self, client):
        self.clients.pop(client.get_id(),None)
        print "[BaseChatServer]on_disconnect impl:", client.get_id(), " client cnt:", len(self.clients)
        pass

    def on_packet(self, packet):
        sys_type = 'chat' #!! should be parsed from packet later.
        r = self.message_handlers[sys_type].on_message(packet)
        return r

class TCPChatServer(BaseChatServer):
    def run(self, bind_ip, bind_port):
        server_address = (bind_ip, bind_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(1)

        try:
            while 1:
                # wait for a connection
                print 'waiting for a connection'
                connection, client_address = sock.accept()
                print 'connection from', client_address, connection.getsockname(), connection.getpeername(), type(connection.getpeername())
                chat_client = TCPChatClient(connection, client_address)
                chat_client.bind_packet_handler(self)
                chat_client.bind_connection_event_handler(self)
                self.on_connect(chat_client) # for tcp server , on_connect this is invoked by itself
                gevent.spawn(chat_client.update)

        except:
            print "tcpchatserver loop exception ", traceback.format_exc()
        
        finally:
            sock.close()

class UDPChatServer(BaseChatServer):
    def run(self, bind_ip, bind_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind_ip, bind_port,))

        try:
            while 1:
                print 'waiting to receive message'
                data, address = sock.recvfrom(4096)
                        
                print 'received %s bytes from %s:data=%s' % (len(data), address), data
                                    
                if data:
                    sent = sock.sendto(data, address)
                    print 'sent %s bytes back to %s' % (sent, address)

        except:
            print "tcpchatserver loop exception ", traceback.format_exc()
        
        finally:
            sock.close()


if __name__ == "__main__":
    srv = TCPChatServer()
    chat_service = ChatService()
    srv.subscribe_connection_event(chat_service)
    srv.bind_message_handler('chat', chat_service)

    srv.run('127.0.0.1', 8888)

