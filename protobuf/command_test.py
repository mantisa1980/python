# -*- coding: utf-8 -*-
'''
to compile:
protoc --python_out=./ pbcommand.command.proto
'''
from pbcommand import command_pb2
from pbcommand.command_pb2 import *
import time
import sys
import json

from google.protobuf import json_format
from google.protobuf import text_format

def parse_system(sys_wrapper):
    system = sys_wrapper.WhichOneof("sys")
    if system == 'game':
        parse_command(sys_wrapper.game)
    elif system == 'item':
        parse_command(sys_wrapper.item)
    else:
        print "unknown system", sys_wrapper.WhichOneof("sys")

def parse_command(cmd_wrapper):
    cmd = cmd_wrapper.WhichOneof("cmd")
    if cmd == 'hit':
        data = cmd_wrapper.hit
        print "hit handler:data=","data1=", data.data1.encode('utf-8'), "data2=", data.data2
        print "killinfo:"
        for i in data.kill:
            print i
        #print "hit handler:data=", data  # 0 will not be printed but the 0 field is right there.
    elif cmd == 'shoot':
        data = cmd_wrapper.shoot
        print "shoot handler:data=", data.data1, data.data2
    pass

def test_command():
    sys_wrapper = SystemWrapper()
    cmd_wrapper = GameSystem()

    cmd = Shoot()
    cmd.data1="shoot data"
    cmd.data2=23456789

    cmd2 = Hit()
    cmd2.data1=u"許功蓋"
    cmd2.data2=0
    
    obj = cmd2.kill.add() # add a new repeated field
    obj.fid = 1
    obj.win = 0

    obj = cmd2.kill.add()
    obj.fid = 2
    obj.win = 200

    #cmd_wrapper.shoot.CopyFrom(cmd)
    #cmd_wrapper.shoot.CopyFrom(cmd)

    
    
    ################### serialize
    cmd_wrapper.hit.CopyFrom(cmd2)
    sys_wrapper.game.CopyFrom(cmd_wrapper)
    s = sys_wrapper.SerializeToString()
    
    ################### deserialize
    sys_wrapper_svr = SystemWrapper()
    sys_wrapper_svr.ParseFromString(s)
    #print sys_wrapper_svr
    #print sys_wrapper_svr.gs.hit.data1, type(sys_wrapper_svr.gs.hit.data1)
    #print sys_wrapper_svr.game.hit.data1.encode('utf-8') , type(sys_wrapper_svr.game.hit.data1)
    
    parse_system(sys_wrapper)


def test_performance():
    import ujson as json
    #import json
    sys_wrapper = SystemWrapper()
    cmd_wrapper = GameSystem()

    cmd2 = Hit()
    cmd2.data1=u"許功蓋"
    cmd2.data2=0
    
    obj = cmd2.kill.add()
    obj.fid = 1
    obj.win = 0

    obj = cmd2.kill.add()
    obj.fid = 2
    obj.win = 200

    cmd_wrapper.hit.CopyFrom(cmd2)
    sys_wrapper.game.CopyFrom(cmd_wrapper)

    t = time.time()
    for _ in xrange(100000):
        s1 = sys_wrapper.SerializeToString()
        sys_wrapper_svr = SystemWrapper()
        deserialize = SystemWrapper().ParseFromString(s1)
    print time.time() - t

    t = time.time()
    
    for _ in xrange(100000):
        x = {"X":u"許功蓋", "Y":0, "A":[{"f":1, "w":0 }, {"f":2 ,"w":200} ]}
        s2 = json.dumps(x)
        y = json.loads(s2)
    print time.time()-t

    print "len of protocol buffer packet=", len(s1), ", len of json packet=", len(s2)

def test_json_conversion():
    sys_wrapper = SystemWrapper()
    cmd_wrapper = GameSystem()

    cmd2 = Hit()
    cmd2.data1=u"許功蓋"
    cmd2.data2=0
    
    obj = cmd2.kill.add() # add a new repeated field
    obj.fid = 1
    obj.win = 0

    obj = cmd2.kill.add()
    obj.fid = 2
    obj.win = 200

    
    cmd_wrapper.hit.CopyFrom(cmd2)
    sys_wrapper.game.CopyFrom(cmd_wrapper)

    json_str = json_format.MessageToJson(sys_wrapper)
    #json_dict = json.loads(json_str)

    sys_wrapper_buffer = SystemWrapper()
    print "from message to json:\n", json_str  # // note: key with value 0 will disappear ! Not recommended
    msg = json_format.Parse(json_str, sys_wrapper_buffer)
    print "from json to message:\n", msg,", kill[0].win=", msg.game.hit.kill[0].win
    

#test_command()
test_performance()
#test_json_conversion()
