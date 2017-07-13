# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'

'''
IChatClient only handles data at packet level. It is not message-aware.
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

class IChatServer(IConnectionEvent, IPacketEvent):
    def get_clients(self):
        raise Exception("IChatServer interface not implemented!")

    def subscribe_connection_event(self, IConnectionEvent_impl):
        raise Exception("IChatServer interface not implemented!")
    
    def bind_message_handler(self, sys_type, IMessageEvent_impl):
        raise Exception("IChatServer interface not implemented!")
