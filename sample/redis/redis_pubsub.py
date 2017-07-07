import gevent
from gevent import monkey; monkey.patch_all()
import redis
import time

def run(num, redis_cli):
    pubsub = redis_cli.pubsub()
    pubsub.subscribe(['channel1', 'channel2'])
    print num, "loop enter"
    for item in pubsub.listen():
        if item['data'] == 'kill':
            print '< -thread', num, ' kill'
            break
        elif item['data'] == 'cancel1':
            print '< -thread', num, ' cancel 1'
            pubsub.unsubscribe('channel1')
        elif item['data'] == 'cancel_all':
            print '<- thread', num, ' cancel all'
            pubsub.unsubscribe()
        
        else:
            print '<- thread', num, 'receive:', item['channel'], ':', item['data'] 
    print "thread ", num , "done"
  
if __name__ == '__main__':
    r = redis.Redis()
    t1 = gevent.spawn(run,'t1', r)
    t2 = gevent.spawn(run,'t2', r)
    gevent.sleep(1) # wait for coroutines to finish subscribing
    print '-> main thread sending chan 1', '1234'
    r.publish('channel1', '1234')
    print '-> main thread sending chan 2', 'abcd'
    r.publish('channel2', 'abcd')
    print '-> main thread sending chan x'
    r.publish('channelx', 'this will not reach')
    print '-> main thread sending cancel1 to chan1'
    r.publish('channel1', 'cancel1')
    gevent.sleep(1)
    print '-> main thread sending data to chan2', 5678
    r.publish('channel2', 5678) 
    gevent.sleep(1)
    print '-> main thread sending cancel all'
    r.publish('channel2', 'cancel_all')
    gevent.sleep(1)
    print '-> main thread sending kill to chan1'
    r.publish('channel1', 'kill') # useless, unsubscribe falseify the loop
    t1.join()
    t2.join()
    print 'main thread done'
