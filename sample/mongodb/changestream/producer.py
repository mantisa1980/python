__author__ = 'duyhsieh'
# -*- coding: utf-8 -*-
import time
import datetime
import pymongo
import traceback


mc = pymongo.MongoClient('mongo', socketTimeoutMS=1000, connectTimeoutMS=1000, waitQueueTimeoutMS=4000)
db = mc['AAA']
col = db['BBB']

def insert():
    counter = 0
    while True:
        try:
            col.insert({'counter':counter})
            counter+=1
        except:
            print "Error------", traceback.format_exc()
            break
        else:
            time.sleep(5)


def batch_insert():
    counter = 0
    while True:
        try:
            data = [{'counter':i } for i in xrange(counter, counter + 10000)]
            counter += len(data)
            col.insert(data)
            
        except:
            print "Error------", traceback.format_exc()
            break
        else:
            time.sleep(10)

def update():
    counter = 0
    while True:
        try:
            print "updating counter=", counter
            col.find_and_modify({},{'$set':{'counter':counter}} ,upsert=True)
            counter+=1
        except:
            print "Error------", traceback.format_exc()
            break
        else:
            time.sleep(5)

if __name__ == '__main__':
    #insert()
    #update()
    batch_insert()