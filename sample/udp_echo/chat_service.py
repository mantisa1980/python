# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'
import socket
import sys
from chat_interface import IConnectionEvent, IMessageEvent




class ChatService(IConnectionEvent, IMessageEvent):
    def __init__(self):
        pass
    
    def on_connect(self, client):
        print "ChatService: on_connect", client 

    def on_disconnect(self, client):
        print "ChatService: on_disconnect", client

    def on_message(self, message):
        print "[ChatService] on_message:", message
        return "echo by chat service:" + message





if __name__ == "__main__":
    svr = ChatService()

