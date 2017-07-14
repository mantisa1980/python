# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'

'''
IChatClient only handles data at packet level. It is not message-aware.
'''
from chat_interface import IPacketParser


class JSONPacketParser(IPacketParser):
    def feed(self, data):
        pass
    
    def next(self):
        pass

class ProtoBufPacketParser(IPacketParser):
    def feed(self, data):
        pass
    
    def next(self):
        pass

class GRPCPacketParser(IPacketParser):
    def feed(self, data):
        pass
    
    def next(self):
        pass

