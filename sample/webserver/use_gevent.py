import gevent
from gevent import monkey
gevent.monkey.patch_all()
from gevent import pywsgi
import pymongo
import json
import time 

#mode = 0 

def hello_world(environ, start_response):
    print "hello begin"
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield '<b>Hello world!</b>\n'
    print "hello end"

def read(environ, start_response):
    #mode +=1 
    #print "read begin"
    mc = pymongo.MongoClient(host="localhost",port=27017)
    db = mc["stress_test"]
    col= db["test1"]
    r = col.find_one({"a":"test"})
    x=0
    for i in xrange(1000):
        x+=1
    #time.sleep(0.5)
    #print "read end"
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield str(r["b"]) + "\n"

def write(environ, start_response):
    x=0
    for i in xrange(1000):
        x+=1
    mc = pymongo.MongoClient(host="localhost",port=27017)
    db = mc["stress_test"]
    col= db["test1"]
    col.update({"a":"test" } ,  {"$inc":{"b":1} } , upsert=True )

    start_response('200 OK', [('Content-Type', 'text/html')])
    yield 'write ok'

server = pywsgi.WSGIServer(
    listener=('', 8080), application=write, log=None)

server.serve_forever()