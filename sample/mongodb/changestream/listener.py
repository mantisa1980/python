# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'
import time
import datetime
import pymongo
import os
import pymongo
import traceback
from bson.json_util import dumps, loads
import time

resume_token = None
resume_token = {u'_data': u'825CE3C3F40000271029295A1004E03BDC13A5A34F7E91C35DD0DC33F2C646645F696400645CE3C3F4475BFB3E8C4A835F0004'} # resume after this document (not included)
# 一次watch會從resume token之後輸出一次; 重新執行就重新輸出
#resume_token = object('825CE39CAF0000000129295A1004EB94468B741947E5A10B8ADCEBEB773E46645F696400645CE39CAF475BFB2117E338BF0004')
# database / collection不需要先存在
# resume目前追朔到14萬筆都可以resume

counter = 0
def main():
    global resume_token
    #mc = pymongo.MongoClient('mongo', socketTimeoutMS=1000, connectTimeoutMS=1000, waitQueueTimeoutMS=4000)
    mc = pymongo.MongoClient('mongo', socketTimeoutMS=1000, connectTimeoutMS=1000, waitQueueTimeoutMS=4000, username='igs', password='igs', authSource='AAA',authMechanism='SCRAM-SHA-1')
    db = mc['AAA']
    col = db['BBB']
    print col.insert({'aaa':'bbb'})
    while True:
        counter = 0
        try:
            for change in col.watch(resume_after=resume_token):
                #print change
                counter +=1 
                pass

                if counter % 1000 == 0:
                    print "counter=", counter

                
                #if resume_token == None:
                #    resume_token = change["_id"]
                #    print "setting resume token", change["_id"]
                #print('') # for readability only
        except:
            print "Error!!!", traceback.format_exc()
        finally:
            time.sleep(1)
            #raw_input('----')


if __name__ == '__main__':
    main()