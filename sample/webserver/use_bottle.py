import gevent
from gevent import monkey
gevent.monkey.patch_all()

import bottle
from bottle import route, run, template
import pymongo
import json
import time 


@route('')
def index():
    return '<b>Hello world!</b>\n'
    
@route('/echo/<name>')
def echo(name):
    #print ("name=", name)
    return template('<b>echo: command= {{name}}</b>!', name=name)


@route('/read')
def read():
    mc = pymongo.MongoClient(host="localhost",port=27017)
    db = mc["stress_test"]
    col= db["test1"]
    r = col.find_one({"a":"test"})
    x=0
    for i in xrange(1000):
        x+=1
    #time.sleep(0.5)
    return str(r["b"]) + "\n"

@route('/write')
def write():
    mc = pymongo.MongoClient(host="localhost",port=27017)
    db = mc["stress_test"]
    col= db["test1"]
    col.update({"a":"test" } ,  {"$inc":{"b":1} } , upsert=True )
    return 'write ok'


#run(host='http://darktech.no-ip.biz', port=8080)
run(host='localhost', server= 'gevent', port=8080, quiet=True)
#run(host='localhost', server= 'wsgiref', port=8080, quiet=True)



'''
def run(app=None, server='wsgiref', host='127.0.0.1', port=8080,
        interval=1, reloader=False, quiet=False, plugins=None,
        debug=None, **kargs):
    """ Start a server instance. This method blocks until the server terminates.

        :param app: WSGI application or target string supported by
               :func:`load_app`. (default: :func:`default_app`)
        :param server: Server adapter to use. See :data:`server_names` keys
               for valid names or pass a :class:`ServerAdapter` subclass.
               (default: `wsgiref`)
        :param host: Server address to bind to. Pass ``0.0.0.0`` to listens on
               all interfaces including the external one. (default: 127.0.0.1)
        :param port: Server port to bind to. Values below 1024 require root
               privileges. (default: 8080)
        :param reloader: Start auto-reloading server? (default: False)
        :param interval: Auto-reloader interval in seconds (default: 1)
        :param quiet: Suppress output to stdout and stderr? (default: False)
        :param options: Options passed to the server adapter.

server_names = {
    'cgi': CGIServer,
    'flup': FlupFCGIServer,
    'wsgiref': WSGIRefServer,
    'waitress': WaitressServer,
    'cherrypy': CherryPyServer,
    'paste': PasteServer,
    'fapws3': FapwsServer,
    'tornado': TornadoServer,
    'gae': AppEngineServer,
    'twisted': TwistedServer,
    'diesel': DieselServer,
    'meinheld': MeinheldServer,
    'gunicorn': GunicornServer,
    'eventlet': EventletServer,
    'gevent': GeventServer,
    'geventSocketIO':GeventSocketIOServer,
    'rocket': RocketServer,
    'bjoern' : BjoernServer,
    'auto': AutoServer,
}

'''
