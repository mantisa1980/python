# -*- coding: utf-8 -*-

import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.gevent import GeventScheduler
import apscheduler.events
import time
import random
import hashlib
import ujson
import requests
import gevent
import logging

logging.basicConfig()

class MyScheduler(object):
    def __init__(self):
        self.scheduler = GeventScheduler()
        self.scheduler.add_listener(self.event_callback, apscheduler.events.EVENT_JOB_MAX_INSTANCES)
        self.scheduler.add_job(self.update1, trigger='interval', seconds=0.5)
        # self.scheduler.add_job(self.make_matches, trigger='interval', seconds=13)
        self.scheduler.add_job(self.update2, trigger='interval', seconds=1)

    def run(self):
        self.scheduler.start()

    def update1(self):
        '''
        counter = 0
        while True:
            counter+=1
            if counter % 10000000 == 0:
                print("Update1")
                gevent.sleep(0.1)
        '''

        gevent.sleep(0.4)

    def update2(self):
        print("Update2")
        pass

    def event_callback(self, event):
        print("Event:", event)


if __name__ == "__main__":
    sc = MyScheduler()
    sc.run()
    while True:
        gevent.sleep(1)

