import gevent
from gevent import monkey
gevent.monkey.patch_all()
from gevent import pywsgi
import pymongo
import json
import time 

global counter
counter = 0

print "init ...", counter



#mode = 0 
def application(env, start_response):
    global counter

    #print counter
    #if counter !=0 : print "before : !=0"
    
    #counter+=1

    #print "begin read"
    read()
    #counter-=1
    #if counter !=0 : print "after : !=0"
    #print "finish read"
    start_response('200 OK', [('Content-Type','text/html')])
    return ["Hello World"]


def read():
    #mode +=1 
    #print "read begin"
    mc = pymongo.MongoClient(host="localhost",port=27017)
    db = mc["stress_test"]
    col= db["test1"]
    r = col.find_one({"a":"test"})
    x=0
    for i in xrange(1000):
        x+=1

def write():
    x=0
    for i in xrange(1000):
        x+=1
    mc = pymongo.MongoClient(host="localhost",port=27017)
    db = mc["stress_test"]
    col= db["test1"]
    col.update({"a":"test" } ,  {"$inc":{"b":1} } , upsert=True )

write()